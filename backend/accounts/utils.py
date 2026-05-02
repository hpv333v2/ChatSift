import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .tokens import generate_verification_token

logger = logging.getLogger(__name__)


def send_verification_email(user, request=None):
    """
    Send email verification link to user.
    
    Args:
        user: User object
        request: HTTP request object (optional, for building absolute URLs)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Generate verification token
    token_data = generate_verification_token(user)
    
    # Build verification URL
    frontend_url = settings.FRONTEND_URL
    verification_url = f"{frontend_url}/verify-email?token={token_data['token']}&uid={token_data['uid']}"
    
    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'frontend_url': frontend_url,
    }
    
    # Email subject
    subject = 'Verify your ChatSift email address'
    
    # Email body (plain text)
    message = f"""
Hi {user.username},

Welcome to ChatSift! Please verify your email address to start connecting your messaging platforms.

Click the link below to verify your email:
{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
The ChatSift Team
    """.strip()
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after email verification.
    
    Args:
        user: User object
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    frontend_url = settings.FRONTEND_URL
    dashboard_url = f"{frontend_url}/dashboard"
    
    subject = 'Welcome to ChatSift!'
    
    message = f"""
Hi {user.username},

Your email has been verified! You can now:
- Connect Discord servers
- Connect Telegram groups
- Set up monitoring schedules
- Receive AI-powered summaries

Get started: {dashboard_url}

Best regards,
The ChatSift Team
    """.strip()
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending welcome email to {user.email}: {e}")
        return False


def send_password_reset_email(user, token_data):
    """
    Send password reset email to user.
    
    Args:
        user: User object
        token_data: Dict containing 'token' and 'uid'
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    frontend_url = settings.FRONTEND_URL
    reset_url = f"{frontend_url}/reset-password?token={token_data['token']}&uid={token_data['uid']}"
    
    subject = 'Reset your ChatSift password'
    
    message = f"""
Hi {user.username},

We received a request to reset your password. Click the link below to create a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The ChatSift Team
    """.strip()
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {e}")
        return False

# Made with Bob
