from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from .validators import (
    AmountIngredientFieldValidator,
    ColorFieldValidator,
    CookingTimeRecipeFieldValidator,)
from users.serializers import UserListSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    color = ColorFieldValidator()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов с указанием количества."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountAddSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления количества ингредиентов в рецепт."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = AmountIngredientFieldValidator()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeListShortSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра краткого рецепта"""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserListSerializer(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    ingredients = IngredientAmountSerializer(
        many=True, source='ingredient_amount', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return recipe.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return recipe.shoppingcart.filter(user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientAmountAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=True)
    cooking_time = CookingTimeRecipeFieldValidator()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError('Ингредиенты обязательны')

        tags_data = data.get('tags')
        if not tags_data:
            raise serializers.ValidationError('Теги обязательны')

        for ingredient_data in ingredients_data:
            amount = ingredient_data.get('amount')
            if int(amount) <= 0:
                raise serializers.ValidationError('Вес ингредиентов должен '
                                                  'быть больше нуля')

        cooking_time = data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError('Время готовки должно '
                                              'быть больше нуля')

        ingredient_ids = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').get('id')
            ingredient_ids.append(ingredient_id)
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не '
                                              'должны повторяться')

        tag_ids = set(tags_data)
        if len(tag_ids) != len(tags_data):
            raise serializers.ValidationError('Теги не должны '
                                              'повторяться')

        return data

    def set_ingredients(self, recipe, ingredients_data):
        ingredients = list()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').get('id')
            amount = ingredient_data.get('amount')
            recipe_ingredient = IngredientAmount(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount
            )
            ingredients.append(recipe_ingredient)
        IngredientAmount.objects.bulk_create(ingredients)

    @atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients_data)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        recipe = instance
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        IngredientAmount.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance=instance, context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteSerializer(serializers.Serializer):
    """Сериализатор для добавления и удаления избранных рецептов."""

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = self.context.get('recipe_id')
        if user.favorite.filter(recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в избранное'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = get_object_or_404(Recipe, pk=validated_data.get('id'))
        recipe.favorite.create(user=user)
        return RecipeListShortSerializer(
            instance=recipe, context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.Serializer):
    """Сериализатор для добавления и удаления рецептов из корзины."""

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = self.context.get('recipe_id')
        if user.shoppingcart.filter(recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списоке для покупок'
            )
        return data

    @atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = get_object_or_404(Recipe, pk=validated_data.get('id'))
        recipe.shoppingcart.create(user=user)
        return RecipeListShortSerializer(
            instance=recipe, context={'request': self.context.get('request')}
        ).data
