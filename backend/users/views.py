from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscribe, User
from .serializers import (
    SubscribeSerializer,
    SubscriptionSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserSetPasswordSerializer,
)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Representation to the user."""

    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('email', 'username')
    filterset_fields = ('email', 'username')

    def get_permissions(self):
        """Defining access for the serializer action."""

        permissions_dict = {
            'list': [permissions.IsAuthenticated()],
            'retrieve': [permissions.IsAuthenticated()],
            'me': [permissions.IsAuthenticated()],
            'set_password': [permissions.IsAuthenticated()],
            'subscriptions': [permissions.IsAuthenticated()],
            'subscribe': [permissions.IsAuthenticated()],
            'create': [permissions.AllowAny()],
        }
        return permissions_dict.get(
            self.action, [permissions.IsAuthenticated()]
        )

    def get_serializer_class(self):
        """Definition of a serializer action."""

        serializer_class_dict = {
            'create': UserCreateSerializer,
            'list': UserListSerializer,
            'retrieve': UserListSerializer,
            'me': UserListSerializer,
            'set_password': UserSetPasswordSerializer,
            'subscriptions': SubscriptionSerializer,
            'subscribe': SubscribeSerializer,
        }
        return serializer_class_dict.get(self.action)

    @action(['GET'], detail=False)
    def me(self, request):
        """Current user."""

        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(['POST'], detail=False)
    def set_password(self, request):
        """Change the user's password."""

        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        old_password = serializer.validated_data.get('current_password')

        if not user.check_password(old_password):
            return Response(
                data='Неверный пароль', status=status.HTTP_400_BAD_REQUEST
            )
        if new_password == old_password:
            return Response(
                data='Новый пароль не может совпадать со старым.',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(
            data='Пароль изменен.', status=status.HTTP_204_NO_CONTENT
        )

    @action(['GET'], detail=False)
    def subscriptions(self, request):
        """List of the user's subscriptions get."""

        user = request.user
        subscribers = User.objects.filter(subscribed__user=user)
        page = self.paginate_queryset(subscribers)
        serializer = self.get_serializer(
            instance=page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk=None):
        """Adding and deleting user subscriptions."""

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request, 'id': pk}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            user = self.request.user
            author = get_object_or_404(User, pk=pk)
            subscribe = get_object_or_404(Subscribe, user=user, author=author)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
