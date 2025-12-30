# accounts/admin.py
"""
ADMIN CONFIGURATION FOR USER MODEL
====================================
This file configures how the User model appears in Django's admin interface.
Admin interface is at: http://127.0.0.1:8000/admin/

We customize:
- Which fields are displayed in the user list
- Which fields can be filtered
- Which fields are searchable
- How the edit form is organized
"""

# Import Django's admin module
from django.contrib import admin

# Import Django's built-in UserAdmin to extend it
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Import our custom User model
from .models import User


# CUSTOM USER ADMIN CLASS
# ========================
# We extend Django's UserAdmin and customize it for our needs

@admin.register(User)  # This decorator registers User model with this admin class
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model
    Extends Django's built-in UserAdmin with our custom 'role' field
    """
    
    # LIST DISPLAY
    # =============
    # These fields appear as columns in the user list page
    # Shows: Username | Email | Full Name | Role | Staff Status | Active Status
    list_display = [
        'username',           # User's login name
        'email',             # User's email address
        'get_full_name',     # Combined first and last name
        'role',              # Our custom role field (ADMIN/MANAGER/STAFF/CUSTOMER)
        'is_staff',          # Can access admin panel? (Yes/No)
        'is_active',         # Account active? (Yes/No)
        'date_joined'        # When user registered
    ]
    
    # LIST FILTER
    # ============
    # Add filter sidebar on right side of user list
    # Users can filter by role, staff status, superuser status, active status
    list_filter = [
        'role',              # Filter by: Admin, Manager, Staff, Customer
        'is_staff',          # Filter by: Can access admin
        'is_superuser',      # Filter by: Is superuser
        'is_active',         # Filter by: Active accounts
        'date_joined'        # Filter by: Registration date
    ]
    
    # SEARCH FIELDS
    # ==============
    # Add search box at top of user list
    # Users can search by username, first name, last name, or email
    search_fields = [
        'username',          # Search in username
        'first_name',        # Search in first name
        'last_name',         # Search in last name
        'email'              # Search in email
    ]
    
    # ORDERING
    # =========
    # Default sort order for user list
    # '-date_joined' means newest users first (minus sign = descending)
    ordering = ['-date_joined']
    
    # FIELDSETS
    # ==========
    # Organize the edit form into sections with headers
    # Each tuple is: ('Section Title', {'fields': (...)})
    
    fieldsets = (
        # SECTION 1: Login Credentials
        # Shows username and password fields
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        
        # SECTION 2: Personal Information
        # Shows name and email fields
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        
        # SECTION 3: Address Information
        # Shows address fields for customer shipping
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country'),
            # 'classes': ('collapse',) would make this section collapsible
        }),
        
        # SECTION 4: Role & Permissions
        # Shows our custom role field and Django's permission fields
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser'),
            'description': 'Role determines what the user can do in the system'
        }),
        
        # SECTION 5: Groups & Permissions (Advanced)
        # Django's group-based permissions system
        ('Advanced Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),  # Make this section collapsed by default
            'description': 'Advanced permission settings (usually not needed)'
        }),
        
        # SECTION 6: Important Dates
        # Shows when user joined and last logged in
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),  # Collapsed by default
        }),
    )
    
    # ADD_FIELDSETS
    # ==============
    # Fieldsets used when CREATING a new user (different from editing)
    # Simplified form with just essential fields
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),  # Make fields wider
            'fields': (
                'username',
                'email',
                'password1',     # Password field
                'password2',     # Password confirmation field
                'role',          # Select user role
                'is_staff',      # Can access admin?
                'is_active'      # Account active?
            ),
            'description': 'Enter details for the new user'
        }),
    )
    
    # LIST_EDITABLE
    # ==============
    # Fields that can be edited directly in the list view (without opening detail page)
    # Commented out because it conflicts with list_display_links
    # Uncomment if you want quick editing:
    # list_editable = ['role', 'is_active']
    
    # ACTIONS
    # ========
    # Bulk actions that can be performed on selected users
    # Django provides 'delete' by default, we add custom ones
    
    actions = ['make_customer', 'make_staff', 'activate_users', 'deactivate_users']
    
    def make_customer(self, request, queryset):
        """
        Bulk action: Change selected users' role to Customer
        Usage: Select users -> Actions dropdown -> "Make Customer"
        """
        # queryset.update() is efficient - updates all in one database query
        updated = queryset.update(role='CUSTOMER')
        
        # Show success message to admin
        # self.message_user() displays a green success banner at top
        self.message_user(
            request,
            f'{updated} user(s) successfully changed to Customer role.'
        )
    make_customer.short_description = "Change role to Customer"  # Action label in dropdown
    
    def make_staff(self, request, queryset):
        """
        Bulk action: Change selected users' role to Staff
        """
        updated = queryset.update(role='STAFF')
        self.message_user(
            request,
            f'{updated} user(s) successfully changed to Staff role.'
        )
    make_staff.short_description = "Change role to Staff"
    
    def activate_users(self, request, queryset):
        """
        Bulk action: Activate selected users
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} user(s) successfully activated.'
        )
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """
        Bulk action: Deactivate selected users (soft delete)
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} user(s) successfully deactivated.'
        )
    deactivate_users.short_description = "Deactivate selected users"
    
    # CUSTOM DISPLAY METHODS
    # =======================
    # These methods customize how data is displayed in list_display
    
    def get_full_name(self, obj):
        """
        Display user's full name in user list
        obj = User object (each row in the list)
        """
        # Return "First Last" or "N/A" if no name set
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else "N/A"
    
    # Set column header for this method
    get_full_name.short_description = 'Full Name'
    
    # READONLY FIELDS
    # ================
    # Fields that can be viewed but not edited
    # Useful for system-generated data like registration date
    # readonly_fields = ['date_joined', 'last_login']
    
    # FILTER HORIZONTAL
    # ==================
    # Makes many-to-many fields easier to use with a nice widget
    filter_horizontal = ('groups', 'user_permissions')


# HOW TO USE THIS ADMIN
# ======================
# 1. Run migrations: python manage.py makemigrations && python manage.py migrate
# 2. Create superuser: python manage.py createsuperuser
# 3. Run server: python manage.py runserver
# 4. Go to: http://127.0.0.1:8000/admin/
# 5. Login with superuser credentials
# 6. Click "Users" to see this custom admin interface!

# ADMIN INTERFACE FEATURES
# =========================
# ✅ View all users in organized table
# ✅ Filter by role, status, date
# ✅ Search by name, email, username
# ✅ Edit user details with organized form
# ✅ Bulk actions (change roles, activate/deactivate)
# ✅ Create new users with simple form
# ✅ See registration and login dates