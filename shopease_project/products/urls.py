# products/urls.py
"""
PRODUCTS APP URL CONFIGURATION
================================
This file defines all URLs specific to the products app.

URLs in this app:
- /products/ - List all products
- /products/category/<slug>/ - Products in a category
- /products/<slug>/ - Individual product detail page
- /products/search/ - Search products
"""

from django.urls import path
from . import views

# App name for namespacing
# Allows us to use {% url 'products:product_detail' slug='iphone' %}
app_name = 'products'

# URL PATTERNS FOR PRODUCTS APP
# ==============================
urlpatterns = [
    # PRODUCT LIST PAGE
    # =================
    # URL: /products/
    # Shows all active products
    # View: ProductListView (class-based view)
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # CATEGORY DETAIL PAGE
    # ====================
    # URL: /products/category/electronics/
    # Shows all products in a specific category
    # <slug:slug> means: capture a slug from URL and pass it to view as 'slug' parameter
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # PRODUCT DETAIL PAGE
    # ====================
    # URL: /products/iphone-15-pro/
    # Shows details of a single product
    # <slug:slug> captures product slug from URL
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # SEARCH PAGE
    # ===========
    # URL: /products/search/?q=iphone
    # Search products by name, description, or brand
    # We'll add this later
    # path('search/', views.ProductSearchView.as_view(), name='product_search'),
]

# URL PATTERN EXPLANATION
# ========================
"""
Django URL patterns use angle brackets < > to capture parts of the URL:

1. <type:name>
   - type: Data type (int, str, slug, uuid, path)
   - name: Variable name passed to view
   
2. Examples:
   - <int:id> → Captures integers: /products/5/
   - <slug:slug> → Captures slugs: /products/iphone-15/
   - <str:username> → Captures strings: /user/john/
   
3. Order matters!
   - More specific patterns should come first
   - /products/search/ should come before /products/<slug>/
   - Otherwise 'search' would be captured as a product slug

4. URL Resolution Example:
   User visits: /products/iphone-15-pro/
   
   Django checks patterns in order:
   a) '' - No match (needs more)
   b) 'category/<slug:slug>/' - No match (missing 'category/')
   c) '<slug:slug>/' - MATCH! 
      - Captures 'iphone-15-pro' as slug parameter
      - Calls ProductDetailView with slug='iphone-15-pro'
"""

# SLUG EXPLANATION
# =================
"""
What is a slug?
- URL-friendly string
- Usually lowercase
- Hyphens instead of spaces
- No special characters

Examples:
- "iPhone 15 Pro" → "iphone-15-pro"
- "Men's Blue Shirt" → "mens-blue-shirt"
- "Book: Python 101" → "book-python-101"

Why use slugs?
1. SEO-friendly URLs
2. Human-readable
3. Better than IDs (/products/iphone-15/ vs /products/42/)
4. Descriptive for search engines
"""