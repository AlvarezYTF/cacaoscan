"""
Helper functions for tests.
"""
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.test import APIClient


def authenticate_client(client: APIClient, user: User) -> None:
    """
    Authenticate a test client with JWT token for a user.
    
    Args:
        client: APIClient instance
        user: User instance to authenticate
    """
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')


def create_authenticated_client(user: User) -> APIClient:
    """
    Create and return an authenticated APIClient for a user.
    
    Args:
        user: User instance to authenticate
        
    Returns:
        Authenticated APIClient
    """
    client = APIClient()
    authenticate_client(client, user)
    return client

