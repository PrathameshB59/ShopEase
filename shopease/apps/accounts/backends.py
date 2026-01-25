"""
========================================
CUSTOM AUTHENTICATION BACKENDS
========================================

Email/Username Authentication Backend
--------------------------------------
Allows users to login with either:
1. Username + Password
2. Email + Password

How it works:
- Overrides Django's default ModelBackend
- First tries to find user by username
- If not found, tries to find user by email
- Verifies password hash
- Returns User object if valid

Security:
- Uses Django's built-in password verification
- Case-insensitive email matching
- Active user check
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email or username.

    Usage in views:
        user = authenticate(username='john', password='secret')
        # OR
        user = authenticate(username='john@example.com', password='secret')

    The 'username' parameter can be either a username or email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username.

        Args:
            request: HTTP request object
            username: Username or email address (can be either)
            password: User's password (plaintext - will be verified)
            **kwargs: Additional arguments

        Returns:
            User object if authentication succeeds
            None if authentication fails

        Process:
        1. Try to find user by username (exact match)
        2. If not found, try to find user by email (case-insensitive)
        3. Verify password hash
        4. Check if user is active
        5. Return User object or None

        Security:
        - Password is never logged or exposed
        - Uses Django's check_password (timing attack resistant)
        - Case-insensitive email matching (prevents duplicate accounts)
        - Active user check (disabled accounts can't login)
        """

        if username is None or password is None:
            return None

        try:
            # Try to find user by username OR email
            # Q objects allow complex database queries (OR/AND conditions)
            # Case-insensitive email matching: email__iexact
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

            # Verify password
            # check_password compares hashed passwords (secure)
            # Returns True if password matches, False otherwise
            if user.check_password(password):
                # Check if user account is active
                # Inactive accounts (is_active=False) can't login
                if user.is_active:
                    return user
                return None
            else:
                return None

        except User.DoesNotExist:
            # User not found (invalid username/email)
            # Don't reveal which part is wrong (security)
            return None

        except User.MultipleObjectsReturned:
            # Multiple users found with same email (duplicate data)
            # This shouldn't happen but can occur if email uniqueness wasn't enforced
            # Strategy: Try to find the correct user by checking password on all matches
            users = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).filter(is_active=True)

            # Try to authenticate each user with the provided password
            for user in users:
                if user.check_password(password):
                    # Found matching user with correct password
                    return user

            # No user matched the password
            return None

    def get_user(self, user_id):
        """
        Get user by ID (required by Django).

        Called when loading user from session.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
