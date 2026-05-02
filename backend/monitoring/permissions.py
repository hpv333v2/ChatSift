"""
Custom permissions for the monitoring app.
"""
from rest_framework.permissions import BasePermission


class IsMonitoringOwner(BasePermission):
    """
    Permission to check if user owns the monitored channel.
    Ensures users can only access their own monitoring configurations.
    """
    message = "You do not have permission to access this monitoring configuration."
    
    def has_object_permission(self, request, view, obj):
        """Check if the user owns the monitored channel."""
        # For MonitoredChannel objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For MonitoringSchedule objects (check through monitored_channel)
        if hasattr(obj, 'monitored_channel'):
            return obj.monitored_channel.user == request.user
        
        return False


class CanManageMonitoring(BasePermission):
    """
    Permission for managing monitoring configurations.
    Requires email verification and active platform connection.
    """
    message = "You must have an active platform connection to manage monitoring."
    
    def has_permission(self, request, view):
        """Check if user can manage monitoring."""
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required to manage monitoring."
            return False
        
        # Must have verified email
        if not getattr(request.user, 'email_verified', False):
            self.message = "Email verification required to manage monitoring."
            return False
        
        # For POST requests (creating monitoring), check if user has active connections
        if request.method == 'POST':
            from integrations.models import PlatformConnection
            has_connection = PlatformConnection.objects.filter(
                user=request.user,
                status='active'
            ).exists()
            
            if not has_connection:
                self.message = "You must connect a platform before monitoring channels."
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage this specific monitoring configuration."""
        # Must be the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For MonitoringSchedule objects
        if hasattr(obj, 'monitored_channel'):
            return obj.monitored_channel.user == request.user
        
        return False


# Made with Bob