"""
=============================================================================
MAIN URL CONFIGURATION - ShopEase E-Commerce Platform
=============================================================================

This is the ROOT URL configuration file. It's the entry point for all URL
routing in your Django project.

Think of it as a reception desk that directs visitors to different
departments (apps) based on the URL they request.

URL ROUTING FLOW:
1. User requests: http://localhost:8000/products/123/
2. Django loads THIS file (because settings.py says ROOT_URLCONF = 'shopease_project.urls')
3. Django checks urlpatterns from top to bottom
4. Finds matching pattern and forwards to the appropriate view/app
5. View processes request and returns response

Official Django URL dispatcher documentation:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

# =============================================================================
# IMPORTS - Required modules for URL routing
# =============================================================================

from django.contrib import admin  # Django's built-in admin interface
from django.urls import path, include  # URL routing functions
from django.conf import settings  # Access to settings.py variables
from django.conf.urls.static import static  # Helper for serving static/media files in development


# =============================================================================
# URL PATTERNS - The routing table
# =============================================================================

# urlpatterns is a list of URL routes
# Django checks these patterns in order from top to bottom
# When a match is found, it stops looking and routes to that view
urlpatterns = [

    # =================================================================
    # ADMIN PANEL - Django's built-in admin interface
    # =================================================================

    # path() function signature: path(route, view_or_include, name=None)
    #
    # route = 'admin/' means any URL starting with /admin/
    # admin.site.urls = Django's admin interface views
    #
    # When user visits: http://localhost:8000/admin/
    # Django forwards to: admin.site.urls (built-in admin)
    #
    # The admin provides a web interface to:
    # - Create/edit/delete database records
    # - Manage users and permissions
    # - View all your models in a nice UI
    # - No need to write CRUD views manually!
    path('admin/', admin.site.urls),


    # =================================================================
    # PRODUCTS APP - Main shopping functionality
    # =================================================================

    # path() with include() delegates URL routing to another app
    #
    # route = '' (empty string) means root URL
    # include('products.urls') means:
    #   1. Look in products app
    #   2. Find its urls.py file
    #   3. Use URL patterns defined there
    #
    # This is called "URL namespacing" - each app manages its own URLs
    #
    # Example URL flow:
    # User requests: http://localhost:8000/products/
    # 1. Django checks this file, finds '' pattern
    # 2. Includes products.urls
    # 3. Products URLs check for 'products/' pattern
    # 4. Routes to appropriate product view
    #
    # Benefits of include():
    # - Apps are self-contained (can be reused in other projects)
    # - URLs organized by feature
    # - Team members can work on different apps without conflicts
    # - Easy to add/remove features
    path('', include('products.urls')),

    # TO ADD MORE APPS, INCLUDE THEIR URLs HERE:
    # path('cart/', include('cart.urls')),        # Shopping cart
    # path('orders/', include('orders.urls')),    # Order management
    # path('accounts/', include('accounts.urls')), # User accounts
    # path('api/', include('api.urls')),          # REST API endpoints
]


# =============================================================================
# DEVELOPMENT-ONLY SETTINGS - Static and Media Files
# =============================================================================

# In development, Django can serve static/media files
# In production, web server (Nginx/Apache) handles this
#
# Why this check? settings.DEBUG is True in development, False in production
if settings.DEBUG:
    # Add media file serving to URL patterns
    #
    # static() is a helper function that creates URL patterns for serving files
    #
    # settings.MEDIA_URL = '/media/'
    # settings.MEDIA_ROOT = '/path/to/project/media/'
    #
    # This means:
    # - URL: http://localhost:8000/media/products/phone.jpg
    # - File: /path/to/project/media/products/phone.jpg
    #
    # += appends these patterns to existing urlpatterns list
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add static file serving to URL patterns
    #
    # settings.STATIC_URL = '/static/'
    # settings.STATIC_ROOT = '/path/to/project/staticfiles/'
    #
    # This means:
    # - URL: http://localhost:8000/static/css/style.css
    # - File: /path/to/project/static/css/style.css (or staticfiles after collectstatic)
    #
    # Note: Django's runserver automatically serves static files in DEBUG mode,
    # but this ensures it works for other WSGI servers too
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# =============================================================================
# HOW URL ROUTING WORKS - DETAILED EXPLANATION
# =============================================================================

"""
EXAMPLE 1: Basic URL Routing
-----------------------------
User visits: http://localhost:8000/admin/products/product/

Django's matching process:
1. Strips domain: /admin/products/product/
2. Checks urlpatterns:
   - path('admin/', ...) ← MATCH!
