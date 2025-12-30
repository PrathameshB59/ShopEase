"""
=============================================================================
PRODUCTS APP URL CONFIGURATION - ShopEase E-Commerce Platform
=============================================================================

This file defines all URL patterns for the products app. It handles
routing for:
- Homepage
- Product listing and filtering
- Product detail pages
- Search functionality
- Category browsing

This is called an "app-level URLconf" - it's included by the main
project URLs file (shopease_project/urls.py).

URL STRUCTURE FOR THIS APP:
----------------------------
/                              → Homepage (featured products)
/products/                     → All products listing
/products/123/                 → Product detail page
/products/search/?q=laptop     → Search results

Official Django URL documentation:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

# =============================================================================
# IMPORTS - Required modules
# =============================================================================

from django.urls import path  # The path() function for defining URL patterns
from . import views  # Import views from current app (products/views.py)
                     # The dot (.) means "current package"


# =============================================================================
# APP NAMESPACE - Prevents URL name conflicts
# =============================================================================

# app_name creates a namespace for this app's URLs
#
# Without namespace:
#   {% url 'home' %} ← Which home? products home? accounts home? blog home?
#
# With namespace:
#   {% url 'products:home' %} ← Clear! This is the products app homepage
#
# This allows multiple apps to have URLs with the same name without conflicts
# For example:
# - products app: 'products:detail' → product detail page
# - blog app: 'blog:detail' → blog post detail page
# - Both can use name='detail' without conflicting
app_name = 'products'  # This creates the namespace!


# =============================================================================
# URL PATTERNS - All routes for the products app
# =============================================================================

# urlpatterns is a list that Django reads from top to bottom
# When a URL matches, Django stops searching and calls that view
# ORDER MATTERS! Put specific patterns before general ones
urlpatterns = [

    # =========================================================================
    # HOMEPAGE - Site landing page
    # =========================================================================

    # path() signature: path(route, view_function, kwargs=None, name=None)

    path(
        '',                # Route: Empty string matches the root URL
                          # Since main urls.py includes this at '', this pattern matches: /
                          # Main URLs: path('', include('products.urls'))
                          # So '' + '' = http://localhost:8000/

        views.home,        # View: Function in products/views.py called home()
                          # This function fetches featured products and categories
                          # It renders templates/home.html

        name='home'        # Name: Used for reverse URL lookup in templates/views
                          # In templates: <a href="{% url 'products:home' %}">Home</a>
                          # In views: from django.urls import reverse
                          #           url = reverse('products:home')  # Returns '/'
    ),


    # =========================================================================
    # PRODUCT LISTING - Browse all products
    # =========================================================================

    path(
        'products/',           # Route: Matches /products/
                              # URL pattern matching is literal - must match exactly
                              # Matches: /products/
                              # Does NOT match: /product/ or /products or /products/123/

        views.product_list,    # View: Function that displays paginated product grid
                              # Handles filtering by category: /products/?category=1
                              # Handles pagination: /products/?page=2
                              # Renders: templates/products/product_list.html

        name='product-list'    # Name: 'product-list' (note: kebab-case is common for names)
                              # Template usage: <a href="{% url 'products:product-list' %}">Shop</a>
                              # View usage: redirect('products:product-list')
    ),


    # =========================================================================
    # PRODUCT DETAIL - Single product page
    # =========================================================================

    path(
        'products/<int:product_id>/',  # Route with URL parameter
                                       # <int:product_id> is a path converter
                                       #
                                       # Breaking it down:
                                       # - <...> = placeholder for dynamic content
                                       # - int = accepts only integers (1, 42, 9999)
                                       # - product_id = variable name passed to view
                                       #
                                       # Matches:
                                       #   /products/1/     → product_id=1
                                       #   /products/42/    → product_id=42
                                       #   /products/9999/  → product_id=9999
                                       #
                                       # Does NOT match:
                                       #   /products/abc/   ← Not an integer
                                       #   /products/       ← Missing ID
                                       #   /products/1      ← Missing trailing slash

        views.product_detail,          # View: Function signature must accept product_id
                                       # def product_detail(request, product_id):
                                       #     product = get_product(product_id)
                                       #     ...
                                       #
                                       # Django automatically passes product_id from URL

        name='product-detail'          # Name for reverse URL generation
                                       # Template with parameter:
                                       #   {% url 'products:product-detail' product_id=42 %}
                                       #   Generates: /products/42/
                                       #
                                       # View with parameter:
                                       #   reverse('products:product-detail', kwargs={'product_id': 42})
                                       #   Returns: '/products/42/'
    ),


    # =========================================================================
    # PRODUCT SEARCH - Find products by keyword
    # =========================================================================

    path(
        'products/search/',        # Route: Literal path for search
                                  # Matches: /products/search/
                                  # Query parameters come from GET:
                                  #   /products/search/?q=laptop
                                  #   /products/search/?q=laptop&page=2
                                  #
                                  # IMPORTANT: This MUST come BEFORE 'products/<int:product_id>/'
                                  # Why? If we put it after, Django would match 'search' as
                                  # a product_id (and fail since 'search' is not an integer)

        views.search_products,     # View: Handles search logic
                                  # Gets search query from: request.GET.get('q')
                                  # Example: /products/search/?q=laptop&page=2
                                  # request.GET = {'q': 'laptop', 'page': '2'}

        name='product-search'      # Name for generating search URLs
                                  # Template example:
                                  #   <form action="{% url 'products:product-search' %}" method="get">
                                  #       <input name="q" placeholder="Search...">
                                  #   </form>
    ),
]


# =============================================================================
# URL PATTERNS EXPLAINED IN DEPTH
# =============================================================================

"""
HOW PATH CONVERTERS WORK
-------------------------

