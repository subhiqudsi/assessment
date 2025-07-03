from rest_framework import authentication, exceptions
from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger('hr_system')


class AdminHeaderAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication that checks for X-ADMIN=1 header
    """
    
    def authenticate(self, request):
        """
        Authenticate based on X-ADMIN header
        Returns None if not an admin request, or (user, token) if valid admin
        """
        admin_header = request.META.get('HTTP_X_ADMIN')
        
        if admin_header == '1':
            # Create a simple admin user object
            class AdminUser:
                is_authenticated = True
                is_admin = True
                username = 'admin'
                
                def __str__(self):
                    return 'admin'
            
            logger.info(f"Admin access granted to {request.META.get('REMOTE_ADDR', 'unknown')} for {request.path}")
            return (AdminUser(), None)
        
        return None


class IsAdminUser(BasePermission):
    """
    Permission class that requires X-ADMIN=1 header
    """
    
    def has_permission(self, request, view):
        """
        Check if user has admin permissions via X-ADMIN header
        """
        admin_header = request.META.get('HTTP_X_ADMIN')
        
        if admin_header != '1':
            logger.warning(
                f"Unauthorized admin access attempt from {request.META.get('REMOTE_ADDR', 'unknown')} "
                f"to {request.path}"
            )
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check for admin users
        """
        return self.has_permission(request, view)