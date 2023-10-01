import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.settings import FILENAME
from .filters import IngredientFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    """Representation for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Representation for ingredients."""

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
    """Representation for recipes."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        """Defining access for serializer action."""

        permissions_dict = {
            'create': [permissions.IsAuthenticated()],
            'partial_update': [permissions.IsAuthenticated()],
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
        """Definition of a serializer action."""

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
        """Adding and removing recipes from favorites."""

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
        """Adding and removing recipes from the shopping cart."""

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

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):

        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.shopping_cart.recipe.
            values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        page.setFont('DejaVuSans', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredients__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=FILENAME)
        page.setFont('DejaVuSans', 24)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!')
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=FILENAME)
