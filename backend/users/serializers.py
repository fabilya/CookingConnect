from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import User
from .validators import UsernameFieldValidator
from recipes.models import Recipe


class UserCreateSerializer(UserCreateSerializer):
    """Serializer for user creation."""

    username = UsernameFieldValidator()

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserListSerializer(UserSerializer):
    """Serializer for reading user fields."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def to_representation(self, instance):
        user = self.context.get('request').user

        if user.is_authenticated:
            return super().to_representation(instance)
        else:
            data = super().to_representation(instance)
            data['email'], data['username'] = None, None
            return data

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return author.subscribed.filter(user=user).exists()


class UserSetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset."""

    new_password = serializers.CharField(required=True, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)


class RecipeListShortSerializer(serializers.ModelSerializer):
    """Serializer to view a short recipe."""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.Serializer):
    """Serializer to view a user's subscriptions."""

    email = serializers.EmailField()
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return author.subscribed.filter(user=user).exists()

    def get_recipes(self, author):
        request = self.context.get('request')
        user = self.context.get('request').user
        if user.is_anonymous:
            return None

        recipes = author.recipes.filter(author=author)
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        else:
            recipes = recipes.all()
        return RecipeListShortSerializer(
            instance=recipes, many=True, context={'request': request}
        ).data

    def get_recipes_count(self, author):
        return author.recipes.count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class SubscribeSerializer(serializers.Serializer):
    """Serializer for adding and removing user subscriptions."""

    def validate(self, data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=self.context.get('id'))
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя самого'
            )
        if author.subscribed.filter(user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data.get('id'))
        author.subscribed.create(user=user)
        return SubscriptionSerializer(
            instance=author, context={'request': self.context.get('request')}
        ).data
