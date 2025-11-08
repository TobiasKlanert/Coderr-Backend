from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'business':
            return True
    
        return False
    
class IsOfferOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False