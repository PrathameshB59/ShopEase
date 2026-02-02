"""
========================================
REPORTS & ANALYTICS VIEWS
========================================

Views for generating sales reports and analytics.

Includes:
- Sales reports with date range filters
- Revenue analytics and breakdowns
- Product performance reports
- CSV export functionality
"""

import csv
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.http import HttpResponse
from datetime import timedelta, date
from decimal import Decimal

from apps.admin_panel.decorators import admin_required, permission_required
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Review
from apps.admin_panel.models import ProductAnalytics


@permission_required('can_view_analytics')
def sales_report(request):
    """
    Comprehensive sales report with date range filtering.

    Shows:
    - Sales metrics (orders, revenue, AOV)
    - Sales by status
    - Daily sales chart
    - Top products
    - Payment method breakdown
    """
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Default to last 30 days
    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        date_from = start_date.isoformat()
        date_to = end_date.isoformat()
    else:
        try:
            start_date = date.fromisoformat(date_from)
            end_date = date.fromisoformat(date_to)
        except ValueError:
            messages.error(request, 'Invalid date format.')
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            date_from = start_date.isoformat()
            date_to = end_date.isoformat()

    # Get orders in date range
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )

    # Overall metrics
    total_orders = orders.count()
    completed_orders = orders.filter(status='COMPLETED').count()
    pending_orders = orders.filter(status='PENDING').count()
    cancelled_orders = orders.filter(status='CANCELLED').count()

    total_revenue = orders.filter(status='COMPLETED').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    average_order_value = (total_revenue / completed_orders) if completed_orders > 0 else Decimal('0.00')

    # Sales by status
    status_breakdown = []
    for status_code, status_label in Order.STATUS_CHOICES:
        count = orders.filter(status=status_code).count()
        revenue = orders.filter(status=status_code).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')

        status_breakdown.append({
            'status': status_label,
            'count': count,
            'revenue': revenue
        })

    # Daily sales (for chart)
    from django.db.models.functions import TruncDate
    daily_sales = orders.filter(status='COMPLETED').annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        order_count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('day')

    chart_data = {
        'dates': [item['day'].isoformat() for item in daily_sales],
        'order_counts': [item['order_count'] for item in daily_sales],
        'revenues': [float(item['revenue']) for item in daily_sales]
    }

    # Top products by revenue
    top_products_revenue = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).values('product__name', 'product_id').annotate(
        total_revenue=Sum(F('price') * F('quantity')),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')[:10]

    # Top products by quantity
    top_products_quantity = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).values('product__name', 'product_id').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_quantity')[:10]

    # Payment method breakdown
    payment_breakdown = orders.filter(status='COMPLETED').values(
        'payment_method'
    ).annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-revenue')

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'start_date': start_date,
        'end_date': end_date,
        'metrics': {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'average_order_value': average_order_value
        },
        'status_breakdown': status_breakdown,
        'chart_data': chart_data,
        'top_products_revenue': top_products_revenue,
        'top_products_quantity': top_products_quantity,
        'payment_breakdown': payment_breakdown
    }

    return render(request, 'admin_panel/reports/sales.html', context)


@permission_required('can_view_analytics')
def revenue_report(request):
    """
    Revenue analytics with detailed breakdowns.

    Shows:
    - Revenue by category
    - Revenue by month
    - Revenue trends
    - Revenue forecasting (simple)
    """
    # Date range
    months = int(request.GET.get('months', 6))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30 * months)

    # Revenue by category
    from apps.products.models import Category
    revenue_by_category = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).values('product__category__name').annotate(
        total_revenue=Sum(F('price') * F('quantity')),
        order_count=Count('order', distinct=True),
        product_count=Count('product', distinct=True)
    ).order_by('-total_revenue')

    # Monthly revenue
    from django.db.models.functions import TruncMonth
    monthly_revenue = Order.objects.filter(
        status='COMPLETED',
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        order_count=Count('id'),
        avg_order_value=Avg('total_amount')
    ).order_by('month')

    # Chart data
    chart_data = {
        'months': [item['month'].strftime('%B %Y') for item in monthly_revenue],
        'revenues': [float(item['revenue']) for item in monthly_revenue],
        'order_counts': [item['order_count'] for item in monthly_revenue],
        'avg_values': [float(item['avg_order_value']) for item in monthly_revenue]
    }

    # Total metrics
    total_revenue = Order.objects.filter(
        status='COMPLETED',
        created_at__date__gte=start_date
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    total_orders = Order.objects.filter(
        status='COMPLETED',
        created_at__date__gte=start_date
    ).count()

    # Growth calculation (compare to previous period)
    previous_start = start_date - timedelta(days=30 * months)
    previous_revenue = Order.objects.filter(
        status='COMPLETED',
        created_at__date__gte=previous_start,
        created_at__date__lt=start_date
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    if previous_revenue > 0:
        growth_rate = ((total_revenue - previous_revenue) / previous_revenue) * 100
    else:
        growth_rate = 0

    context = {
        'months': months,
        'start_date': start_date,
        'end_date': end_date,
        'revenue_by_category': revenue_by_category,
        'monthly_revenue': monthly_revenue,
        'chart_data': chart_data,
        'metrics': {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'previous_revenue': previous_revenue,
            'growth_rate': round(growth_rate, 2)
        }
    }

    return render(request, 'admin_panel/reports/revenue.html', context)


@permission_required('can_view_analytics')
def product_performance(request):
    """
    Product performance report.

    Shows:
    - Best selling products
    - Worst performing products
    - Stock analysis
    - Product ratings
    """
    # Date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Best sellers
    best_sellers = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__date__gte=start_date
    ).values(
        'product__name', 'product__sku', 'product_id'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity')),
        order_count=Count('order', distinct=True)
    ).order_by('-units_sold')[:20]

    # Low stock products
    low_stock = Product.objects.filter(
        is_active=True,
        stock__lt=10
    ).order_by('stock')[:20]

    # Out of stock
    out_of_stock = Product.objects.filter(
        is_active=True,
        stock=0
    ).count()

    # Products with no sales
    no_sales = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=OrderItem.objects.filter(
            order__status='COMPLETED',
            order__created_at__date__gte=start_date
        ).values_list('product_id', flat=True)
    ).count()

    # Top rated products
    top_rated = Product.objects.filter(
        is_active=True,
        reviews__is_approved=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gte=3).order_by('-avg_rating')[:10]

    # Low rated products
    low_rated = Product.objects.filter(
        is_active=True,
        reviews__is_approved=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gte=3).order_by('avg_rating')[:10]

    context = {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'best_sellers': best_sellers,
        'low_stock': low_stock,
        'out_of_stock_count': out_of_stock,
        'no_sales_count': no_sales,
        'top_rated': top_rated,
        'low_rated': low_rated
    }

    return render(request, 'admin_panel/reports/product_performance.html', context)


