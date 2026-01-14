"""
========================================
ADMIN PANEL CONTEXT PROCESSORS
========================================

Context processors to provide admin-related data to all templates.
"""

from apps.admin_panel.models import AdminRole


def admin_permissions(request):
    """
    Add user permissions to template context.

    This allows templates to check permissions like:
    {% if user_permissions.can_view_orders %}
    """
    context = {
        'user_permissions': None,
        'user_role': None,
        'is_admin': False
    }

    if not request.user.is_authenticated:
        return context

    # Superuser has all permissions
    if request.user.is_superuser:
        context['is_admin'] = True
        context['user_permissions'] = {
            'can_view_orders': True,
            'can_edit_orders': True,
            'can_process_refunds': True,
            'can_view_products': True,
            'can_edit_products': True,
            'can_manage_inventory': True,
            'can_moderate_reviews': True,
            'can_manage_featured': True,
            'can_view_users': True,
            'can_edit_users': True,
            'can_view_analytics': True,
            'can_view_activity': True,
        }
        context['user_role'] = 'Super Admin'
        return context

    # Staff user - check for AdminRole
    if request.user.is_staff:
        context['is_admin'] = True
        try:
            admin_role = request.user.admin_role
            context['user_role'] = admin_role.get_role_display()
            context['user_permissions'] = {
                'can_view_orders': admin_role.can_view_orders,
                'can_edit_orders': admin_role.can_edit_orders,
                'can_process_refunds': admin_role.can_process_refunds,
                'can_view_products': admin_role.can_view_products,
                'can_edit_products': admin_role.can_edit_products,
                'can_manage_inventory': admin_role.can_manage_inventory,
                'can_moderate_reviews': admin_role.can_moderate_reviews,
                'can_manage_featured': admin_role.can_manage_featured,
                'can_view_users': admin_role.can_view_users,
                'can_edit_users': admin_role.can_edit_users,
                'can_view_analytics': admin_role.can_view_analytics,
                'can_view_activity': admin_role.can_view_activity,
            }
        except AdminRole.DoesNotExist:
            # Staff without role - minimal permissions
            context['user_permissions'] = {
                'can_view_orders': False,
                'can_edit_orders': False,
                'can_process_refunds': False,
                'can_view_products': False,
                'can_edit_products': False,
                'can_manage_inventory': False,
                'can_moderate_reviews': False,
                'can_manage_featured': False,
                'can_view_users': False,
                'can_edit_users': False,
                'can_view_analytics': False,
                'can_view_activity': False,
            }
            context['user_role'] = 'Staff (No Role)'

    return context
