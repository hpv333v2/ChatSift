from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()

# Constants
EMAIL_NOT_VERIFIED = 'not_verified'


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generator for email verification.
    Creates a unique token based on user's email verification status.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key, email, and email_verified status.
        This ensures the token becomes invalid once email is verified.
        """
        email_verified = '' if user.email_verified else EMAIL_NOT_VERIFIED
        return f"{user.pk}{user.email}{email_verified}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()


def generate_verification_token(user):
    """
    Generate a verification token and UID for a user.
    
    Returns:
        dict: Contains 'token' and 'uid' for verification
    """
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return {
        'token': token,
        'uid': uid
    }


def verify_token(uid, token):
    """
    Verify a token and return the user if valid.
    
    Args:
        uid: Base64 encoded user ID
        token: Verification token
    
    Returns:
        User object if valid, None otherwise
    """
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
        
        # Check if token is valid
        if email_verification_token.check_token(user, token):
            return user
        return None
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

# Made with Bob
