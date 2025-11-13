from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    """
    Permission class that allows access only to users
    whose 'type' attribute is equal to 'customer'.
    Its has_permission method returns True when request.user.type == 'customer',
    and False otherwise.
    """
    def has_permission(self, request, view):
        if request.user.type == 'customer':
            return True
    
        return False
    
class IsReviewer(permissions.BasePermission):
    """Allow object-level access only to the object's reviewer.
    It grants access to an object only when the requesting user (request.user) is
    the same as the object's `reviewer` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.user == obj.reviewer:
            return True
        
        return False