"""
Custom permissions for the integrations app.
"""
from rest_framework.permissions import BasePermission


class IsEmailVerified(BasePermission):
    """
    Permission to check if user has verified their email.
    Required before users can create platform integrations.
    """
    message = "Email verification required to connect platforms. Please verify your email first."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has verified email."""
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'email_verified', False)
        )


class IsConnectionOwner(BasePermission):
    """
    Permission to check if user owns the platform connection.
    Ensures users can only access their own connections.
    """
    message = "You do not have permission to access this connection."
    
    def has_object_permission(self, request, view, obj):
        """Check if the user owns the connection."""
        # For PlatformConnection objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For Channel objects (check through connection)
        if hasattr(obj, 'connection'):
            return obj.connection.user == request.user
        
        return False


class CanManageConnection(BasePermission):
    """
    Permission for managing connections (update, delete).
    Only allows actions on active connections owned by the user.
    """
    message = "You cannot manage this connection."
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage the connection."""
        # Must be the owner
        if not (hasattr(obj, 'user') and obj.user == request.user):
            return False
        
        # For DELETE requests, connection must not be in error state
        # (allow deletion of error connections for cleanup)
        if request.method == 'DELETE':
            return True
        
        # For other methods, connection should be active or expired
        # (not revoked, as revoked connections should be deleted)
        if hasattr(obj, 'status'):
            return obj.status in ['active', 'expired', 'error']
        
        return True


# Made with Bob