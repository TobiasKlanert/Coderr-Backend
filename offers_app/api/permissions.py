from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'business':
            return True
    
        return False