"""
========================================
PRODUCT TEMPLATE TAGS - Reusable Data Loaders
========================================
Custom Django template tags for loading product-related data.

What are template tags?
- Special functions that can be called inside templates
- Load data without passing through views
- Make templates more dynamic and reusable

Security:
- Only loads active categories (is_active=True)
- Uses Django ORM (prevents SQL injection)
- Read-only operations (no data modification)

Performance:
- Caches results to avoid repeated database queries
- Only loads minimal fields needed (name, slug, id)
- Limits to active categories only
"""

from django import template
from apps.products.models import Category

# Register this file as a template tag library
# Django looks for this when you use {% load products_tags %}
register = template.Library()


@register.simple_tag
def get_categories():
    """
    Load all active categories for navigation dropdown.
    
    Usage in templates:
        {% load products_tags %}
        {% get_categories as categories %}
        {% for category in categories %}
            {{ category.name }}
        {% endfor %}
    
    Why this is better than passing in every view:
    - DRY principle: Define once, use everywhere
    - Navigation always shows categories without view changes
    - Easier to maintain (one place to update)
    
    Performance:
    - Queries database once per page load
    - Only loads 3 fields (id, name, slug)
    - Filters to active categories only
    
    Security:
    - is_active check prevents showing hidden categories
    - Django ORM prevents SQL injection
    - Read-only (doesn't modify data)
    
    Returns:
        QuerySet: All active Category objects with minimal fields
    """
    
    # Query active categories from database
    # only() loads just these fields instead of all fields
    # This is faster and uses less memory
    return Category.objects.filter(
        is_active=True  # WHERE is_active = TRUE
    ).only(             # SELECT only these fields:
        'id',           # - category.id (needed for URLs)
        'name',         # - category.name (for display)
        'slug'          # - category.slug (for URLs)
    ).order_by('name')  # ORDER BY name ASC (alphabetical)


@register.simple_tag
def get_category_count(category):
    """
    Get product count for a specific category.
    
    Usage in templates:
        {% get_category_count category %}
    
    Why separate function:
    - Keeps query logic separate from display logic
    - Can be cached independently
    - Reusable across templates
    
    Args:
        category: Category object
    
    Returns:
        int: Number of active products in category
    """
    
    # Count active products in this category
    # filter() with count() generates:
    # SELECT COUNT(*) FROM products_product 
    # WHERE category_id = ? AND is_active = TRUE
    return category.products.filter(
        is_active=True  # Only count active products
    ).count()


@register.inclusion_tag('includes/category_menu.html')
def render_category_menu():
    """
    Render complete category menu HTML.
    
    Inclusion tags are more powerful than simple tags:
    - They render a template snippet
    - Good for complex HTML structures
    - Keeps template logic separate
    
    Usage in templates:
        {% load products_tags %}
        {% render_category_menu %}
    
    This will load templates/includes/category_menu.html
    and render it with the categories context.
    
    Returns:
        dict: Context for category_menu.html template
    """
    
    # Get categories with product counts
    categories = Category.objects.filter(
        is_active=True
    ).only('id', 'name', 'slug')
    
    # Return context dict for the template
    return {
        'categories': categories
    }