Django provides built-in path converters for capturing URL parameters:

1. <int:name>
   - Matches: Any positive integer
   - Examples: 1, 42, 9999, 1000000
   - Does NOT match: -5 (negative), 3.14 (decimal), "abc" (string)
   - Use for: IDs, page numbers, quantities
   - Generated view parameter type: int

2. <str:name>
   - Matches: Any non-empty string (excluding /)
   - Examples: "hello", "product-name", "123" (treated as string)
   - Does NOT match: "" (empty), "hello/world" (contains /)
   - Use for: Slugs, usernames, categories
   - Generated view parameter type: str

3. <slug:name>
   - Matches: Slug format (letters, numbers, hyphens, underscores)
   - Examples: "iphone-14", "gaming-laptop", "product_123"
   - Does NOT match: "Hello World" (spaces), "café" (special chars)
   - Use for: SEO-friendly URLs
   - Generated view parameter type: str
   - Pattern: [-a-zA-Z0-9_]+

4. <uuid:name>
   - Matches: UUID format
   - Example: "075194d3-6885-417e-a8a8-6c931e272f00"
   - Use for: Secure unique IDs
   - Generated view parameter type: uuid.UUID

5. <path:name>
   - Matches: Any string INCLUDING /
   - Examples: "docs/tutorial.pdf", "images/products/phone.jpg"
   - Use for: File paths, nested structures
   - Generated view parameter type: str


PATH CONVERTER EXAMPLES
------------------------

# Product by ID (integer)
path('products/<int:product_id>/', views.detail)
URL: /products/42/
View: def detail(request, product_id):  # product_id = 42 (int)

# Product by slug (SEO-friendly)
path('products/<slug:slug>/', views.detail_by_slug)
URL: /products/iphone-14-pro/
View: def detail_by_slug(request, slug):  # slug = "iphone-14-pro" (str)

# Category and product
path('category/<int:cat_id>/products/<int:prod_id>/', views.detail)
URL: /category/5/products/42/
View: def detail(request, cat_id, prod_id):  # cat_id=5, prod_id=42

# File download with path
path('download/<path:filepath>/', views.download)
URL: /download/docs/2024/report.pdf
View: def download(request, filepath):  # filepath = "docs/2024/report.pdf"


QUERY PARAMETERS vs PATH PARAMETERS
------------------------------------

PATH PARAMETERS (in URL pattern):
    path('products/<int:id>/', views.detail)
    URL: /products/42/
    Access: def detail(request, id):  # id comes from URL pattern

QUERY PARAMETERS (after ?):
    path('products/', views.list)
    URL: /products/?category=electronics&page=2
    Access: def list(request):
                category = request.GET.get('category')  # 'electronics'
                page = request.GET.get('page')          # '2'

When to use which?
- Path parameters: Required, identifies a resource
  Example: /products/42/ (ID 42 is essential)

- Query parameters: Optional, filters or modifies
  Example: /products/?category=electronics&sort=price
           (filters are optional, defaults can be used)


URL NAMING BEST PRACTICES
--------------------------

1. Use descriptive names:
   ✓ name='product-detail'
   ✓ name='checkout-success'
   ✗ name='detail'  (too generic)
   ✗ name='page2'   (unclear purpose)

2. Use kebab-case (hyphens):
   ✓ name='product-detail'
   ✓ name='add-to-cart'
   ✗ name='product_detail'  (use hyphens, not underscores)
   ✗ name='ProductDetail'   (not PascalCase)

3. Match URL structure in name:
   URL: 'products/<int:id>/'     → name='product-detail'
   URL: 'cart/add/'              → name='cart-add'
   URL: 'checkout/success/'      → name='checkout-success'

4. Include namespace in templates:
   ✓ {% url 'products:product-detail' id=42 %}
   ✗ {% url 'product-detail' id=42 %}  (might conflict with other apps)


REVERSE URL GENERATION
-----------------------

