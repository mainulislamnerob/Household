from rest_framework import permissions

class IsAdminUserCustom(permissions.BasePermission):
    """Allow access only to users with is_admin True."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False))

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
