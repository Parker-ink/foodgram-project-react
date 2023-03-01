# Продуктовый помощник

Продуктовый помощник это социальная сеть, для любителей кулинарии. Пользователи могут создавать свои рецепты, добавлять понравившиеся рецепты в избранное, подписываться на любимых авторов. Так же пользователи могут добавить рецепт в список покупок и загрузить файл с общим получившимся списком, что им надо купить.

## Для использования сайта перейдите по ссылке http://158.160.22.77

Для доступа к админке 

http://158.160.22.77/admin

Логин: admin
Пароль admin2409

# Для локального запуска

Загрузите репозиторий 
```bash
git@github.com:Parker-ink/foodgram-project-react.git
```
Перейдите в папку /infra/
```bash
cd infra/
```
Заполните .env файлы. Например:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

Выполните команды
```bash
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py import_csv
```
перейдите http://localhost/

