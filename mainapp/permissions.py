from rest_framework.permissions import BasePermission

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated and request.user.is_superuser
        return True
    
    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve']:
            return request.user.is_authenticated
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and request.user.is_superuser
        return False