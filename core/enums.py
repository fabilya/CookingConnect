"""Настройки параметров.
"""
from enum import Enum, IntEnum


class Tuples(tuple, Enum):
    RECIPE_IMAGE_SIZE = 500, 500
    SYMBOL_TRUE_SEARCH = "1", "true"
    SYMBOL_FALSE_SEARCH = "0", "false"


class Limits(IntEnum):
    MAX_LEN_EMAIL_FIELD = 256
    MAX_LEN_USERS_CHARFIELD = 32
    MIN_LEN_USERNAME = 3
    MAX_LEN_RECIPES_CHARFIELD = 64
    MAX_LEN_MEASUREMENT = 256
    MAX_LEN_RECIPES_TEXTFIELD = 5000
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 300
    MIN_AMOUNT_INGREDIENTS = 1
    MAX_AMOUNT_INGREDIENTS = 32


class UrlQueries(str, Enum):
    # Параметр для поиска ингридиентов по вхождению значения в название
    SEARCH_ING_NAME = "name"
    # Параметр для поиска объектов в списке "избранное"
    FAVORITE = "is_favorited"
    # Параметр для поиска объектов в списке "покупки"
    SHOP_CART = "is_in_shopping_cart"
    # Параметр для поиска объектов по автору
    AUTHOR = "author"
    # Параметр для поиска объектов по тэгам
    TAGS = "tags"
