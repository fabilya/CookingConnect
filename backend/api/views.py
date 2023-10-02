from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly

from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from .utils import queryset_to_csv


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):

        permissions_dict = {
            'create': [permissions.IsAuthenticated()],
            'partial_update': [IsAuthorOrAdminOrReadOnly()],
            'favorite': [permissions.IsAuthenticated()],
            'shopping_cart': [permissions.IsAuthenticated()],
            'download_shopping_cart': [permissions.IsAuthenticated()],
            'list': [permissions.AllowAny()],
            'retrieve': [permissions.AllowAny()],
        }
        return permissions_dict.get(
            self.action, [permissions.IsAuthenticated()]
        )

    def get_serializer_class(self):

        serializer_class_dict = {
            'create': RecipeCreateSerializer,
            'partial_update': RecipeCreateSerializer,
            'download_shopping_cart': RecipeCreateSerializer,
            'list': RecipeListSerializer,
            'retrieve': RecipeListSerializer,
            'favorite': FavoriteSerializer,
            'shopping_cart': ShoppingCartSerializer,
        }
        return serializer_class_dict.get(self.action, RecipeCreateSerializer)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk=None):

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk},
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk=None):

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk},
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(permissions.IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        ingredients = (
            Recipe.ingredients.through.objects.filter(
                recipe__shoppingcart__user=request.user)
            .values('ingredient__name',
                    'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        if not ingredients.exists():
            raise ValidationError({'errors': 'Корзина пуста'})
        response = queryset_to_csv(ingredients)
        return response
