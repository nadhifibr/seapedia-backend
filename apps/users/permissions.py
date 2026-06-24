from rest_framework.permissions import BasePermission

class IsActiveBuyer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.auth and 
            request.auth.payload.get('active_role') == 'BUYER'
        )

class IsActiveSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.auth and 
            request.auth.payload.get('active_role') == 'SELLER'
        )

class IsActiveDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.auth and 
            request.auth.payload.get('active_role') == 'DRIVER'
        )

class IsActiveAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.auth and 
            request.auth.payload.get('active_role') == 'ADMIN'
        )
