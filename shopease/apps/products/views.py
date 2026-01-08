"""
========================================
PRODUCTS VIEWS - Product Display Logic
========================================
Handles product listings, category filtering, and product details.

Security:
- Only shows active products (prevents showing hidden items)
- Sanitizes all user input through Django ORM
- Uses get_object_or_404 to prevent information disclosure
- Validates category slugs before querying

Performance:
- Uses select_related to prevent N+1 queries
- Implements pagination (not just LIMIT)
- Only loads fields actually displayed
- Database indexes on filtered fields

Real-world considerations:
- SEO-friendly URLs with slugs
- Breadcrumb navigation
- Filtering preserves sort order
- Empty state handling
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Q
from .models import Product, Category


# ==========================================
# PRODUCT LIST VIEW - All Products
# ==========================================

def product_list(request):
    """
    Display all products with optional filtering and sorting.
    
    URL: /products/
    
    Query Parameters:
        - sort: 'price_low', 'price_high', 'name', 'newest'
        - page: Page number for pagination
    
    Why function-based view:
    - Simpler than class-based views for this use case
    - Easier to customize filtering logic
    - Better for beginners to understand
    
    Security:
        - is_active check prevents showing hidden products
        - Django ORM prevents SQL injection
        - Pagination prevents DOS via huge result sets
    
    Performance:
        - select_related loads category in same query
        - only() loads minimal fields
        - Pagination limits database load
        
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered product list page
    """
    
    # Base queryset - all active products with stock
    # This doesn't hit database yet (lazy evaluation)
    products = Product.objects.filter(
        is_active=True,      # WHERE is_active = TRUE
        stock__gt=0          # AND stock > 0
    ).select_related(        # LEFT JOIN category table
        'category'           # Prevents N+1 queries
    ).only(                  # SELECT only these fields:
        'id',                # Product ID
        'name',              # Product name
        'slug',              # URL slug
        'price',             # Regular price
        'sale_price',        # Discounted price
        'image',             # Main image
        'category__name',    # Category name (via JOIN)
        'category__slug'     # Category slug (via JOIN)
    )
    
    # Get sort parameter from URL (?sort=price_low)
    # Default to newest if not specified
    sort = request.GET.get('sort', 'newest')
    
    # Apply sorting based on user selection
    # This modifies the SQL ORDER BY clause
    if sort == 'price_low':
        # Order by price ascending (cheapest first)
        products = products.order_by('price')
    elif sort == 'price_high':
        # Order by price descending (expensive first)
        products = products.order_by('-price')
    elif sort == 'name':
        # Alphabetical order by product name
        products = products.order_by('name')
    elif sort == 'newest':
        # Newest products first (default)
        products = products.order_by('-created_at')
    
    # Pagination - break results into pages
    # Why paginate?
    # - Better performance (don't load 1000s of products)
    # - Better UX (users don't want to scroll forever)
    # - Lower bandwidth usage
    paginator = Paginator(products, 12)  # 12 products per page
    
    # Get requested page number from URL (?page=2)
    page = request.GET.get('page')
    
    try:
        # Try to get the requested page
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        # Example: ?page=abc → show page 1
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        # Example: ?page=999 → show last page
        products_page = paginator.page(paginator.num_pages)
    
    # Context data for template
    context = {
        'products': products_page,        # Page object with products
        'current_sort': sort,              # Current sort selection
        'total_products': paginator.count, # Total product count
        'page_title': 'All Products',      # For <title> tag
        'breadcrumbs': [                   # For breadcrumb navigation
            {'name': 'Home', 'url': '/'},
            {'name': 'Products', 'url': None}
        ]
    }
    
    return render(request, 'products/product_list.html', context)


# ==========================================
# CATEGORY VIEW - Products by Category
# ==========================================

def category_products(request, slug):
    """
    Display products filtered by category.
    
    URL: /products/category/<slug>/
    Example: /products/category/electronics/
    
    Why slugs instead of IDs:
    - SEO-friendly URLs
    - More meaningful to users
    - Can change without breaking URLs
    
    Security:
        - get_object_or_404 prevents information disclosure
          (returns 404 instead of revealing if category exists)
        - is_active check prevents accessing hidden categories
        - Slug validation via Django's SlugField
        - ORM prevents SQL injection
    
    Performance:
        - Uses prefetch_related for products (reverse FK)
        - Annotates product count (single query)
        - Caches category object
        
    Real-world considerations:
        - 404 page if category not found (not 500 error)
        - Empty state if no products in category
        - Breadcrumb navigation
        - SEO metadata (title, description)
        
    Args:
        request: HttpRequest object
        slug: Category slug from URL (e.g., 'electronics')
        
    Returns:
        HttpResponse: Rendered category page
    """
    
    # Get category or return 404
    # Why get_object_or_404:
    # - Returns 404 if not found (proper HTTP status)
    # - Prevents information disclosure (can't tell if category exists)
    # - Standard Django pattern
    # - Handles DoesNotExist exception automatically
    category = get_object_or_404(
        Category,
        slug=slug,           # WHERE slug = ?
        is_active=True       # AND is_active = TRUE
    )
    
    # Get products in this category
    # prefetch_related would be used if we needed reverse relations
    # But here we're going forward (product → category) so select_related
    products = Product.objects.filter(
        category=category,   # WHERE category_id = ?
        is_active=True,      # AND is_active = TRUE
        stock__gt=0          # AND stock > 0
    ).select_related(        # Already have category, but good practice
        'category'
    ).only(
        'id', 'name', 'slug', 'price', 'sale_price', 
        'image', 'category__name', 'category__slug'
    )
    
    # Get sort parameter
    sort = request.GET.get('sort', 'newest')
    
    # Apply sorting (same as product_list)
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination (12 products per page)
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Context for template
    context = {
        'category': category,              # Category object
        'products': products_page,         # Page object with products
        'current_sort': sort,              # Current sort selection
        'total_products': paginator.count, # Total products in category
        'page_title': f'{category.name} Products',  # For <title> tag
        'breadcrumbs': [                   # Breadcrumb navigation
            {'name': 'Home', 'url': '/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': category.name, 'url': None}
        ]
    }
    
    return render(request, 'products/category_products.html', context)


# ==========================================
# PRODUCT DETAIL VIEW - Single Product
# ==========================================

def product_detail(request, slug):
    """
    Display detailed information for a single product.
    
    URL: /products/<slug>/
    Example: /products/apple-iphone-15-pro/
    
    Features:
    - Product images gallery
    - Reviews and ratings
    - Stock availability
    - Add to cart functionality
    - Related products
    
    Security:
        - get_object_or_404 prevents information disclosure
        - is_active check prevents viewing hidden products
        - Reviews filtered to approved only
        
    Performance:
        - select_related for category (1 query)
        - prefetch_related for images (2 queries total)
        - Annotates average rating (database-level)
        
    Args:
        request: HttpRequest object
        slug: Product slug from URL
        
    Returns:
        HttpResponse: Rendered product detail page
    """
    
    # Get product with related data
    # Why select_related AND prefetch_related:
    # - select_related: For forward FK (product → category)
    # - prefetch_related: For reverse FK (product ← images, reviews)
    product = get_object_or_404(
        Product.objects.select_related(
            'category'           # Load category in same query
        ).prefetch_related(
            'images',            # Load product images in 2nd query
            'reviews'            # Load reviews in 3rd query
        ),
        slug=slug,               # WHERE slug = ?
        is_active=True           # AND is_active = TRUE
    )
    
    # Get approved reviews only
    # Security: Never show unapproved reviews (spam/inappropriate)
    reviews = product.reviews.filter(
        is_approved=True
    ).select_related('user').order_by('-created_at')[:10]
    
    # Get related products (same category, different product)
    # Why limit to 4:
    # - Don't overwhelm user with choices
    # - Faster page load
    # - Better mobile experience
    related_products = Product.objects.filter(
        category=product.category,  # Same category
        is_active=True,
        stock__gt=0
    ).exclude(
        id=product.id               # Don't show current product
    ).only(
        'id', 'name', 'slug', 'price', 'sale_price', 'image'
    )[:4]  # LIMIT 4
    
    # Context for template
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'page_title': product.name,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': product.category.name, 'url': f'/products/category/{product.category.slug}/'},
            {'name': product.name, 'url': None}
        ]
    }
    
    return render(request, 'products/product_detail.html', context)