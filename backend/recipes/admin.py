from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import (Favorite, Ingredient, IngredientAmount,
                     Recipe, ShoppingCart, Tag)


class RecipeResource(ModelResource):
    """Recipe resource model"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'pub_date',
        )


class IngredientsInline(admin.TabularInline):
    """Menu to manage the ingredients in a recipe."""

    model = IngredientAmount
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    """Registration of recipe model and import/export in admin panel."""

    resource_class = (RecipeResource,)
    inlines = (IngredientsInline,)
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author')


class TagResource(ModelResource):
    """Tagging Resource Model."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    """Register tag model and import/export in admin panel."""

    resource_class = (TagResource,)
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'color', 'slug')


class IngredientResource(ModelResource):
    """Ingredient resource model."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Registration of ingredient model and import/export in admin panel."""

    resource_classes = (IngredientResource,)
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class IngredientAmountResource(ModelResource):
    """A model of an ingredient in a recipe."""

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'recipe',
            'ingredient',
            'amount',
        )


@admin.register(IngredientAmount)
class IngredientAmountAdmin(ImportExportModelAdmin):
    """
    Registration of the ingredient model in the recipe and
    import/export in the admin panel.
    """

    resource_classes = (IngredientAmountResource,)
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe', 'ingredient')


class FavoriteResource(ModelResource):
    """A resource model of selected prescription resources."""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(Favorite)
class FavoriteAdmin(ImportExportModelAdmin):
    """
    Registration of favorite recipes and import/export model in admin panel.
    """

    resource_classes = (FavoriteResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')


class ShoppingCartResource(ModelResource):
    """Prescription resource model in your shopping cart."""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ImportExportModelAdmin):
    """
    Registration of recipe model in cart and import/export in admin panel.
    """

    resource_classes = (ShoppingCartResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
