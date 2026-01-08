"""
========================================
PRODUCTS URLs - Routing Configuration
========================================
Maps URLs to views for the products app.

URL Structure:
    /products/                          → All products list
    /products/category/<slug>/          → Products by category
    /products/<slug>/                   → Product detail page

Why this structure:
- SEO-friendly (descriptive URLs)
- Logical hierarchy
- Easy to remember
- RESTful design

Security:
- slug fields validated by Django's SlugField
- No user IDs exposed in URLs
- Prevents enumeration attacks
"""

from django.urls import path
from . import views

# Namespace for this app
# Allows {% url 'products:product_list' %} in templates
# Prevents naming conflicts with other apps
app_name = 'products'

urlpatterns = [
    # All products list
    # URL: /products/
    # Name: 'products:product_list'
    # View: views.product_list
    # Usage: {% url 'products:product_list' %}
    path('', views.product_list, name='product_list'),
    
    # Category products list
    # URL: /products/category/electronics/
    # Name: 'products:category'
    # View: views.category_products
    # Usage: {% url 'products:category' category.slug %}
    # 
    # Why 'category/' prefix:
    # - Distinguishes from product detail URLs
    # - Prevents conflicts (what if product slug is 'electronics'?)
    # - More explicit and clear
    path('category/<slug:slug>/', views.category_products, name='category'),
    
    # Product detail page
    # URL: /products/apple-iphone-15-pro/
    # Name: 'products:detail'
    # View: views.product_detail
    # Usage: {% url 'products:detail' product.slug %}
    # 
    # Why last:
    # - Django matches URLs top-to-bottom
    # - More specific patterns go first
    # - This catches everything else
    path('<slug:slug>/', views.product_detail, name='detail'),
]