"""
========================================
PRODUCT ANALYTICS VIEWS
========================================

Views for managing product analytics and featured products.

Includes:
- Product analytics list with metrics
- Featured products dashboard
- Auto-suggest featured products (API)
- Manual featured product management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta, date

from apps.admin_panel.decorators import admin_required, permission_required
from apps.admin_panel.models import (
    ProductAnalytics,
    FeaturedProduct,
    ProductView,
    ProductEngagement
)
from apps.products.models import Product
from apps.orders.models import OrderItem


@permission_required('can_view_analytics')
def product_analytics_list(request):
    """
    Display list of all products with their analytics metrics.

    Shows aggregated metrics for each product with filtering and sorting.
    """
    # Date range filter
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Get all active products
    products = Product.objects.filter(is_active=True)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category_id=category)

    # Aggregate analytics for each product
    product_data = []
    for product in products:
        analytics = ProductAnalytics.objects.filter(
            product=product,
            date__range=[start_date, end_date]
        ).aggregate(
            total_views=Sum('view_count'),
            total_unique_viewers=Sum('unique_viewers'),
            total_cart_adds=Sum('add_to_cart_count'),
            total_wishlist=Sum('wishlist_count'),
            total_purchases=Sum('purchase_count'),
            total_revenue=Sum('revenue'),
            avg_rating=Avg('average_rating'),
            avg_featured_score=Avg('featured_score')
        )

        # Get latest featured score
        latest_analytics = ProductAnalytics.objects.filter(
            product=product
        ).order_by('-date').first()

        product_data.append({
            'product': product,
            'views': analytics['total_views'] or 0,
            'unique_viewers': analytics['total_unique_viewers'] or 0,
            'cart_adds': analytics['total_cart_adds'] or 0,
            'wishlist': analytics['total_wishlist'] or 0,
            'purchases': analytics['total_purchases'] or 0,
            'revenue': analytics['total_revenue'] or 0,
            'avg_rating': analytics['avg_rating'] or 0,
            'featured_score': latest_analytics.featured_score if latest_analytics else 0,
            'conversion_rate': (
                (analytics['total_purchases'] or 0) / (analytics['total_views'] or 1) * 100
            ) if analytics['total_views'] else 0
        })

    # Sort by featured score by default
    sort_by = request.GET.get('sort', 'featured_score')
    reverse = request.GET.get('order', 'desc') == 'desc'

    if sort_by in ['views', 'purchases', 'revenue', 'featured_score', 'conversion_rate']:
        product_data.sort(key=lambda x: x[sort_by], reverse=reverse)

    # Pagination
    paginator = Paginator(product_data, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get categories for filter
    from apps.products.models import Category
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'days': days,
        'sort_by': sort_by,
        'order': request.GET.get('order', 'desc'),
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    }

    return render(request, 'admin_panel/products/analytics_list.html', context)


@permission_required('can_view_analytics')
def featured_products_dashboard(request):
    """
    Analytics dashboard for featured products.

    Shows:
    - Top products by featured score
    - Current featured products performance
    - Metrics comparison
    - Trending products
    """
    today = timezone.now().date()

    # Top 10 products by featured score (last 7 days)
    last_week = today - timedelta(days=7)
    top_products = ProductAnalytics.objects.filter(
        date__gte=last_week
    ).values('product').annotate(
        avg_score=Avg('featured_score'),
        total_revenue=Sum('revenue'),
        total_purchases=Sum('purchase_count'),
        total_views=Sum('view_count')
    ).order_by('-avg_score')[:10]

    # Enhance with product details
    top_products_data = []
    for item in top_products:
        product = Product.objects.get(id=item['product'])
        top_products_data.append({
            'product': product,
            'avg_score': round(item['avg_score'], 2),
            'total_revenue': item['total_revenue'],
            'total_purchases': item['total_purchases'],
            'total_views': item['total_views']
        })

    # Currently featured products
    current_featured = FeaturedProduct.objects.filter(
        is_active=True,
        created_at__lte=today
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=today)
    ).select_related('product').order_by('priority')

    # Performance of current featured products
    featured_performance = []
    for featured in current_featured:
        analytics = ProductAnalytics.objects.filter(
            product=featured.product,
            date__gte=featured.created_at,
            date__lte=today
        ).aggregate(
            total_views=Sum('view_count'),
            total_purchases=Sum('purchase_count'),
            total_revenue=Sum('revenue'),
            avg_score=Avg('featured_score')
        )

        featured_performance.append({
            'featured': featured,
            'analytics': analytics
        })

    # Trending products (biggest score increase in last 7 days)
    trending = []
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    for product in Product.objects.filter(is_active=True)[:50]:  # Sample top 50
        recent_score = ProductAnalytics.objects.filter(
            product=product,
            date__gte=week_ago
        ).aggregate(avg=Avg('featured_score'))['avg'] or 0

        previous_score = ProductAnalytics.objects.filter(
            product=product,
            date__gte=two_weeks_ago,
            date__lt=week_ago
        ).aggregate(avg=Avg('featured_score'))['avg'] or 0

        if previous_score > 0:
            score_change = ((recent_score - previous_score) / previous_score) * 100
            if score_change > 0:
                trending.append({
                    'product': product,
                    'score_change': round(score_change, 2),
                    'recent_score': round(recent_score, 2),
                    'previous_score': round(previous_score, 2)
                })

    trending.sort(key=lambda x: x['score_change'], reverse=True)
    trending = trending[:10]  # Top 10 trending

    # Overall stats
    total_featured = current_featured.count()
    auto_featured = current_featured.filter(source='AUTO').count()
    manual_featured = current_featured.filter(source='MANUAL').count()

    context = {
        'top_products': top_products_data,
        'featured_performance': featured_performance,
        'trending': trending,
        'total_featured': total_featured,
        'auto_featured': auto_featured,
        'manual_featured': manual_featured,
        'last_week': last_week,
        'today': today
    }

    return render(request, 'admin_panel/products/featured_dashboard.html', context)


@permission_required('can_view_analytics')
def auto_suggest_featured(request):
    """
    API endpoint that returns auto-suggested products for featuring.

    Returns top products by featured score that aren't already featured.
    Used for AJAX calls from management interface.
    """
    # Get top products by featured score (last 7 days average)
    days = int(request.GET.get('days', 7))
    limit = int(request.GET.get('limit', 10))

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Get products with analytics
    suggested = ProductAnalytics.objects.filter(
        date__gte=start_date
    ).values('product').annotate(
        avg_score=Avg('featured_score'),
        total_revenue=Sum('revenue'),
        total_purchases=Sum('purchase_count'),
        total_views=Sum('view_count')
    ).order_by('-avg_score')

    # Filter out already featured products
    currently_featured_ids = FeaturedProduct.objects.filter(
        is_active=True,
        created_at__lte=end_date
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=end_date)
    ).values_list('product_id', flat=True)

    suggested = suggested.exclude(product__in=currently_featured_ids)[:limit]

    # Build response
    suggestions = []
    for item in suggested:
        product = Product.objects.get(id=item['product'])
        suggestions.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.price),
            'stock': product.stock,
            'featured_score': round(item['avg_score'], 2),
            'revenue': float(item['total_revenue']),
            'purchases': item['total_purchases'],
            'views': item['total_views'],
            'image_url': product.images.first().image.url if product.images.first() else None
        })

    return JsonResponse({
        'success': True,
        'suggestions': suggestions,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    })


@permission_required('can_manage_featured')
def manage_featured_products(request):
    """
    Manage featured products - add, remove, reorder.

    Handles both manual selection and auto-suggestions.
    """
    today = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_manual':
            # Add product manually
            product_id = request.POST.get('product_id')
            priority = request.POST.get('priority', 0)
            reason = request.POST.get('reason', '')
            end_date = request.POST.get('end_date', None)

            try:
                product = Product.objects.get(id=product_id)

                # Check if already featured
                existing = FeaturedProduct.objects.filter(
                    product=product,
                    is_active=True,
                    created_at__lte=today
                ).filter(
                    Q(expires_at__isnull=True) | Q(expires_at__gte=today)
                )

                if existing.exists():
                    messages.warning(request, f'{product.name} is already featured.')
                else:
                    FeaturedProduct.objects.create(
                        product=product,
                        source='MANUAL',
                        priority=priority,
                        reason=reason,
                        expires_at=end_date if end_date else None,
                        is_active=True
                    )
                    messages.success(request, f'Added {product.name} to featured products.')

            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')

        elif action == 'add_auto':
            # Add auto-suggested product
            product_id = request.POST.get('product_id')

            try:
                product = Product.objects.get(id=product_id)

                # Get latest analytics for reason
                analytics = ProductAnalytics.objects.filter(
                    product=product
                ).order_by('-date').first()

                reason = f"Auto-suggested (Score: {analytics.featured_score if analytics else 'N/A'})"

                FeaturedProduct.objects.create(
                    product=product,
                    source='AUTO',
                    priority=0,
                    reason=reason,
                    expires_at=None,
                    is_active=True
                )
                messages.success(request, f'Added {product.name} to featured products (auto).')

            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')

        elif action == 'remove':
            # Remove/deactivate featured product
            featured_id = request.POST.get('featured_id')

            try:
                featured = FeaturedProduct.objects.get(id=featured_id)
                featured.is_active = False
                featured.expires_at = today
                featured.save(update_fields=['is_active', 'expires_at'])

                messages.success(request, f'Removed {featured.product.name} from featured products.')

            except FeaturedProduct.DoesNotExist:
                messages.error(request, 'Featured product not found.')

        elif action == 'update_priority':
            # Update priorities (bulk)
            priorities = request.POST.getlist('priority')
            featured_ids = request.POST.getlist('featured_id')

            for featured_id, priority in zip(featured_ids, priorities):
                try:
                    featured = FeaturedProduct.objects.get(id=featured_id)
                    featured.priority = int(priority)
                    featured.save(update_fields=['priority'])
                except (FeaturedProduct.DoesNotExist, ValueError):
                    pass

            messages.success(request, 'Updated featured product priorities.')

        return redirect('admin_panel:manage_featured_products')

    # GET request - show management interface

    # Currently featured products
    current_featured = FeaturedProduct.objects.filter(
        is_active=True,
        created_at__lte=today
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=today)
    ).select_related('product').order_by('priority')

    # Get auto-suggestions (top 10 not currently featured)
    auto_suggestions = []
    suggested_data = auto_suggest_featured(request)  # Reuse API endpoint

    # All active products for manual selection
    all_products = Product.objects.filter(is_active=True).order_by('name')

    context = {
        'current_featured': current_featured,
        'all_products': all_products,
        'today': today
    }

    return render(request, 'admin_panel/products/manage_featured.html', context)


@permission_required('can_view_analytics')
def product_analytics_detail(request, product_id):
    """
    Detailed analytics view for a single product.

    Shows time-series data, engagement metrics, and trends.
    """
    product = get_object_or_404(Product, id=product_id)

    # Date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Get analytics for date range
    analytics = ProductAnalytics.objects.filter(
        product=product,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Aggregate totals
    totals = analytics.aggregate(
        total_views=Sum('view_count'),
        total_unique_viewers=Sum('unique_viewers'),
        total_cart_adds=Sum('add_to_cart_count'),
        total_wishlist=Sum('wishlist_count'),
        total_purchases=Sum('purchase_count'),
        total_revenue=Sum('revenue'),
        avg_rating=Avg('average_rating'),
        avg_score=Avg('featured_score')
    )

    # Prepare chart data
    chart_data = {
        'dates': [a.date.isoformat() for a in analytics],
        'views': [a.view_count for a in analytics],
        'purchases': [a.purchase_count for a in analytics],
        'revenue': [float(a.revenue) for a in analytics],
        'featured_score': [float(a.featured_score) for a in analytics]
    }

    # Check if currently featured
    is_featured = FeaturedProduct.objects.filter(
        product=product,
        is_active=True,
        created_at__lte=end_date
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=end_date)
    ).exists()

    # Calculate conversion rates
    total_views = totals['total_views'] or 0
    total_purchases = totals['total_purchases'] or 0
    total_cart_adds = totals['total_cart_adds'] or 0

    conversion_rate = (total_purchases / total_views * 100) if total_views > 0 else 0
    cart_rate = (total_cart_adds / total_views * 100) if total_views > 0 else 0

    context = {
        'product': product,
        'totals': totals,
        'chart_data': chart_data,
        'is_featured': is_featured,
        'days': days,
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'conversion_rate': round(conversion_rate, 2),
        'cart_rate': round(cart_rate, 1),
    }

    return render(request, 'admin_panel/products/analytics_detail.html', context)


# ========================================
# PRODUCT CRUD VIEWS
# ========================================

from apps.products.models import Category


@permission_required('can_view_products')
def product_list(request):
    """
    List all products with search, filters, and pagination.
    """
    products = Product.objects.select_related('category').all()

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)

    # Status filter
    status = request.GET.get('status', '')
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)

    # Stock filter
    stock_status = request.GET.get('stock', '')
    if stock_status == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock=0)
    elif stock_status == 'low_stock':
        products = products.filter(stock__gt=0, stock__lte=10)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['name', '-name', 'price', '-price', 'stock', '-stock', 'created_at', '-created_at']:
        products = products.order_by(sort_by)

    # Pagination
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get categories for filter dropdown
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status,
        'selected_stock': stock_status,
        'sort_by': sort_by,
        'total_products': products.count(),
    }

    return render(request, 'admin_panel/products/list.html', context)


@permission_required('can_edit_products')
def product_create(request):
    """
    Create a new product.
    """
    from apps.admin_panel.forms import ProductForm

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('admin_panel:product_list')
    else:
        form = ProductForm()

    categories = Category.objects.filter(is_active=True)

    context = {
        'form': form,
        'categories': categories,
    }

    return render(request, 'admin_panel/products/create.html', context)


@permission_required('can_view_products')
def product_detail(request, product_id):
    """
    View and edit product details.
    """
    from apps.admin_panel.forms import ProductForm

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Check edit permission for POST
        if not request.user.is_superuser:
            try:
                admin_role = request.user.admin_role
                if not admin_role.can_edit_products:
                    messages.error(request, 'You do not have permission to edit products.')
                    return redirect('admin_panel:product_detail', product_id=product_id)
            except:
                messages.error(request, 'You do not have permission to edit products.')
                return redirect('admin_panel:product_detail', product_id=product_id)

        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('admin_panel:product_detail', product_id=product_id)
    else:
        form = ProductForm(instance=product)

    # Get product analytics summary
    analytics_summary = ProductAnalytics.objects.filter(
        product=product
    ).aggregate(
        total_views=Sum('view_count'),
        total_purchases=Sum('purchase_count'),
        total_revenue=Sum('revenue'),
    )

    categories = Category.objects.filter(is_active=True)

    context = {
        'product': product,
        'form': form,
        'categories': categories,
        'analytics_summary': analytics_summary,
    }

    return render(request, 'admin_panel/products/detail.html', context)


@permission_required('can_edit_products')
def product_update(request, product_id):
    """
    Update product (POST only, redirects to detail).
    """
    from apps.admin_panel.forms import ProductForm

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return redirect('admin_panel:product_detail', product_id=product_id)


@permission_required('can_edit_products')
def product_delete(request, product_id):
    """
    Delete a product (soft delete by setting is_active=False).
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        action = request.POST.get('action', 'deactivate')

        if action == 'permanent':
            product_name = product.name
            product.delete()
            messages.success(request, f'Product "{product_name}" has been permanently deleted.')
        else:
            # Soft delete - just deactivate
            product.is_active = False
            product.save(update_fields=['is_active'])
            messages.success(request, f'Product "{product.name}" has been deactivated.')

        return redirect('admin_panel:product_list')

    context = {
        'product': product,
    }

    return render(request, 'admin_panel/products/delete_confirm.html', context)


@permission_required('can_edit_products')
def product_bulk_action(request):
    """
    Handle bulk actions on products (activate, deactivate, delete).
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        product_ids = request.POST.getlist('product_ids')

        if not product_ids:
            messages.warning(request, 'No products selected.')
            return redirect('admin_panel:product_list')

        products = Product.objects.filter(id__in=product_ids)
        count = products.count()

        if action == 'activate':
            products.update(is_active=True)
            messages.success(request, f'{count} product(s) activated successfully.')

        elif action == 'deactivate':
            products.update(is_active=False)
            messages.success(request, f'{count} product(s) deactivated successfully.')

        elif action == 'feature':
            products.update(is_featured=True)
            messages.success(request, f'{count} product(s) marked as featured.')

        elif action == 'unfeature':
            products.update(is_featured=False)
            messages.success(request, f'{count} product(s) removed from featured.')

        elif action == 'delete':
            products.delete()
            messages.success(request, f'{count} product(s) permanently deleted.')

    return redirect('admin_panel:product_list')
