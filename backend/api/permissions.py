from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class OwnerUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
