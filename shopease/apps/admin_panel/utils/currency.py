"""
========================================
CURRENCY UTILITY
========================================

Utilities for country-based currency detection and display.
Supports multiple currencies with symbols, tax rates, and formatting.
"""

# Currency mapping by country code
CURRENCY_MAP = {
    'IN': {'code': 'INR', 'symbol': '₹', 'name': 'Indian Rupee'},
    'US': {'code': 'USD', 'symbol': '$', 'name': 'US Dollar'},
    'GB': {'code': 'GBP', 'symbol': '£', 'name': 'British Pound'},
    'DE': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'FR': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'IT': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'ES': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'JP': {'code': 'JPY', 'symbol': '¥', 'name': 'Japanese Yen'},
    'CN': {'code': 'CNY', 'symbol': '¥', 'name': 'Chinese Yuan'},
    'AU': {'code': 'AUD', 'symbol': 'A$', 'name': 'Australian Dollar'},
    'CA': {'code': 'CAD', 'symbol': 'C$', 'name': 'Canadian Dollar'},
    'BR': {'code': 'BRL', 'symbol': 'R$', 'name': 'Brazilian Real'},
    'MX': {'code': 'MXN', 'symbol': '$', 'name': 'Mexican Peso'},
    'ZA': {'code': 'ZAR', 'symbol': 'R', 'name': 'South African Rand'},
}

# Tax rate mapping by country code
TAX_RATE_MAP = {
    'IN': 0.18,  # 18% GST
    'US': 0.07,  # 7% average sales tax
    'GB': 0.20,  # 20% VAT
    'DE': 0.19,  # 19% VAT
    'FR': 0.20,  # 20% VAT
    'IT': 0.22,  # 22% VAT
    'ES': 0.21,  # 21% VAT
    'JP': 0.10,  # 10% consumption tax
    'CN': 0.13,  # 13% VAT
    'AU': 0.10,  # 10% GST
    'CA': 0.13,  # 13% HST (Ontario average)
    'BR': 0.17,  # 17% average
    'MX': 0.16,  # 16% IVA
    'ZA': 0.15,  # 15% VAT
}


def get_user_country(request):
    """
    Detect user's country from their profile or session.

    Priority:
    1. Session preference (user override)
    2. User profile (shipping or billing country)
    3. Default to India

    Args:
        request: Django request object

    Returns:
        str: Two-letter country code (e.g., 'IN', 'US')
    """
    # Check session first (user can override)
    if 'preferred_country' in request.session:
        return request.session['preferred_country']

    # Check authenticated user's profile
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            # Try shipping country first, then billing country
            if hasattr(profile, 'shipping_country') and profile.shipping_country:
                return profile.shipping_country
            if hasattr(profile, 'billing_country') and profile.billing_country:
                return profile.billing_country
        except:
            pass

    # Default to India
    return 'IN'


def get_currency_info(country_code):
    """
    Get currency information for a given country code.

    Args:
        country_code: Two-letter country code (e.g., 'IN', 'US')

    Returns:
        dict: Currency information with code, symbol, and name
    """
    return CURRENCY_MAP.get(country_code.upper(), CURRENCY_MAP['IN'])


def get_tax_rate(country_code):
    """
    Get tax rate for a given country.

    Args:
        country_code: Two-letter country code (e.g., 'IN', 'US')

    Returns:
        float: Tax rate as decimal (e.g., 0.18 for 18%)
    """
    return TAX_RATE_MAP.get(country_code.upper(), TAX_RATE_MAP['IN'])


def format_currency(amount, currency_symbol='₹'):
    """
    Format amount with currency symbol.

    Args:
        amount: Numeric amount to format
        currency_symbol: Currency symbol to use

    Returns:
        str: Formatted currency string (e.g., '₹1,234.56')
    """
    try:
        return f"{currency_symbol}{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


def get_all_currencies():
    """
    Get list of all supported currencies for dropdown.

    Returns:
        list: List of dicts with country_code, currency_code, symbol, name
    """
    currencies = {}
    for country_code, info in CURRENCY_MAP.items():
        currency_code = info['code']
        if currency_code not in currencies:
            currencies[currency_code] = {
                'country_code': country_code,
                'currency_code': currency_code,
                'symbol': info['symbol'],
                'name': info['name'],
            }

    return list(currencies.values())
