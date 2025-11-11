from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'customer':
            return True
    
        return False