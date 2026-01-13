"""
========================================
PERMISSION DECORATORS
========================================

Custom decorators for role-based access control in the admin panel.

Provides three levels of permission checking:
1. @admin_required - Basic staff/admin check
2. @permission_required - Granular permission check
3. @role_required - Specific role requirement

Usage:
    from apps.admin_panel.decorators import admin_required, permission_required

    @admin_required
    def some_admin_view(request):
        ...

    @permission_required('can_view_orders', 'can_edit_orders')
    def order_detail(request, order_id):
        ...

    @role_required('ORDER_MANAGER', 'SUPER_ADMIN')
    def process_refund(request, refund_id):
        ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """
    Decorator to require user to be staff/admin.

    Checks:
    - User is authenticated
    - User has is_staff=True

    If checks fail, redirect to home with error message.

    Usage:
        @admin_required
        def my_admin_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(
                request,
                'Access denied. Admin privileges required.'
            )
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(*permissions):
    """
    Decorator to check granular admin permissions.

    Checks if user has specific permissions based on their AdminRole.
    Superusers bypass all permission checks.

    Args:
        *permissions: Variable number of permission names to check
                     (e.g., 'can_view_orders', 'can_edit_orders')

    Raises:
        PermissionDenied: If user doesn't have required permissions

    Usage:
        @permission_required('can_view_orders')
        def order_list(request):
            ...

        @permission_required('can_view_orders', 'can_edit_orders')
        def order_detail(request, order_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @admin_required
        def wrapper(request, *args, **kwargs):
            # Superusers bypass permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has admin role assigned
            if not hasattr(request.user, 'admin_role'):
                messages.error(
                    request,
                    'Access denied. No admin role assigned to your account.'
                )
                return redirect('admin_panel:dashboard')

            admin_role = request.user.admin_role

            # Check all required permissions
            missing_perms = []
            for perm in permissions:
                if not getattr(admin_role, perm, False):
                    missing_perms.append(perm)

            if missing_perms:
                perm_names = ', '.join([p.replace('_', ' ').title() for p in missing_perms])
                messages.error(
                    request,
                    f'Access denied. Missing permission(s): {perm_names}'
                )
                return redirect('admin_panel:dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required(*roles):
    """
    Decorator to require specific role(s).

    Checks if user has one of the specified roles.
    Superusers bypass role requirements.

    Args:
        *roles: Variable number of role names that are allowed
               (e.g., 'ORDER_MANAGER', 'SUPER_ADMIN')

    Usage:
        @role_required('ORDER_MANAGER')
        def process_refund(request, refund_id):
            ...

        @role_required('ORDER_MANAGER', 'SUPER_ADMIN')
        def bulk_order_update(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @admin_required
        def wrapper(request, *args, **kwargs):
            # Superusers bypass role checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has admin role
            if not hasattr(request.user, 'admin_role'):
                messages.error(
                    request,
                    'Access denied. No admin role assigned to your account.'
                )
                return redirect('admin_panel:dashboard')

            admin_role = request.user.admin_role

            # Check if user's role is in allowed roles
            if admin_role.role not in roles:
                allowed_roles = ', '.join([r.replace('_', ' ').title() for r in roles])
                messages.error(
                    request,
                    f'Access denied. Required role: {allowed_roles}'
                )
                return redirect('admin_panel:dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_admin_activity(action_type):
    """
    Decorator to automatically log admin actions.

    Creates an AdminActivity record for the action.
    Can be combined with other decorators.

    Args:
        action_type: Type of action from AdminActivity.ACTION_CHOICES

    Usage:
        @log_admin_activity('ORDER_STATUS_CHANGE')
        @permission_required('can_edit_orders')
        def update_order_status(request, order_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view
            response = view_func(request, *args, **kwargs)

            # Log the activity (import here to avoid circular imports)
            from apps.admin_panel.models import AdminActivity

            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Create activity log
            AdminActivity.objects.create(
                user=request.user,
                action=action_type,
                description=f"{action_type} - View: {view_func.__name__}",
                ip_address=ip_address,
                order_id=kwargs.get('order_id'),
                product_id=kwargs.get('product_id'),
            )

            return response
        return wrapper
    return decorator
