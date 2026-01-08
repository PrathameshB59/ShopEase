from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from .models import Product, Category


def product_list(request):
    """
    Display products with search, filters, and sorting.
    
    CRITICAL: This function MUST filter products based on search query.
    The issue is: If products queryset isn't filtered, all products show.
    
    URL Examples:
        /products/ → All products
        /products/?q=jacket → Only products matching "jacket"
        /products/?q=jacket&category=mens-clothing → Refined search
    """
    
    # ==========================================
    # 1. BASE QUERYSET - Start with all products
    # ==========================================
    # WHY: We need a starting point before applying filters
    # SECURITY: Only active, in-stock products shown to customers
    products = Product.objects.filter(
        is_active=True,
        stock__gt=0
    ).select_related(
        'category'  # JOIN category table (prevents N+1 queries)
    ).only(
        # Only load fields we need (memory optimization)
        'id', 'name', 'slug', 'price', 'sale_price', 
        'image', 'category__name', 'category__slug'
    )
    
    # ==========================================
    # 2. SEARCH FILTER - MOST IMPORTANT PART
    # ==========================================
    # Get search query from URL parameter: ?q=jacket
    search_query = request.GET.get('q', '').strip()
    
    # SECURITY: Limit query length (prevent DOS attacks)
    if len(search_query) > 100:
        search_query = search_query[:100]
    
    # DEBUG: Print to console to verify search is working
    if search_query:
        print(f"🔍 SEARCH QUERY: '{search_query}'")  # Remove this in production
        
        # APPLY SEARCH FILTER
        # This is the line that actually filters the results!
        products = products.filter(
            Q(name__icontains=search_query) |          # Search in product name
            Q(description__icontains=search_query) |   # OR in description
            Q(category__name__icontains=search_query)  # OR in category name
        )
        
        # DEBUG: Print result count
        print(f"📊 RESULTS FOUND: {products.count()}")  # Remove this in production
    
    # ==========================================
    # 3. CATEGORY FILTER
    # ==========================================
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # ==========================================
    # 4. PRICE RANGE FILTER
    # ==========================================
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    try:
        if min_price:
            min_price_decimal = Decimal(min_price)
            products = products.filter(price__gte=min_price_decimal)
    except (ValueError, InvalidOperation):
        pass
    
    try:
        if max_price:
            max_price_decimal = Decimal(max_price)
            products = products.filter(price__lte=max_price_decimal)
    except (ValueError, InvalidOperation):
        pass
    
    # ==========================================
    # 5. SORTING
    # ==========================================
    sort = request.GET.get('sort', 'newest')
    
    # SECURITY: Whitelist valid sort options
    VALID_SORTS = {
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'newest': '-created_at',
        'relevance': '-created_at'  # TODO: Add real relevance scoring
    }
    
    order_by = VALID_SORTS.get(sort, '-created_at')
    products = products.order_by(order_by)
    
    # ==========================================
    # 6. PAGINATION
    # ==========================================
    paginator = Paginator(products, 12)  # 12 products per page
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # ==========================================
    # 7. TEMPLATE CONTEXT
    # ==========================================
    context = {
        'products': products_page,
        'search_query': search_query,
        'current_sort': sort,
        'total_products': paginator.count,
        'page_title': f'Search Results for "{search_query}"' if search_query else 'All Products',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Search Results' if search_query else 'Products', 'url': None}
        ],
        'selected_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'products/product_list.html', context)


def category_products(request, slug):
    """
    Display products filtered by category.
    
    URL: /products/category/mens-clothing/
    """
    # Get category or return 404
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all products in this category
    products = Product.objects.filter(
        category=category,
        is_active=True,
        stock__gt=0
    ).select_related('category').only(
        'id', 'name', 'slug', 'price', 'sale_price', 
        'image', 'category__name', 'category__slug'
    )
    
    # Apply same sorting as product_list
    sort = request.GET.get('sort', 'newest')
    VALID_SORTS = {
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'newest': '-created_at'
    }
    order_by = VALID_SORTS.get(sort, '-created_at')
    products = products.order_by(order_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'category': category,
        'current_sort': sort,
        'total_products': paginator.count,
        'page_title': category.name,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': category.name, 'url': None}
        ]
    }
    
    return render(request, 'products/category_products.html', context)


def product_detail(request, slug):
    """
    Display single product detail page.
    
    URL: /products/mens-casual-premium-slim-fit-t-shirts/
    """
    # Get product or 404
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True
    )
    
    # Get product images (gallery)
    images = product.images.all().order_by('order')
    
    # Get reviews
    reviews = product.reviews.filter(
        is_approved=True
    ).select_related('user').order_by('-created_at')[:10]
    
    # Get related products (same category, exclude current)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock__gt=0
    ).exclude(
        id=product.id  # Don't show the current product
    ).only(
        'id', 'name', 'slug', 'price', 'sale_price', 'image'
    )[:4]  # Limit to 4 products
    
    # Breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Products', 'url': '/products/'},
        {'name': product.category.name, 'url': f'/products/category/{product.category.slug}/'},
        {'name': product.name, 'url': None}
    ]
    
    context = {
        'product': product,
        'images': images,
        'reviews': reviews,
        'related_products': related_products,
        'breadcrumbs': breadcrumbs
    }
    
    return render(request, 'products/product_detail.html', context)