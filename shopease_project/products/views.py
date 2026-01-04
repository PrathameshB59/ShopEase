# products/views.py
"""
VIEWS FOR PRODUCTS APP
=======================
Views are the "controller" in MVC architecture.
They handle requests, fetch data from database, and return HTML responses.

Views in this file:
1. home_view - Homepage with featured products
2. ProductListView - List all products
3. CategoryDetailView - Products in a category
4. ProductDetailView - Single product details
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Product, Category, ProductImage


# ============================================================================
# HOME PAGE VIEW
# ============================================================================
def home_view(request):
    """
    HOME PAGE VIEW (Function-Based View)
    =====================================
    Displays the main landing page with:
    - Featured products
    - New arrivals
    - Products on sale
    - Categories
    
    This is what customers see when they visit your website.
    
    Args:
        request (HttpRequest): Contains metadata about the request
            - request.user: Current user (logged in or anonymous)
            - request.method: HTTP method (GET, POST, etc.)
            - request.GET: URL parameters (?page=2)
            - request.POST: Form data
            - request.session: Session data (shopping cart, etc.)
    
    Returns:
        HttpResponse: Rendered HTML page
    """
    
    # FETCH FEATURED PRODUCTS
    # =======================
    # Get products marked as featured by admin
    # .filter() - Query database with conditions
    # is_active=True - Only show active products
    # is_featured=True - Only show featured products
    # .select_related('category') - Optimize query (fetch category in same query)
    # .prefetch_related('images') - Optimize query (fetch images efficiently)
    # [:8] - Limit to 8 products (like SQL LIMIT 8)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').prefetch_related('images')[:8]
    
    
    # FETCH NEW ARRIVALS
    # ==================
    # Get newest products (sorted by creation date)
    # .order_by('-created_at') - Sort by created_at descending (newest first)
    # The minus sign (-) means descending order
    new_arrivals = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
    
    
    # FETCH PRODUCTS ON SALE
    # ======================
    # Get products that have a sale price set
    # .filter(sale_price__isnull=False) - sale_price is NOT NULL
    # __isnull is a field lookup that checks for NULL values
    sale_products = Product.objects.filter(
        is_active=True,
        sale_price__isnull=False  # Has a sale price
    ).select_related('category').prefetch_related('images')[:8]
    
    
    # FETCH ACTIVE CATEGORIES
    # =======================
    # Get all categories that are currently active
    # .annotate() - Add computed field to each category
    # Count('products') - Count how many products in each category
    # We name it 'product_count' for use in template
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('order', 'name')[:8]
    
    
    # PREPARE CONTEXT DATA
    # ====================
    # Context is a dictionary of data passed to the template
    # Template can access these variables: {{ featured_products }}
    context = {
        'featured_products': featured_products,   # For "Featured Products" section
        'new_arrivals': new_arrivals,             # For "New Arrivals" section
        'sale_products': sale_products,           # For "On Sale" section
        'categories': categories,                 # For "Shop by Category" section
        'page_title': 'Welcome to ShopEase',      # Browser tab title
    }
    
    # RENDER TEMPLATE
    # ===============
    # render() function does three things:
    # 1. Takes the request object
    # 2. Loads the template file (products/home.html)
    # 3. Passes context data to template
    # 4. Returns HttpResponse with rendered HTML
    return render(request, 'products/home.html', context)


# ============================================================================
# PRODUCT LIST VIEW
# ============================================================================
class ProductListView(ListView):
    """
    PRODUCT LIST VIEW (Class-Based View)
    =====================================
    Shows all products with filtering, sorting, and pagination.
    
    URL: /products/
    Template: products/product_list.html
    
    Class-based views are reusable and come with built-in functionality.
    ListView automatically handles:
    - Fetching objects from database
    - Pagination
    - Passing data to template
    """
    
    # Which model to query
    model = Product
    
    # Template to render
    template_name = 'products/product_list.html'
    
    # Variable name in template (default would be 'product_list' or 'object_list')
    context_object_name = 'products'
    
    # How many products per page
    paginate_by = 12
    
    def get_queryset(self):
        """
        GET QUERYSET METHOD
        ===================
        Customize which products to show.
        This method is called automatically by Django.
        
        Returns:
            QuerySet: Filtered and sorted products
        """
        
        # Start with all active products
        queryset = Product.objects.filter(is_active=True)
        
        # OPTIMIZATION
        # ============
        # .select_related('category') - Fetch category in same query (SQL JOIN)
        # .prefetch_related('images') - Fetch all images efficiently
        # This prevents N+1 query problem (hundreds of separate queries)
        queryset = queryset.select_related('category').prefetch_related('images')
        
        # FILTERING BY CATEGORY
        # =====================
        # Check if 'category' parameter in URL: ?category=electronics
        category_slug = self.request.GET.get('category')
        if category_slug:
            # Filter products by category slug
            queryset = queryset.filter(category__slug=category_slug)
        
        # SORTING
        # =======
        # Check if 'sort' parameter in URL: ?sort=price_low
        sort = self.request.GET.get('sort', 'newest')  # Default: newest first
        
        if sort == 'price_low':
            # Sort by price: lowest first
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            # Sort by price: highest first
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            # Sort alphabetically
            queryset = queryset.order_by('name')
        elif sort == 'newest':
            # Sort by date: newest first (default)
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            # Sort by views: most viewed first
            queryset = queryset.order_by('-views')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        GET CONTEXT DATA METHOD
        =======================
        Add extra data to template context.
        
        Returns:
            dict: Context dictionary with additional data
        """
        # Get the default context from ListView
        context = super().get_context_data(**kwargs)
        
        # Add list of all categories for filter sidebar
        context['categories'] = Category.objects.filter(is_active=True).order_by('name')
        
        # Add current filter/sort values (so template can show active filters)
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        
        # Add page title
        context['page_title'] = 'All Products'
        
        return context


