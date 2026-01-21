"""
========================================
CORE CONTEXT PROCESSORS
========================================

Context processors to provide core data to customer-facing templates.
"""

from django.conf import settings


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