In Templates:
    <a href="{% url 'products:home' %}">Home</a>
    <a href="{% url 'products:product-detail' product_id=42 %}">View Product</a>

In Views:
    from django.urls import reverse
    from django.shortcuts import redirect

    # Simple reverse
    url = reverse('products:home')  # Returns: '/'

    # Reverse with parameters
    url = reverse('products:product-detail', kwargs={'product_id': 42})
    # Returns: '/products/42/'

    # Redirect to URL
    return redirect('products:home')
    return redirect('products:product-detail', product_id=42)

Why use reverse instead of hardcoding URLs?
    ✓ Changing URL pattern updates everywhere automatically
    ✓ No broken links
    ✓ Maintainable codebase

    ✗ Hardcoded: <a href="/products/42/">View</a>
      (if you change URL pattern to /items/42/, link breaks)

    ✓ Dynamic: <a href="{% url 'products:product-detail' product_id=42 %}">View</a>
      (automatically adapts to URL changes)


URL PATTERN ORDER - EXTREMELY IMPORTANT!
-----------------------------------------

Django checks patterns TOP TO BOTTOM and stops at first match.

WRONG ORDER (will cause bugs):
    path('products/<int:id>/', views.detail),      # This matches FIRST
    path('products/search/', views.search),        # This NEVER matches!

Why broken? Django sees "products/search/" and matches it against
"products/<int:id>/" thinking "search" is an ID. It tries to convert
"search" to int, fails, and returns 404.

CORRECT ORDER (specific before general):
    path('products/search/', views.search),        # Specific pattern first
    path('products/<int:id>/', views.detail),      # General pattern after

Rule: Always put literal paths BEFORE dynamic paths!


COMMON ECOMMERCE URL PATTERNS
------------------------------

# Homepage
path('', views.home, name='home')

# Products
path('products/', views.product_list, name='product-list')
path('products/<int:id>/', views.product_detail, name='product-detail')
path('products/<slug:slug>/', views.product_by_slug, name='product-slug')
path('products/category/<int:category_id>/', views.by_category, name='category')
path('products/search/', views.search, name='search')

# Shopping Cart
path('cart/', views.view_cart, name='cart')
path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart')
path('cart/update/<int:item_id>/', views.update_cart, name='update-cart')
path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart')
path('cart/clear/', views.clear_cart, name='clear-cart')

# Checkout
path('checkout/', views.checkout, name='checkout')
path('checkout/payment/', views.payment, name='payment')
path('checkout/success/<int:order_id>/', views.order_success, name='order-success')

# User Account
path('account/profile/', views.profile, name='profile')
path('account/orders/', views.order_history, name='orders')
path('account/orders/<int:order_id>/', views.order_detail, name='order-detail')

# Reviews
path('products/<int:product_id>/review/', views.add_review, name='add-review')


DEBUGGING URL ISSUES
---------------------

Problem: "Page not found (404)"
Solutions:
1. Check URL pattern exists in urlpatterns
2. Verify pattern matches exactly (check trailing slash)
3. Ensure pattern order is correct (specific before general)
4. Check namespace usage: 'products:home' not just 'home'
5. Look at Django's error page - it shows all tried patterns

Problem: "NoReverseMatch"
Solutions:
1. Check URL name is spelled correctly
2. Include namespace: 'products:detail' not 'detail'
3. Pass required parameters: product_id, etc.
4. Verify app_name is set in app's urls.py

Problem: Wrong view is called
Solutions:
1. Check pattern order (Django uses first match)
2. Verify path converter type (int vs str vs slug)
3. Check pattern specificity

Testing URLs:
    # Test in shell
    python manage.py shell
    >>> from django.urls import reverse
    >>> reverse('products:home')
    '/'
    >>> reverse('products:product-detail', kwargs={'product_id': 42})
    '/products/42/'


SECURITY CONSIDERATIONS
------------------------

1. Always validate URL parameters in views:
   def product_detail(request, product_id):
       try:
           product = Product.objects.get(id=product_id)
       except Product.DoesNotExist:
           return HttpResponseNotFound("Product not found")

2. Use path converters to restrict input:
   ✓ <int:id> only accepts integers
   ✗ <str:id> accepts anything

3. Be careful with <path:name>:
   Could allow: /files/../../etc/passwd (directory traversal)
   Always sanitize in view

4. Don't expose sensitive IDs:
   ✗ /user/12345/profile/  (database ID visible)
   ✓ /user/<uuid>/profile/ (UUID is safer)
   ✓ /profile/              (use session to get user)


RELATED FILES
-------------
This URL configuration works together with:
- shopease_project/urls.py  (includes this file)
- products/views.py         (contains view functions)
- templates/products/*.html (rendered by views)
- products/models.py        (data models)

Understanding how these files work together is key to Django mastery!
"""
