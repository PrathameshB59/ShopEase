# accounts/models.py
"""
CUSTOM USER MODEL
==================
This file defines our custom User model that extends Django's built-in User.
We add a 'role' field to support different user types (Admin, Manager, Staff, Customer).

Why custom User model?
- Django's default User model is basic (just username, email, password)
- We need to add 'role' field for access control
- We need to add it from the start (can't easily change later)
"""

# Import Django's built-in AbstractUser
# AbstractUser has all the basic user fields (username, email, password, etc.)
# We inherit from it and add our custom fields
from django.contrib.auth.models import AbstractUser

# Import models module - contains all database field types
from django.db import models


class User(AbstractUser):
    """
    CUSTOM USER MODEL
    =================
    Extends Django's AbstractUser to add role-based access control.
    
    This model creates a 'accounts_user' table in the database with columns:
    - id (primary key, auto-generated)
    - username (inherited from AbstractUser)
    - email (inherited from AbstractUser)
    - password (inherited from AbstractUser, hashed)
    - first_name (inherited from AbstractUser)
    - last_name (inherited from AbstractUser)
    - is_active (inherited from AbstractUser)
    - is_staff (inherited from AbstractUser)
    - is_superuser (inherited from AbstractUser)
    - date_joined (inherited from AbstractUser)
    - last_login (inherited from AbstractUser)
    - role (our custom field)
    
    How roles work:
    - ADMIN: Full access to everything (manage users, products, orders, settings)
    - MANAGER: Can manage products and view orders
    - STAFF: Can only update order status
    - CUSTOMER: Regular shoppers (default role)
    """
    
    # ROLE CHOICES
    # =============
    # This is a tuple of tuples defining the available roles
    # Format: (database_value, human_readable_name)
    # The database stores 'ADMIN', but displays 'Admin' to users
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),        # Full system access
        ('MANAGER', 'Manager'),    # Product and order management
        ('STAFF', 'Staff'),        # Order processing only
        ('CUSTOMER', 'Customer'),  # Regular customers
    )
    
    # ROLE FIELD
    # ===========
    # CharField: Stores text data in the database
    # max_length=20: Maximum 20 characters (enough for longest role name)
    # choices=ROLE_CHOICES: User can only select from predefined roles
    # default='CUSTOMER': New users are customers by default
    # This field is required (can't be null)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
        help_text='User role determines access level in the system'
    )
    
    # PHONE NUMBER FIELD (Optional)
    # ==============================
    # Let's add a phone field for customer contact
    # blank=True: Field not required in forms
    # null=True: Can be NULL in database
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    # ADDRESS FIELDS (Optional)
    # =========================
    # Useful for quick checkout if customer has saved address
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Street address'
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='India'
    )
    
    # META CLASS
    # ===========
    # Meta class defines metadata about the model
    class Meta:
        # verbose_name: Singular name shown in admin
        verbose_name = 'User'
        
        # verbose_name_plural: Plural name shown in admin
        verbose_name_plural = 'Users'
        
        # ordering: Default order when querying users
        # '-date_joined' means newest users first (- means descending)
        ordering = ['-date_joined']
    
    # STRING REPRESENTATION
    # ======================
    # This method defines how User objects are displayed as strings
    # When you print(user) or see user in admin, this is what shows
    # Example output: "john_doe (Customer)"
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    # CUSTOM METHODS
    # ==============
    # These are helper methods to check user roles easily
    # Instead of: if user.role == 'ADMIN'
    # We can use: if user.is_admin()
    
    def is_admin(self):
        """
        Check if user is an Admin
        Returns: True if user role is ADMIN, False otherwise
        """
        return self.role == 'ADMIN'
    
    def is_manager(self):
        """
        Check if user is a Manager
        Returns: True if user role is MANAGER, False otherwise
        """
        return self.role == 'MANAGER'
    
    def is_staff_member(self):
        """
        Check if user is Staff
        Returns: True if user role is STAFF, False otherwise
        Note: Different from Django's is_staff (which is for admin access)
        """
        return self.role == 'STAFF'
    
    def is_customer(self):
        """
        Check if user is a Customer
        Returns: True if user role is CUSTOMER, False otherwise
        """
        return self.role == 'CUSTOMER'
    
    def can_manage_products(self):
        """
        Check if user can manage products (add/edit/delete)
        Returns: True if user is Admin or Manager
        """
        return self.role in ['ADMIN', 'MANAGER']
    
    def can_manage_orders(self):
        """
        Check if user can manage orders
        Returns: True if user is Admin, Manager, or Staff
        """
        return self.role in ['ADMIN', 'MANAGER', 'STAFF']
    
    def get_full_address(self):
        """
        Get user's complete address as formatted string
        Returns: Formatted address or None if no address saved
        """
        if not self.address:
            return None
        
        # Build address string from available fields
        address_parts = [self.address]
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.zip_code:
            address_parts.append(self.zip_code)
        if self.country:
            address_parts.append(self.country)
        
        return ', '.join(address_parts)


# EXPLANATION OF AbstractUser vs AbstractBaseUser
# ================================================
# We use AbstractUser (not AbstractBaseUser) because:
# 1. AbstractUser already has username, email, password fields
# 2. We just need to ADD fields (role), not change core functionality
# 3. AbstractBaseUser requires us to define everything from scratch
# 
# Use AbstractUser when: You want to add fields to default User
# Use AbstractBaseUser when: You want completely custom authentication
#                            (e.g., login with phone instead of username)