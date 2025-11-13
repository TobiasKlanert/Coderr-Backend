from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """
    Permission class that grants access only to authenticated users whose 'type' attribute is 'customer'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'type', None) == 'customer')
