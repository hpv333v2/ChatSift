from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own resources.
    """
    message = "You do not have permission to access this resource."
    
    def has_object_permission(self, request, view, obj):
        """Check if the object belongs to the requesting user."""
        # Check if object has a 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # If object is the user itself
        return obj == request.user


class IsEmailVerified(permissions.BasePermission):
    """
    Custom permission to check if user has verified their email.
    Required for creating platform integrations.
    """
    message = "Email verification required. Please verify your email before connecting platforms."
    
    def has_permission(self, request, view):
        """Check if user's email is verified."""
        return request.user and request.user.is_authenticated and request.user.email_verified

# Made with Bob