3. Removes 'admin/' from path, leaving: products/product/
4. Forwards to admin.site.urls
5. Admin URLconf handles the rest

EXAMPLE 2: Include() URL Routing
---------------------------------
User visits: http://localhost:8000/products/123/

Django's matching process:
1. Strips domain: /products/123/
2. Checks urlpatterns:
   - path('admin/', ...) ← No match
   - path('', include('products.urls')) ← MATCH! ('' matches anything)
3. Forwards '/products/123/' to products.urls
4. Products URLconf checks its patterns:
   - path('products/<int:product_id>/', views.product_detail, name='product-detail') ← MATCH!
5. Calls views.product_detail(request, product_id=123)

EXAMPLE 3: Static Files
------------------------
User requests: http://localhost:8000/media/products/phone.jpg

Django's matching process:
1. Strips domain: /media/products/phone.jpg
2. Checks urlpatterns:
   - path('admin/', ...) ← No match
   - path('', ...) ← No match
   - static(settings.MEDIA_URL, ...) ← MATCH!
3. Serves file from: /path/to/project/media/products/phone.jpg


URL PATTERN COMPONENTS
----------------------

1. path(route, view, name=None)
   - route: URL pattern to match ('products/', 'admin/', etc.)
   - view: View function or include() to call
   - name: Optional name for reverse URL lookup

2. include(module)
   - Includes another URLconf module
   - Allows apps to manage their own URLs
   - Creates clean URL structure

3. Path Converters:
   - <int:id>       Matches integers: /products/123/
   - <str:slug>     Matches strings: /products/iphone-14/
   - <uuid:id>      Matches UUIDs: /products/550e8400-e29b-41d4-a716-446655440000/
   - <path:path>    Matches any path: /files/documents/report.pdf


BEST PRACTICES
--------------

1. Always use include() for app URLs
   ✓ path('blog/', include('blog.urls'))
   ✗ Importing all blog views into main URLs

2. Keep main urls.py minimal
   ✓ Only admin and app includes
   ✗ Hundreds of URL patterns here

3. Use URL namespaces
   ✓ app_name = 'products' in products/urls.py
   ✓ Then use: {% url 'products:product-list' %}
   ✗ Generic names that might conflict

4. Serve static files properly
   ✓ if settings.DEBUG: in development
   ✓ Configure Nginx/Apache in production
   ✗ Serving with Django in production (slow!)

5. Order matters!
   Django checks patterns top to bottom:
   ✓ path('products/featured/', ...)
   ✓ path('products/<int:id>/', ...)
   ✗ path('products/<int:id>/', ...)  ← This would match 'featured' as ID!
   ✗ path('products/featured/', ...)


COMMON URL PATTERNS FOR E-COMMERCE
-----------------------------------

# Homepage
path('', views.home, name='home')

# Product URLs
path('products/', views.product_list, name='product-list')
path('products/<int:id>/', views.product_detail, name='product-detail')
path('products/<slug:slug>/', views.product_by_slug, name='product-slug')
path('products/category/<int:cat_id>/', views.category_products, name='category')

# Cart URLs
path('cart/', views.cart_view, name='cart')
path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart')
path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart')

# Checkout URLs
path('checkout/', views.checkout, name='checkout')
path('checkout/success/', views.checkout_success, name='checkout-success')

# Account URLs
path('accounts/login/', views.login_view, name='login')
path('accounts/register/', views.register_view, name='register')
path('accounts/profile/', views.profile_view, name='profile')

# Search
path('search/', views.search, name='search')

# API endpoints
path('api/products/', api_views.ProductListAPI.as_view(), name='api-products')
path('api/cart/', api_views.CartAPI.as_view(), name='api-cart')


DEBUGGING URL ROUTING
----------------------

Can't figure out why your URL isn't working?

1. Check URL pattern order (Django stops at first match)
2. Print available URLs: python manage.py show_urls
3. Check for typos in route strings
4. Verify include() points to correct app
5. Test URL in browser: http://localhost:8000/your-url/
6. Check Django's error page (it shows tried patterns)


SECURITY NOTES
--------------

1. Never expose admin at /admin/ in production
   - Use custom URL: path('secret-admin-panel/', admin.site.urls)

2. Be careful with pattern order
   - Don't let <path:filename> match before specific routes

3. Validate URL parameters in views
   - User might visit: /products/99999999999/
   - Always check if object exists

4. Use HTTPS in production
   - Django can enforce this with SECURE_SSL_REDIRECT = True
"""
