"""
Custom authentication backend for ShopEase Documentation.

Allows users to login with either username OR email address.
This matches the authentication pattern used in the main ShopEase project.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email or username.

    This backend checks if the provided username matches either:
    - The user's username (case-insensitive)
    - The user's email address (case-insensitive)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user by username/email and password.

        Args:
            request: The HTTP request object
            username: The username or email provided by the user
            password: The password provided by the user

        Returns:
            User object if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None

        try:
            # Try to find user by username or email (case-insensitive)
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

            # Check password and return user if valid
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        except User.DoesNotExist:
            # Run the default password hasher to prevent timing attacks
            User().set_password(password)
            return None

        except User.MultipleObjectsReturned:
            # If multiple users match (shouldn't happen), return None
            return None

        return None

    def get_user(self, user_id):
        """
        Retrieve a user by their primary key.

        Args:
            user_id: The user's primary key

        Returns:
            User object if found and active, None otherwise
        """
        try:
            user = User.objects.get(pk=user_id)
            if self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        return None
