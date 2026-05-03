"""
URL configuration for the integrations app.
"""
from django.urls import path
from .views import (
    DiscordAuthorizeView,
    DiscordCallbackView,
    TelegramConnectView,
    ConnectionListView,
    ConnectionDetailView,
    ConnectionRefreshView,
)

app_name = 'integrations'

urlpatterns = [
    # Discord OAuth endpoints
    path(
        'discord/authorize/',
        DiscordAuthorizeView.as_view(),
        name='discord-authorize'
    ),
    path(
        'discord/callback/',
        DiscordCallbackView.as_view(),
        name='discord-callback'
    ),
    
    # Telegram endpoints
    path(
        'telegram/connect/',
        TelegramConnectView.as_view(),
        name='telegram-connect'
    ),
    
    # General connection endpoints
    path(
        '',
        ConnectionListView.as_view(),
        name='connection-list'
    ),
    path(
        '<uuid:pk>/',
        ConnectionDetailView.as_view(),
        name='connection-detail'
    ),
    path(
        '<uuid:pk>/refresh/',
        ConnectionRefreshView.as_view(),
        name='connection-refresh'
    ),
]

# Made with Bob