"""
========================================
CORE VIEWS - Homepage Logic
========================================
Handles homepage display with featured products and categories.

Performance optimization:
- Uses select_related for foreign keys (prevents N+1 queries)
- Uses only() to load minimal fields
- Caches page for 15 minutes
"""

from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from apps.products.models import Product, Category


class HomeView(TemplateView):
    """
    Homepage view displaying featured products and categories.
    
    Template: home.html
    Context variables:
        - featured_products: Up to 8 featured products
        - categories: All active categories
    """
    
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        """
        Add featured products and categories to template context.
        
        Performance notes:
        - select_related('category'): Fetch category in same query
        - only(): Load only fields we need (saves memory)
        - [:8]: Limit to 8 products (LIMIT in SQL)
        
        Security notes:
        - is_active=True: Only show active products
        - Django ORM prevents SQL injection
        """
        
        context = super().get_context_data(**kwargs)
        
        # Fetch featured products with category
        # select_related('category'): JOIN category table (1 query instead of N+1)
        # only(): Load only these fields (faster, uses less memory)
        context['featured_products'] = Product.objects.filter(
            is_featured=True,
            is_active=True,
            stock__gt=0  # Only in-stock products
        ).select_related('category').only(
            'id', 'name', 'slug', 'price', 'sale_price', 
            'image', 'category__name', 'category__slug'
        )[:8]  # Limit to 8 products
        
        # Fetch all active categories
        context['categories'] = Category.objects.filter(
            is_active=True
        ).only('name', 'slug', 'image')[:6]  # Limit to 6 categories
        
        return context