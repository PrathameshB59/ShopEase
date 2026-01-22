"""
========================================
ADMIN PANEL CONTEXT PROCESSORS
========================================

Context processors to provide admin-related data to all templates.
"""

from django.conf import settings
from apps.admin_panel.models import AdminRole


def server_type(request):
    """
    Add server type to template context.

    This allows templates to check which server they're on:
    {% if server_type == 'admin' %} ... {% endif %}
    {% if server_type == 'customer' %} ... {% endif %}
    """
    return {
        'server_type': getattr(settings, 'SERVER_TYPE', None)
    }


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
            'can_manage_featured': True,
            'can_moderate_reviews': True,
            'can_view_users': True,
            'can_manage_roles': True,
            'can_view_analytics': True,
            'can_export_data': True,
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
                'can_manage_featured': admin_role.can_manage_featured,
                'can_moderate_reviews': admin_role.can_moderate_reviews,
                'can_view_users': admin_role.can_view_users,
                'can_manage_roles': admin_role.can_manage_roles,
                'can_view_analytics': admin_role.can_view_analytics,
                'can_export_data': admin_role.can_export_data,
                'can_view_documentation': admin_role.can_view_documentation,
                'can_edit_documentation': admin_role.can_edit_documentation,
                'can_manage_faqs': admin_role.can_manage_faqs,
                'can_access_code_docs': admin_role.can_access_code_docs,
                'can_participate_dev_chat': admin_role.can_participate_dev_chat,
                'can_manage_versions': admin_role.can_manage_versions,
            }
        except AdminRole.DoesNotExist:
            # Staff without role - minimal permissions
            context['user_permissions'] = {
                'can_view_orders': False,
                'can_edit_orders': False,
                'can_process_refunds': False,
                'can_view_products': False,
                'can_edit_products': False,
                'can_manage_featured': False,
                'can_moderate_reviews': False,
                'can_view_users': False,
                'can_manage_roles': False,
                'can_view_analytics': False,
                'can_export_data': False,
                'can_view_documentation': False,
                'can_edit_documentation': False,
                'can_manage_faqs': False,
                'can_access_code_docs': False,
                'can_participate_dev_chat': False,
                'can_manage_versions': False,
            }
            context['user_role'] = 'Staff (No Role)'

    return context


def currency_context(request):
    """
    Add currency information to template context based on user's country.

    This allows templates to use:
    {{ currency_symbol }} -> '₹'
    {{ currency_code }} -> 'INR'
    {{ currency_name }} -> 'Indian Rupee'
    {{ user_country }} -> 'IN'
    """
    from apps.admin_panel.utils.currency import get_user_country, get_currency_info

    country = get_user_country(request)
    currency = get_currency_info(country)

    return {
        'user_country': country,
        'currency_symbol': currency['symbol'],
        'currency_code': currency['code'],
        'currency_name': currency['name'],
    }
