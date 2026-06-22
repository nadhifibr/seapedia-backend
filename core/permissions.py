from rest_framework.permissions import BasePermission

class BaseRolePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        # Memastikan user sudah login
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Mengecek payload JWT dari request.auth
        if hasattr(request, 'auth') and request.auth:
            active_role = request.auth.payload.get('active_role', '')
            return active_role == self.required_role
        
        return False

class IsActiveBuyer(BaseRolePermission):
    """
    Permission khusus untuk user yang active_role-nya adalah 'BUYER'.
    """
    required_role = 'BUYER'

class IsActiveSeller(BaseRolePermission):
    """
    Permission khusus untuk user yang active_role-nya adalah 'SELLER'.
    """
    required_role = 'SELLER'

class IsActiveDriver(BaseRolePermission):
    """
    Permission khusus untuk user yang active_role-nya adalah 'DRIVER'.
    """
    required_role = 'DRIVER'

class IsAdmin(BaseRolePermission):
    """
    Permission khusus untuk user yang active_role-nya adalah 'ADMIN'.
    """
    required_role = 'ADMIN'

class IsAuthenticatedWithRole(BasePermission):
    """
    Permission untuk memastikan user sudah login DAN sudah memilih active_role
    (active_role tidak boleh kosong).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if hasattr(request, 'auth') and request.auth:
            active_role = request.auth.payload.get('active_role', '')
            return bool(active_role) # Return True jika active_role tidak empty string
            
        return False
