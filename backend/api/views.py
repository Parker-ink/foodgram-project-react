from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from .filters import IngredientSearchFilter, RecipesFilter
from .pagination import LimitPagePagination
from .permissions import AdminOrAuthor, AdminOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeForFollowersSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UsersSerializer)


class UsersViewSet(UserViewSet):
    """Всьюсет модели пользователя"""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny, )

    def subscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        if self.request.user == follower:
            return Response({'message': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.get_or_create(user=self.request.user,
                                              author=follower)
        serializer = FollowSerializer(follow[0])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        Follow.objects.filter(user=self.request.user,
                              author=follower).delete()
        return Response({'message': 'Вы успешно отписаны'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, serializer, id):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serializer, id)
        return self.subscribed(serializer, id)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, serializer):
        following = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = (AdminOrAuthor,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_or_del_object(self, model, pk, serializer, errors):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={'user': self.request.user.id, 'recipe': recipe.id}
        )
        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeForFollowersSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        objects = model.objects.filter(user=self.request.user, recipe=recipe)
        if not objects.exists():
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        errors = 'У вас нет данного рецепта в избранном'
        return self.add_or_del_object(Favorite, pk, FavoriteSerializer, errors)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        errors = 'У вас нет данного рецепта в списке покупок'
        return self.add_or_del_object(
            ShoppingCart, pk, ShoppingCartSerializer, errors
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_list = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values_list(
                'ingredients__name', 'ingredients__measurement_unit').annotate(
                    Sum('amount')).order_by()
        shopping_cart = 'Список покупок:\n'
        for name, measure, amount in ingredients_list:
            shopping_cart += (f'{name.capitalize()} {amount} {measure},\n')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        return response
