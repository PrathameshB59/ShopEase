# shopease_project/urls.py
"""
MAIN URL CONFIGURATION
=======================
This is the root URL configuration for the entire project.
All URLs start here and are routed to appropriate apps.

URL Structure:
- / (root) → Home page
- /admin/ → Django admin interface
- /products/ → Product listing, detail pages
- /cart/ → Shopping cart
- /orders/ → Order management
- /accounts/ → User authentication (login, register, profile)

Think of this file as a map that tells Django:
"When user visits THIS url, show THAT page"
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the home view from products app
# We'll create this view in the next step
from products.views import home_view

# URL PATTERNS
# =============
# This list defines all the URLs in our application
urlpatterns = [
    # ADMIN PANEL
    # ===========
    # URL: http://127.0.0.1:8000/admin/
    # Django's built-in admin interface
    path('admin/', admin.site.urls),
    
    # HOME PAGE
    # ==========
    # URL: http://127.0.0.1:8000/
    # The main landing page customers see first
    # name='home' allows us to reference this URL in templates: {% url 'home' %}
    path('', home_view, name='home'),
    
    # PRODUCTS APP URLS
    # ==================
    # URL: http://127.0.0.1:8000/products/...
    # All product-related URLs (category pages, product details, etc.)
    # include() means: "Look in products/urls.py for more URL patterns"
    # namespace='products' lets us use {% url 'products:product_detail' %}
    path('products/', include('products.urls', namespace='products')),
    
    # ACCOUNTS APP URLS
    # ==================
    # URL: http://127.0.0.1:8000/accounts/...
    # User authentication URLs (login, register, profile)
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    # CART APP URLS
    # ==============
    # URL: http://127.0.0.1:8000/cart/...
    # Shopping cart URLs (view cart, add to cart, update, remove)
    # We'll create these later
    # path('cart/', include('cart.urls', namespace='cart')),
    
    # ORDERS APP URLS
    # ================
    # URL: http://127.0.0.1:8000/orders/...
    # Order-related URLs (checkout, order history, order details)
    # We'll create these later
    # path('orders/', include('orders.urls', namespace='orders')),
    
    # ACCOUNTS APP URLS
    # ==================
    # URL: http://127.0.0.1:8000/accounts/...
    # User authentication URLs (login, logout, register, profile)
    # We'll create these later
    # path('accounts/', include('accounts.urls', namespace='accounts')),
]

# MEDIA FILES CONFIGURATION (Development Only)
# =============================================
# Serve uploaded media files (product images, etc.) during development
# In production, use a proper web server (Nginx, Apache) to serve media files

if settings.DEBUG:
    # This adds a URL pattern that serves files from MEDIA_ROOT
    # Example: http://127.0.0.1:8000/media/products/iphone.jpg
    # Maps to: /path/to/project/media/products/iphone.jpg
    urlpatterns += static(
        settings.MEDIA_URL,           # URL prefix (/media/)
        document_root=settings.MEDIA_ROOT  # Actual folder on disk
    )
    
    # Also serve static files during development
    # CSS, JavaScript, images used in templates
    urlpatterns += static(
        settings.STATIC_URL,          # URL prefix (/static/)
        document_root=settings.STATIC_ROOT  # Actual folder on disk
    )

# EXPLANATION OF URL PATTERNS
# ============================
"""
1. path(route, view, name):
   - route: URL pattern (string)
   - view: Function or class that handles the request
   - name: Unique name to reference this URL
   
2. include():
   - Includes URLs from another app
   - Keeps URL configuration organized
   - Each app has its own urls.py
   
3. URL Resolution Flow:
   User visits: http://127.0.0.1:8000/products/electronics/
   
   Django checks:
   a) '' (root) - No match
   b) 'admin/' - No match
   c) 'products/' - Match! Now check products/urls.py
   
   In products/urls.py:
   - Looks for 'electronics/' pattern
   - Finds matching view
   - Executes view function
   - Returns HTML response
   
4. Namespaces:
   - Prevent URL name conflicts between apps
   - Both products and orders might have 'detail' URL
   - Use: {% url 'products:detail' %} vs {% url 'orders:detail' %}
"""

# URL NAMING CONVENTIONS
# =======================
"""
Good URL names should be:
- Descriptive: 'product_detail' not 'pd'
- Consistent: Use underscores, not hyphens
- Unique: No duplicates across apps (use namespaces)

Examples:
- 'home' - Homepage
- 'product_list' - List all products
- 'product_detail' - Single product page
- 'category_detail' - Category page
- 'cart_view' - View cart
- 'cart_add' - Add to cart
- 'checkout' - Checkout page
- 'order_confirmation' - Order success page
"""