from core.enums import Limits, Tuples
from core.validators import OneOfTwoValidator, hex_color_validator
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    Q,
    TextField,
    UniqueConstraint,
)
from django.db.models.functions import Length
from PIL import Image

CharField.register_lookup(Length)

User = get_user_model()


class Tag(Model):
    name = CharField(
        verbose_name="Тэг",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        validators=(OneOfTwoValidator(field="Название тэга"),),
        unique=True,
    )
    color = CharField(
        verbose_name="Цвет",
        max_length=7,
        unique=True,
        db_index=False,
    )
    slug = CharField(
        verbose_name="Слаг тэга",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} (цвет: {self.color})"

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = hex_color_validator(self.color)
        return super().clean()


class Ingredient(Model):
    name = CharField(
        verbose_name="Ингридиент",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    measurement_unit = CharField(
        verbose_name="Единицы измерения",
        max_length=24,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)
        constraints = (
            UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_for_ingredient",
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name="\n%(app_label)s_%(class)s_measurement_unit is empty\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Recipe(Model):
    name = CharField(
        verbose_name="Название блюда",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    author = ForeignKey(
        verbose_name="Автор рецепта",
        related_name="recipes",
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        verbose_name="Тег",
        related_name="recipes",
        to="Tag",
    )
    ingredients = ManyToManyField(
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
        to=Ingredient,
        through="recipes.AmountIngredient",
    )
    pub_date = DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        verbose_name="Изображение блюда",
        upload_to="recipe_images/",
    )
    text = TextField(
        verbose_name="Описание блюда",
        max_length=Limits.MAX_LEN_RECIPES_TEXTFIELD.value,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_COOKING_TIME.value,
                "Ваше блюдо уже готово!",
            ),
            MaxValueValidator(
                Limits.MAX_COOKING_TIME.value,
                "Очень долго ждать...",
            ),
        ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail(Tuples.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)


class AmountIngredient(Model):
    recipe = ForeignKey(
        verbose_name="В каких рецептах",
        related_name="ingredient",
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        verbose_name="Связанные ингредиенты",
        related_name="recipe",
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENTS,
                "Нужно хоть какое-то количество.",
            ),
            MaxValueValidator(
                Limits.MAX_AMOUNT_INGREDIENTS,
                "Слишком много!",
            ),
        ),
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Количество ингридиентов"
        ordering = ("recipe",)
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredients",
                ),
                name="\n%(app_label)s_%(class)s ingredient alredy added\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredients}"


class Favorites(Model):
    recipe = ForeignKey(
        verbose_name="Понравившиеся рецепты",
        related_name="in_favorites",
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name="Пользователь",
        related_name="favorites",
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is favorite alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Carts(Model):
    recipe = ForeignKey(
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name="Владелец списка",
        related_name="carts",
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is cart alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
