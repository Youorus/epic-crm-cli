from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsGestionOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'GESTION'

class IsCommercial(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'COMMERCIAL'

class IsSupport(BasePermission):
     def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPPORT'