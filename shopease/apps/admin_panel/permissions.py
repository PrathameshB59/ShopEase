"""
========================================
ROLE PERMISSION DEFINITIONS
========================================

Defines the permission structure for each role in the admin panel.

This module provides:
- Role descriptions
- Default permissions per role
- Access patterns for each role
- Restrictions documentation

Used by AdminRole model to auto-assign permissions when creating roles.
"""

ROLE_PERMISSIONS = {
    'CUSTOMER_SERVICE': {
        'description': 'Handle customer inquiries, moderate reviews, view and update orders',
        'permissions': {
            'can_view_orders': True,
            'can_edit_orders': True,
            'can_process_refunds': False,
            'can_view_products': False,
            'can_edit_products': False,
            'can_manage_featured': False,
            'can_moderate_reviews': True,
            'can_view_users': False,
            'can_manage_roles': False,
            'can_view_analytics': False,
            'can_export_data': False,
        },
        'access': [
            'dashboard:index',
            'orders:list',
            'orders:detail',
            'orders:update_status',
            'reviews:list',
            'reviews:approve',
            'reviews:reject',
            'reviews:bulk_approve',
        ],
        'restrictions': [
            'Cannot process refunds',
            'Cannot edit products or inventory',
            'Cannot manage featured products',
            'Cannot access user management',
            'Cannot view detailed analytics',
        ],
    },

    'INVENTORY_MANAGER': {
        'description': 'Manage products, stock levels, and inventory',
        'permissions': {
            'can_view_orders': False,
            'can_edit_orders': False,
            'can_process_refunds': False,
            'can_view_products': True,
            'can_edit_products': True,
            'can_manage_featured': False,
            'can_moderate_reviews': False,
            'can_view_users': False,
            'can_manage_roles': False,
            'can_view_analytics': True,
            'can_export_data': False,
        },
        'access': [
            'dashboard:index',
            'products:list',
            'products:create',
            'products:edit',
            'products:delete',
            'products:analytics',
        ],
        'restrictions': [
            'Cannot access orders',
            'Cannot manage featured products (Marketing only)',
            'Cannot moderate reviews',
            'Cannot manage users or roles',
            'Cannot export data',
        ],
    },

    'MARKETING_MANAGER': {
        'description': 'Manage featured products, view analytics, export data',
        'permissions': {
            'can_view_orders': False,
            'can_edit_orders': False,
            'can_process_refunds': False,
            'can_view_products': True,
            'can_edit_products': False,
            'can_manage_featured': True,
            'can_moderate_reviews': False,
            'can_view_users': False,
            'can_manage_roles': False,
            'can_view_analytics': True,
            'can_export_data': True,
        },
        'access': [
            'dashboard:index',
            'products:list',
            'products:analytics',
            'products:featured_manage',
            'products:auto_suggest',
            'reports:sales',
            'reports:revenue',
            'reports:export',
        ],
        'restrictions': [
            'Cannot edit product inventory',
            'Cannot access orders',
            'Cannot moderate reviews',
            'Cannot manage users',
        ],
    },

    'ORDER_MANAGER': {
        'description': 'Full order management including refunds and returns',
        'permissions': {
            'can_view_orders': True,
            'can_edit_orders': True,
            'can_process_refunds': True,
            'can_view_products': False,
            'can_edit_products': False,
            'can_manage_featured': False,
            'can_moderate_reviews': False,
            'can_view_users': False,
            'can_manage_roles': False,
            'can_view_analytics': True,
            'can_export_data': False,
        },
        'access': [
            'dashboard:index',
            'orders:*',  # All order views
            'reports:sales',
            'reports:revenue',
        ],
        'restrictions': [
            'Cannot manage products',
            'Cannot manage users',
            'Cannot moderate reviews',
            'Cannot export data (request from Marketing)',
        ],
    },

    'SUPER_ADMIN': {
        'description': 'Full access to all admin features',
        'permissions': {
            'can_view_orders': True,
            'can_edit_orders': True,
            'can_process_refunds': True,
            'can_view_products': True,
            'can_edit_products': True,
            'can_manage_featured': True,
            'can_moderate_reviews': True,
            'can_view_users': True,
            'can_manage_roles': True,
            'can_view_analytics': True,
            'can_export_data': True,
        },
        'access': ['*'],  # Everything
        'restrictions': [],  # No restrictions
    },
}


def get_role_description(role_name):
    """
    Get human-readable description for a role.

    Args:
        role_name: Role name string (e.g., 'CUSTOMER_SERVICE')

    Returns:
        String description or "Unknown role"
    """
    role_data = ROLE_PERMISSIONS.get(role_name, {})
    return role_data.get('description', 'Unknown role')


def get_role_access_list(role_name):
    """
    Get list of views/routes accessible to a role.

    Args:
        role_name: Role name string

    Returns:
        List of accessible route patterns
    """
    role_data = ROLE_PERMISSIONS.get(role_name, {})
    return role_data.get('access', [])


def get_role_restrictions(role_name):
    """
    Get list of restrictions for a role.

    Args:
        role_name: Role name string

    Returns:
        List of restriction descriptions
    """
    role_data = ROLE_PERMISSIONS.get(role_name, {})
    return role_data.get('restrictions', [])


def check_role_permission(role_name, permission_name):
    """
    Check if a role has a specific permission.

    Args:
        role_name: Role name string
        permission_name: Permission field name (e.g., 'can_view_orders')

    Returns:
        Boolean indicating if role has permission
    """
    role_data = ROLE_PERMISSIONS.get(role_name, {})
    permissions = role_data.get('permissions', {})
    return permissions.get(permission_name, False)
