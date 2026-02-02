"""
========================================
DASHBOARD VIEW
========================================

Main dashboard view for the custom admin panel.

Displays:
- Key performance indicators (KPIs)
- Recent orders
- Low stock alerts
- Recent admin activity

Access: All staff users with admin_required decorator
"""

from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from apps.admin_panel.decorators import admin_required
from apps.admin_panel.models import AdminActivity
from apps.orders.models import Order
from apps.products.models import Product
from apps.accounts.models import Profile


@admin_required
def dashboard_view(request):
    """
    Main admin dashboard with overview statistics.

    Shows:
    - Today's orders and revenue
    - Pending orders count
    - Low stock products
    - Recent admin activities

    Access: All staff users
    """

    # Get current user's role info if exists
    user_role = None
    user_permissions = {}
    if hasattr(request.user, 'admin_role'):
        user_role = request.user.admin_role
        # Get all permissions for template
        user_permissions = {
            'can_view_orders': user_role.can_view_orders,
            'can_edit_orders': user_role.can_edit_orders,
            'can_process_refunds': user_role.can_process_refunds,
            'can_view_products': user_role.can_view_products,
            'can_edit_products': user_role.can_edit_products,
            'can_manage_featured': user_role.can_manage_featured,
            'can_moderate_reviews': user_role.can_moderate_reviews,
            'can_view_users': user_role.can_view_users,
            'can_manage_roles': user_role.can_manage_roles,
            'can_view_analytics': user_role.can_view_analytics,
            'can_export_data': user_role.can_export_data,
        }

    # Calculate date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Order statistics
    today_orders = Order.objects.filter(created_at__date=today)
    today_orders_count = today_orders.count()
    today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Pending orders
    pending_orders_count = Order.objects.filter(
        status__in=['PENDING', 'PROCESSING']
    ).count()

    # Low stock products (stock < 10)
    low_stock_products = Product.objects.filter(
        stock__lt=10,
        is_active=True
    ).order_by('stock')[:5]

    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Recent admin activities (last 10)
    recent_activities = AdminActivity.objects.select_related('user').order_by('-timestamp')[:10]

    # Total stats (for display)
    total_products = Product.objects.filter(is_active=True).count()
    total_customers = Profile.objects.count()

    context = {
        'user_role': user_role,
        'user_permissions': user_permissions,

        # Today's stats
        'today_orders_count': today_orders_count,
        'today_revenue': today_revenue,
        'pending_orders_count': pending_orders_count,

        # Lists
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'recent_activities': recent_activities,

        # Totals
        'total_products': total_products,
        'total_customers': total_customers,
    }

    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
@admin_required
def database_status(request):
    """
    Display database connection status and statistics.
    Only accessible to superusers for security reasons.
    """
    from apps.admin_panel.utils.database_health import get_db_status, get_db_statistics
    from apps.admin_panel.decorators import role_required

    # Only superusers can view database status
    if not request.user.is_superuser:
        from django.contrib import messages
        messages.error(request, 'Only superusers can view database status.')
        return render(request, 'admin_panel/access_denied.html', status=403)

    # Get database status
    db_status = get_db_status()

    # Get statistics only if connected
    db_stats = {}
    if db_status.get('connected'):
        db_stats = get_db_statistics()

    context = {
        'db_status': db_status,
        'db_stats': db_stats,
    }

    return render(request, 'admin_panel/database_status.html', context)


def set_currency(request):
    """
    Handle currency selection from navbar dropdown.
    Stores user's currency preference in session.
    """
    from django.http import HttpResponseRedirect

    # Get currency code from query parameter
    currency_code = request.GET.get('set_currency', 'IN')

    # Store in session
    request.session['preferred_country'] = currency_code.upper()

    # Redirect to referer or homepage
    referer = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(referer)
