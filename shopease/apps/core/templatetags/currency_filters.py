"""
========================================
CURRENCY TEMPLATE FILTERS (CUSTOMER SIDE)
========================================

Template filters for formatting currency displays in customer-facing pages.
"""

from django import template

register = template.Library()


@register.filter
def currency_format(value, currency_symbol='₹'):
    """
    Format a numeric value with currency symbol.

    Usage:
        {{ price|currency_format }}
        {{ price|currency_format:currency_symbol }}

    Args:
        value: Numeric value to format
        currency_symbol: Currency symbol to use (default: ₹)

    Returns:
        str: Formatted currency string (e.g., '₹1,234.56')
    """
    try:
        return f"{currency_symbol}{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


@register.filter
def currency_code(country_code):
    """
    Get currency code for a country.

    Usage:
        {{ 'IN'|currency_code }}  -> 'INR'

    Args:
        country_code: Two-letter country code

    Returns:
        str: Currency code (e.g., 'INR', 'USD')
    """
    from apps.admin_panel.utils.currency import get_currency_info

    currency_info = get_currency_info(country_code)
    return currency_info.get('code', 'INR')


@register.filter
def currency_symbol(country_code):
    """
    Get currency symbol for a country.

    Usage:
        {{ 'US'|currency_symbol }}  -> '$'

    Args:
        country_code: Two-letter country code

    Returns:
        str: Currency symbol (e.g., '₹', '$', '£')
    """
    from apps.admin_panel.utils.currency import get_currency_info

    currency_info = get_currency_info(country_code)
    return currency_info.get('symbol', '₹')