# ============================================================================
# CATEGORY DETAIL VIEW
# ============================================================================
class CategoryDetailView(DetailView):
    """
    CATEGORY DETAIL VIEW (Class-Based View)
    ========================================
    Shows all products in a specific category.
    
    URL: /products/category/electronics/
    Template: products/category_detail.html
    
    DetailView automatically:
    - Fetches one object based on slug
    - Passes it to template
    - Returns 404 if not found
    """
    
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        """
        Add products in this category to context.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the category object (automatically fetched by DetailView)
        category = self.get_object()
        
        # Get all active products in this category
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category').prefetch_related('images')
        
        # SORTING (same as ProductListView)
        sort = self.request.GET.get('sort', 'newest')
        
        if sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
        elif sort == 'name':
            products = products.order_by('name')
        elif sort == 'newest':
            products = products.order_by('-created_at')
        elif sort == 'popular':
            products = products.order_by('-views')
        
        # Add to context
        context['products'] = products
        context['current_sort'] = sort
        context['page_title'] = f'{category.name} - Products'
        
        return context


# ============================================================================
# PRODUCT DETAIL VIEW
# ============================================================================
class ProductDetailView(DetailView):
    """
    PRODUCT DETAIL VIEW (Class-Based View)
    =======================================
    Shows detailed information about a single product.
    
    URL: /products/iphone-15-pro/
    Template: products/product_detail.html
    
    Features:
    - Product details (name, description, price, stock)
    - Image gallery
    - Add to cart button
    - Related products
    - Increment view count
    """
    
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """
        Optimize query to fetch related data.
        """
        return Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('images')
    
    def get_object(self):
        """
        Get the product and increment view count.
        """
        # Get the product using parent method
        product = super().get_object()
        
        # Increment view count
        # update_fields prevents updating unnecessary fields
        product.views += 1
        product.save(update_fields=['views'])
        
        return product
    
    def get_context_data(self, **kwargs):
        """
        Add related products and images to context.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the product
        product = self.get_object()
        
        # Get all product images (ordered by 'order' field)
        context['images'] = product.images.all().order_by('order')
        
        # Get related products (same category, different product)
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(
            id=product.id  # Don't include current product
        ).select_related('category').prefetch_related('images')[:4]
        
        context['related_products'] = related_products
        context['page_title'] = f'{product.name} - ShopEase'
        
        return context


# ============================================================================
# QUERY OPTIMIZATION EXPLANATION
# ============================================================================
"""
WHY USE select_related() and prefetch_related()?
=================================================

Without optimization:
---------------------
# Get 10 products
products = Product.objects.all()[:10]

# In template, when you loop:
{% for product in products %}
    {{ product.category.name }}  ← Triggers separate query for EACH product!
{% endfor %}

Result: 1 query + 10 queries = 11 total queries (N+1 problem)


With select_related():
----------------------
# Get 10 products WITH their categories in ONE query
products = Product.objects.select_related('category').all()[:10]

# In template:
{% for product in products %}
    {{ product.category.name }}  ← No extra query! Data already loaded.
{% endfor %}

Result: 1 query total (uses SQL JOIN)


With prefetch_related():
------------------------
# Get 10 products WITH all their images efficiently
products = Product.objects.prefetch_related('images').all()[:10]

# In template:
{% for product in products %}
    {% for image in product.images.all %}  ← No extra queries!
    {% endfor %}
{% endfor %}

Result: 2 queries total (1 for products, 1 for all images)


WHEN TO USE WHICH:
==================
- select_related(): For ForeignKey and OneToOne (single related object)
  Example: product.category, order.user

- prefetch_related(): For ManyToMany and reverse ForeignKey (multiple related objects)
  Example: product.images, category.products

This makes your site MUCH faster!
"""
# products/views.py
# This file handles all product-related views for the customer-facing side

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category, ProductImage

