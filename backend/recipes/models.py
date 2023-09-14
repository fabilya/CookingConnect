from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
    )
    text = models.TextField(
        help_text='Введите описание рецепта',
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть меньше 1 минуты'
        )],
        verbose_name='Время приготовления (в минутах)',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
    )
    color = ColorField(
        format="hex",
        unique=True,
        verbose_name='Цвет тега',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_unit_name',
            )
        ]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Количество ингредиентов не может быть меньше 1',
        )],
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique',
            )
        ]

