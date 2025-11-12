from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'customer':
            return True
    
        return False
    
class IsReviewer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.reviewer:
            return True
        
        return False