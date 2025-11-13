from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    """Permission class that grants access only to users identified as business users.
    This DRF permission checks the incoming request's user and allows access only when
    request.user.type == 'business'.
    Behavior:
    - Returns True if the authenticated user's 'type' equals 'business'.
    - Returns False otherwise.
    """
    def has_permission(self, request, view):
        if request.user.type == 'business':
            return True
    
        return False
    
class IsOfferOwner(permissions.BasePermission):
    """
    Permission class for Django REST Framework that grants access only to the owner of an offer object.

    The permission check is performed in has_object_permission by comparing the object's `user`
    attribute to `request.user`. It returns True when they are equal (the requester is the owner),
    and False otherwise.
    """
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False