def home(request):
    """
    Home page view - displays featured products and all categories
    
    What this does:
    1. Gets all active products marked as featured (is_featured=True)
    2. Gets all active categories for the navigation
    3. Passes them to the home template
    """
    # Get only featured products that are active and in stock
    # order_by('-created_at') shows newest products first
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True,
        stock__gt=0  # gt means "greater than" - only show products with stock
    ).order_by('-created_at')[:8]  # [:8] limits to 8 products
    
    # Get all active categories ordered by their order field
    categories = Category.objects.filter(is_active=True).order_by('order')
    
    # Context is a dictionary we send to the template
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'page_title': 'Welcome to ShopEase'
    }
    
    return render(request, 'products/home.html', context)


def product_list(request):
    """
    Product listing page - shows all products with filtering options
    
    This view handles:
    1. Displaying all products
    2. Filtering by category
    3. Searching products
    4. Pagination (showing products across multiple pages)
    """
    # Start with all active products
    products = Product.objects.filter(is_active=True, stock__gt=0)
    
    # Get the category slug from URL parameters (?category=electronics)
    category_slug = request.GET.get('category')
    selected_category = None
    
    # If a category is selected, filter products by that category
    if category_slug:
        # get_object_or_404 returns the category or shows 404 error page if not found
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        # Filter products to only show those in this category
        products = products.filter(category=selected_category)
    
    # Search functionality - check if there's a search query
    search_query = request.GET.get('search')
    if search_query:
        # Filter products where name or description contains the search term
        # icontains means "contains" but case-insensitive (iPhone = iphone = IPHONE)
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            description__icontains=search_query
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', '-created_at')  # Default: newest first
    
    # Dictionary of allowed sort options (prevents users from sorting by invalid fields)
    valid_sorts = {
        'price_low': 'price',           # Cheapest first
        'price_high': '-price',         # Most expensive first
        'name_asc': 'name',             # A to Z
        'name_desc': '-name',           # Z to A
        'newest': '-created_at',        # Newest first
        'oldest': 'created_at'          # Oldest first
    }
    
    # Apply sorting if it's a valid option
    if sort_by in valid_sorts:
        products = products.order_by(valid_sorts[sort_by])
    else:
        products = products.order_by('-created_at')  # Default sort
    
    # Pagination - divide products into pages (12 per page)
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')  # Get current page number from URL
    page_obj = paginator.get_page(page_number)  # Get the products for this page
    
    # Get all categories for the filter sidebar
    categories = Category.objects.filter(is_active=True).order_by('order')
    
    context = {
        'products': page_obj,  # This contains products for current page + pagination info
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'page_title': f'{selected_category.name} Products' if selected_category else 'All Products'
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Product detail page - shows one product with all its information
    
    Parameters:
    - slug: The URL-friendly version of product name (e.g., "blue-t-shirt")
    
    What this does:
    1. Gets the specific product by its slug
    2. Gets all images for this product
    3. Gets related products (same category)
    """
    # Get the product or show 404 if not found
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get all images for this product, ordered by the 'order' field
    # Primary image first (is_primary=True)
    product_images = product.images.all().order_by('-is_primary', 'order')
    
    # Get related products (same category, exclude current product)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock__gt=0
    ).exclude(id=product.id)[:4]  # Show 4 related products
    
    # Check if product has a sale price
    discount_percentage = 0
    if product.sale_price:
        # Calculate discount percentage
        discount = product.price - product.sale_price
        discount_percentage = int((discount / product.price) * 100)
    
    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
        'discount_percentage': discount_percentage,
        'page_title': product.name
    }
    
    return render(request, 'products/product_detail.html', context)


def category_list(request):
    """
    Categories page - shows all available categories
    
    This is useful for mobile users or as a dedicated categories page
    Shows each category with product count
    """
    # Get all active categories
    categories = Category.objects.filter(is_active=True).order_by('order')
    
    # For each category, we can access category.product_count
    # (This is defined in the Category model as a method)
    
    context = {
        'categories': categories,
        'page_title': 'Shop by Category'
    }
    
    return render(request, 'products/category_list.html', context)