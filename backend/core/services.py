from datetime import datetime as dt
from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models import F, Sum
from foodgram.settings import DATE_TIME_FORMAT

if TYPE_CHECKING:
    from users.models import User


def create_shoping_list(user: "User") -> str:
    shopping_list = [
        f"Список покупок для:\n\n{user.first_name}\n"
        f"{dt.now().strftime(DATE_TIME_FORMAT)}\n"
    ]
    ingredient = apps.get_model("recipes", "Ingredient")
    ingredients = (
        ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values("name", measurement=F("measurement_unit"))
        .annotate(amount=Sum("recipe__amount"))
    )
    ing_list = (
        f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_list.extend(ing_list)

    shopping_list.append("\nПосчитано в Foodgram")
    return "\n".join(shopping_list)