@permission_required('can_view_analytics')
def export_sales_csv(request):
    """
    Export sales data to CSV.

    Includes all orders with details.
    """
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if date_from and date_to:
        try:
            start_date = date.fromisoformat(date_from)
            end_date = date.fromisoformat(date_to)
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

    # Get orders
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('user').order_by('-created_at')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow([
        'Order ID',
        'Date',
        'Customer',
        'Email',
        'Status',
        'Payment Method',
        'Total Amount',
        'Items Count',
        'Shipping Address'
    ])

    # Data rows
    for order in orders:
        writer.writerow([
            str(order.order_id)[:8],
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.shipping_full_name,
            order.shipping_email,
            order.get_status_display(),
            order.payment_method,
            f'{order.total_amount:.2f}',
            order.items.count(),
            f'{order.shipping_address_line1}, {order.shipping_city}, {order.shipping_country}'
        ])

    return response


@permission_required('can_view_analytics')
def export_products_csv(request):
    """
    Export product performance data to CSV.
    """
    # Date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Get product data
    products = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__date__gte=start_date
    ).values(
        'product__name',
        'product__sku',
        'product__price',
        'product__stock'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity')),
        order_count=Count('order', distinct=True)
    ).order_by('-revenue')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="product_performance_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow([
        'Product Name',
        'SKU',
        'Current Price',
        'Current Stock',
        'Units Sold',
        'Revenue',
        'Orders',
        'Avg per Order'
    ])

    # Data rows
    for product in products:
        avg_per_order = product['units_sold'] / product['order_count'] if product['order_count'] > 0 else 0
        writer.writerow([
            product['product__name'],
            product['product__sku'],
            f'{product["product__price"]:.2f}',
            product['product__stock'],
            product['units_sold'],
            f'{product["revenue"]:.2f}',
            product['order_count'],
            f'{avg_per_order:.2f}'
        ])

    return response


@permission_required('can_view_analytics')
def dashboard_overview(request):
    """
    Executive dashboard with key metrics.

    Quick overview of entire business.
    """
    today = timezone.now().date()

    # Today's metrics
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.filter(status='COMPLETED').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    # This month
    month_start = today.replace(day=1)
    month_orders = Order.objects.filter(created_at__date__gte=month_start)
    month_revenue = month_orders.filter(status='COMPLETED').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    # All time
    total_customers = Order.objects.values('user').distinct().count()
    total_products = Product.objects.filter(is_active=True).count()
    total_revenue = Order.objects.filter(status='COMPLETED').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    # Pending items
    pending_orders = Order.objects.filter(status__in=['PENDING', 'PROCESSING']).count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    low_stock = Product.objects.filter(is_active=True, stock__lt=10).count()

    context = {
        'today': today,
        'today_metrics': {
            'orders': today_orders.count(),
            'revenue': today_revenue
        },
        'month_metrics': {
            'orders': month_orders.count(),
            'revenue': month_revenue
        },
        'totals': {
            'customers': total_customers,
            'products': total_products,
            'revenue': total_revenue
        },
        'pending': {
            'orders': pending_orders,
            'reviews': pending_reviews,
            'low_stock': low_stock
        }
    }

    return render(request, 'admin_panel/reports/dashboard_overview.html', context)
