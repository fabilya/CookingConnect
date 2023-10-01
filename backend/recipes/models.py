from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        verbose_name='Название',
        db_index=True,
        max_length=200,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=20,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(
        verbose_name='Название',
        unique=True,
        db_index=True,
        max_length=200,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )
    color = ColorField(
        format='hex',
        default='#FF0000',
        verbose_name='Цвет',
        unique=True,
        max_length=7,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )
    slug = models.SlugField(
        verbose_name='Индентификатор',
        unique=True,
        max_length=200,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    image = models.ImageField(
        verbose_name='Фотография',
        upload_to='recipes/',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Название не корректное.',
        },
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Время приготовления не может быть меньше 1 минуты!',
            ),
            MaxValueValidator(
                limit_value=1000,
                message='Время приготовления не может быть больше 1000 минут!',
            ),
        ),
        error_messages={
            'blank': 'Обязательно для заполнения.',
            'invalid': 'Введите корректное колличество минут от 1 до 1000.',
        },
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Ingredient quantity model."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                limit_value=1, message='Ингредиентов не может быть меньше 1!'
            ),
            MaxValueValidator(
                limit_value=50000,
                message='Ингредиентов не может быть больше 50000!',
            ),
        ),
        error_messages={
            'blank': 'Это поле обязательно для заполнения.',
            'invalid': 'Введите корректное количество.',
        },
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}, {self.amount}'


class Favorite(models.Model):
    """Model favorite recipes."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='favorite_unique',
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Recipe model in a shopping cart."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='shopping_cart_unique',
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в корзину'