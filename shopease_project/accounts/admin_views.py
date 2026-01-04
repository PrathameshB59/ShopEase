# accounts/admin_views.py
"""
ADMIN DASHBOARD VIEWS
======================
Custom admin panel views for managing the e-commerce site.
Only accessible by users with 'ADMIN' role.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from functools import wraps

from .models import User
from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem


# ============================================================================
# DECORATOR: Role-based access control
# ============================================================================
def admin_required(view_func):
    """
    Decorator to ensure only ADMIN users can access the view.
    Checks if user is authenticated and has ADMIN role.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access admin panel.')
            return redirect('accounts:auth')
        
        # Check if user is admin
        if request.user.role != 'ADMIN' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        
        # User is admin, allow access
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ============================================================================
# ADMIN DASHBOARD - Main Overview
# ============================================================================
@admin_required
def admin_dashboard(request):
    """
    Main admin dashboard with statistics and overview.
    
    Shows:
    - Total sales, orders, products, users
    - Recent orders
    - Low stock alerts
    - Revenue charts
    """
    
    # Get date ranges for statistics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # ========== STATISTICS ==========
    
    # Total counts
    total_products = Product.objects.filter(is_active=True).count()
    total_users = User.objects.filter(role='CUSTOMER').count()
    total_orders = Order.objects.count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Orders this month
    orders_this_month = Order.objects.filter(
        created_at__gte=last_30_days
    ).count()
    
    # Revenue this month
    revenue_this_month = Order.objects.filter(
        created_at__gte=last_30_days,
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Pending orders
    pending_orders = Order.objects.filter(status='PENDING').count()
    
    # Low stock products (stock < low_stock_threshold)
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=10
    ).count()
    
    # ========== RECENT ORDERS ==========
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # ========== LOW STOCK ALERTS ==========
    low_stock_alerts = Product.objects.filter(
        is_active=True,
        stock__lte=10
    ).select_related('category').order_by('stock')[:10]
    
    # ========== TOP SELLING PRODUCTS ==========
    top_products = Product.objects.annotate(
        total_sold=Count('orderitem')
    ).filter(is_active=True).order_by('-total_sold')[:5]
    
    # ========== RECENT USERS ==========
    recent_users = User.objects.filter(role='CUSTOMER').order_by('-date_joined')[:5]
    
    # ========== ORDER STATUS BREAKDOWN ==========
    order_status_stats = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Context data
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_this_month': orders_this_month,
        'revenue_this_month': revenue_this_month,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'low_stock_alerts': low_stock_alerts,
        'top_products': top_products,
        'recent_users': recent_users,
        'order_status_stats': order_status_stats,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


# ============================================================================
# PRODUCT MANAGEMENT
# ============================================================================
@admin_required
def admin_products(request):
    """
    List all products with search and filter options.
    """
    products = Product.objects.select_related('category').prefetch_related('images')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    elif status_filter == 'low_stock':
        products = products.filter(stock__lte=10)
    
    # Order by
    products = products.order_by('-created_at')
    
    # Get all categories for filter
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin_panel/products.html', context)


# ============================================================================
# ORDER MANAGEMENT
# ============================================================================
@admin_required
def admin_orders(request):
    """
    List all orders with filter options.
    """
    orders = Order.objects.select_related('user').prefetch_related('items')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search by order number or customer
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(shipping_email__icontains=search_query)
        )
    
    # Order by newest first
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/orders.html', context)


@admin_required
def admin_order_detail(request, order_id):
    """
    View detailed information about a specific order.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), id=order_id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'admin_panel/order_detail.html', context)


@admin_required
def admin_update_order_status(request, order_id):
    """
    Update order status (AJAX endpoint).
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Validate status
        valid_statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED']
        if new_status in valid_statuses:
            order.status = new_status
            
            # Update shipped_at if status is SHIPPED
            if new_status == 'SHIPPED' and not order.shipped_at:
                order.shipped_at = timezone.now()
            
            # Update delivered_at if status is DELIVERED
            if new_status == 'DELIVERED' and not order.delivered_at:
                order.delivered_at = timezone.now()
            
            order.save()
            messages.success(request, f'Order {order.order_number} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('accounts:admin_order_detail', order_id=order_id)


# ============================================================================
# USER MANAGEMENT
# ============================================================================
@admin_required
def admin_users(request):
    """
    List all users with search and filter options.
    """
    users = User.objects.all()
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Search by username or email
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Order by newest first
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/users.html', context)


# ============================================================================
# CATEGORY MANAGEMENT
# ============================================================================
@admin_required
def admin_categories(request):
    """
    List all categories.
    """
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('order', 'name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin_panel/categories.html', context)


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================
@admin_required
def admin_analytics(request):
    """
    Analytics and reports page.
    Shows sales trends, revenue charts, etc.
    """
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Revenue by day (last 30 days)
    daily_revenue = []
    for i in range(30):
        date = today - timedelta(days=i)
        revenue = Order.objects.filter(
            created_at__date=date,
            status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue)
        })
    
    daily_revenue.reverse()
    
    # Orders by day (last 30 days)
    daily_orders = []
    for i in range(30):
        date = today - timedelta(days=i)
        count = Order.objects.filter(created_at__date=date).count()
        
        daily_orders.append({
            'date': date.strftime('%Y-%m-%d'),
            'orders': count
        })
    
    daily_orders.reverse()
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Count('orderitem'),
        revenue=Sum('orderitem__total_price')
    ).filter(is_active=True).order_by('-total_sold')[:10]
    
    # Category sales distribution
    category_sales = Category.objects.annotate(
        total_sales=Sum('product__orderitem__total_price')
    ).filter(total_sales__isnull=False).order_by('-total_sales')
    
    context = {
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'top_products': top_products,
        'category_sales': category_sales,
    }
    
    return render(request, 'admin_panel/analytics.html', context)


# ============================================================================
# SETTINGS
# ============================================================================
@admin_required
def admin_settings(request):
    """
    Admin settings page.
    """
    if request.method == 'POST':
        # Handle settings update
        messages.success(request, 'Settings updated successfully!')
        return redirect('accounts:admin_settings')
    
    context = {}
    
    return render(request, 'admin_panel/settings.html', context)