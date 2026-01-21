"""
One-time authentication tokens for cross-port login.
Enables secure transfer of authentication state between customer and admin servers.
"""
import secrets
from django.core.cache import cache


TOKEN_EXPIRY_SECONDS = 60  # Token valid for 60 seconds
TOKEN_PREFIX = 'auth_token:'


def generate_auth_token(user_id, username):
    """
    Generate a one-time authentication token for cross-port login.

    Args:
        user_id: User's database ID
        username: User's username

    Returns:
        str: Random token string (cryptographically secure)
    """
    # Generate secure random token (32 bytes = 43 characters in base64)
    token = secrets.token_urlsafe(32)

    # Store in cache with user info
    cache_key = f"{TOKEN_PREFIX}{token}"
    cache.set(cache_key, {
        'user_id': user_id,
        'username': username,
    }, timeout=TOKEN_EXPIRY_SECONDS)

    print(f"Generated auth token for user {username}: {token[:8]}... (expires in {TOKEN_EXPIRY_SECONDS}s)")
    return token


def validate_auth_token(token):
    """
    Validate and consume a one-time authentication token.

    Security:
    - Token is deleted after validation (single use)
    - Token expires after TOKEN_EXPIRY_SECONDS
    - Invalid tokens return {'valid': False}

    Args:
        token: Token string to validate

    Returns:
        dict: {'valid': bool, 'user_id': int, 'username': str} or {'valid': False}
    """
    cache_key = f"{TOKEN_PREFIX}{token}"
    user_data = cache.get(cache_key)

    if user_data:
        # Token is valid - delete it immediately (single use)
        cache.delete(cache_key)
        print(f"Validated and consumed auth token for user {user_data['username']}")
        return {
            'valid': True,
            'user_id': user_data['user_id'],
            'username': user_data['username']
        }
    else:
        print(f"Invalid or expired auth token: {token[:8] if len(token) >= 8 else token}...")
        return {'valid': False}
