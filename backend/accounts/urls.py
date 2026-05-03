from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CustomTokenRefreshView,
    CurrentUserView,
    SendVerificationEmailView,
    VerifyEmailView,
    EmailVerificationStatusView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # Email verification endpoints
    path('auth/email/verify/send/', SendVerificationEmailView.as_view(), name='send-verification'),
    path('auth/email/verify/confirm/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/email/status/', EmailVerificationStatusView.as_view(), name='email-status'),
    
    # User profile endpoints
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
]

# Made with Bob
