"""
========================================
CORE VIEWS - Homepage Logic
========================================
Handles homepage display with featured products and categories.

Performance optimization:
- Uses select_related for foreign keys (prevents N+1 queries)
- Uses only() to load minimal fields
- Limits queries with slicing [:8]

Security:
- Only shows active products (is_active=True)
- Only shows in-stock products (stock__gt=0)
- Django ORM prevents SQL injection
"""

from django.shortcuts import render
from apps.products.models import Product, Category


def home(request):
    """
    Homepage view displaying featured products and categories.
    
    This is a function-based view (FBV) - simpler than class-based views.
    Django calls this function when someone visits the homepage.
    
    Args:
        request: HttpRequest object containing metadata about the request
                 (user, session, cookies, GET/POST data, etc.)
    
    Returns:
        HttpResponse: Rendered HTML page with context data
    
    Context variables sent to template:
        - featured_products: Up to 8 featured products
        - categories: All active categories
    
    Performance notes:
        - select_related('category'): JOIN category table in same query
          This prevents N+1 query problem where Django would make:
          1 query for products + N queries for each product's category
          Instead: 1 query gets everything
        
        - only(): Load only specific fields (saves memory & bandwidth)
          Without this, Django loads ALL fields for each product
          With this: Only loads the fields we actually need
        
        - [:8]: SQL LIMIT clause, only fetch 8 rows from database
          More efficient than loading all products then slicing in Python
    
    Security notes:
        - is_active=True: Only show products admin has marked as active
          Prevents showing discontinued/hidden products
        
        - stock__gt=0: Only show products with stock > 0
          Prevents showing "sold out" items as featured
        
        - Django ORM: All queries parameterized, prevents SQL injection
          User can't inject malicious SQL through URL parameters
    """
    
    # Query featured products from database
    # This builds a SQL query but doesn't execute yet (lazy evaluation)
    featured_products = Product.objects.filter(
        is_featured=True,      # WHERE is_featured = TRUE
        is_active=True,        # AND is_active = TRUE
        stock__gt=0            # AND stock > 0
    ).select_related(          # LEFT JOIN products_category
        'category'             # Fetch category data in same query
    ).only(                    # SELECT only these fields:
        'id',                  # - product.id
        'name',                # - product.name
        'slug',                # - product.slug
        'price',               # - product.price
        'sale_price',          # - product.sale_price
        'image',               # - product.image
        'category__name',      # - category.name (via JOIN)
        'category__slug'       # - category.slug (via JOIN)
    )[:8]                      # LIMIT 8
    
    # Query categories from database
    categories = Category.objects.filter(
        is_active=True         # WHERE is_active = TRUE
    ).only(                    # SELECT only these fields:
        'name',                # - category.name
        'slug',                # - category.slug
        'image'                # - category.image
    )[:6]                      # LIMIT 6
    
    # Debug: Print to console to verify data exists
    # Remove these in production (use logging instead)
    print(f"DEBUG: Featured products count: {featured_products.count()}")
    print(f"DEBUG: Categories count: {categories.count()}")
    
    # Context dictionary - data to send to template
    # Template can access these as {{ featured_products }} and {{ categories }}
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    
    # Render template with context data
    # Django:
    # 1. Loads templates/home.html
    # 2. Processes template tags ({% for %}, {{ }}, etc.)
    # 3. Replaces variables with context data
    # 4. Returns HttpResponse with rendered HTML
    return render(request, 'home.html', context)