# Generated by Django 3.2.15 on 2023-02-17 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientamount',
            name='Такой ингредиент уже есть',
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='Такой ингредиент есть'),
        ),
    ]
