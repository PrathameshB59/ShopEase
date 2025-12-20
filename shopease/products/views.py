# products/views.py

"""
Product Views - Updated for Platzi API

These views handle all product-related pages on your site.
They fetch data from the Platzi API via our service layer and
render responsive templates that work beautifully on any device.
"""

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .services import PlatziAPIService


def home(request):
    """
    Homepage - Your store's front entrance
    
    URL: /
    
    The homepage is like your store's window display. It should entice
    visitors to explore more by showing your best products and making
    navigation easy.
    
    We display:
    - Featured products (newest/best sellers)
    - Category quick links
    - Welcome message
    - Search bar (in navigation)
    """
    # Get featured products for the hero section
    # These appear prominently on the homepage
    featured_products = PlatziAPIService.get_featured_products(limit=8)
    
    # Get all categories for the category grid
    # Showing categories helps visitors find what they're looking for
    all_categories = PlatziAPIService.get_categories()
    
    # We'll show the first 6 categories on homepage
    # In a real store, you might want to mark certain categories as "featured"
    categories = all_categories[:6] if all_categories else []
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'page_title': 'Welcome to ShopEase',
        'is_home': True,  # Template can use this to add special styling
    }
    
    return render(request, 'home.html', context)


def product_list(request):
    """
    Product listing page with filtering and pagination
    
    URL: /products/
    URL with category: /products/?category=3
    URL with page: /products/?page=2
    
    This is your main shop page where customers browse all products.
    Supports:
    - Pagination (12 products per page)
    - Category filtering
    - Responsive grid layout
    
    The pagination math:
    - Page 1: offset=0, shows products 1-12
    - Page 2: offset=12, shows products 13-24
    - Page 3: offset=24, shows products 25-36
    """
    # Get filter parameters from URL query string
    category_id = request.GET.get('category')
    page_number = request.GET.get('page', 1)
    
    # Products per page - adjust this number to your preference
    # 12 is good because it divides evenly into responsive grid (4 cols, 3 cols, 2 cols, 1 col)
    per_page = 12
    
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1
    
    # Calculate offset for API pagination
    offset = (page_number - 1) * per_page
    
    # Fetch products based on whether category filter is applied
    if category_id:
        try:
            category_id = int(category_id)
            # Fetch products in specific category
            # We fetch extra to know if there are more pages
            products = PlatziAPIService.get_products_by_category(
                category_id, 
                limit=per_page + 1,  # Fetch one extra to check if there's a next page
                offset=offset
            )
            
            # Get category info for display
            current_category = PlatziAPIService.get_category_by_id(category_id)
            
            if not current_category:
                messages.warning(request, 'Category not found.')
                category_id = None
                current_category = None
                # Fall back to all products
                products = PlatziAPIService.get_products(limit=per_page + 1, offset=offset)
            
        except (ValueError, TypeError):
            # Invalid category ID
            messages.error(request, 'Invalid category.')
            category_id = None
            current_category = None
            products = PlatziAPIService.get_products(limit=per_page + 1, offset=offset)
    else:
        # No filter, show all products
        current_category = None
        products = PlatziAPIService.get_products(limit=per_page + 1, offset=offset)
    
    # Check if there's a next page
    has_next = len(products) > per_page
    
    # Only show the products for current page (not the extra one we fetched)
    display_products = products[:per_page]
    
    # Calculate total pages (approximate, since API doesn't tell us total count)
    # This is a limitation of the API, but we work around it
    has_previous = page_number > 1
    
    # Get all categories for the filter sidebar
    categories = PlatziAPIService.get_categories()
    
    # Build page title
    if current_category:
        page_title = current_category.name
    else:
        page_title = 'All Products'
    
    context = {
        'products': display_products,
        'categories': categories,
        'current_category': current_category,
        'page_title': page_title,
        # Pagination info
        'page_number': page_number,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page': page_number + 1,
        'previous_page': page_number - 1,
        # For maintaining filters in pagination links
        'category_filter': category_id,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, product_id):
    """
    Product detail page - Full information about one product
    
    URL: /products/<id>/
    Example: /products/42/
    
    This is where customers decide whether to buy. Show:
    - Multiple product images in a gallery
    - Full description
    - Price and availability
    - Add to cart button
    - Related products
    
    If product doesn't exist, gracefully redirect to product list with message.
    """
    # Fetch the product
    product = PlatziAPIService.get_product_by_id(product_id)
    
    if not product:
        messages.error(request, 'Product not found.')
        from django.shortcuts import redirect
        return redirect('products:product-list')
    
    # Fetch related products (from same category)
    # This helps increase sales through "you might also like" suggestions
    related_products = []
    if product.category_id:
        # Get products from same category
        all_category_products = PlatziAPIService.get_products_by_category(
            product.category_id,
            limit=20  # Get more so we have options after filtering
        )
        
        # Filter out the current product and take first 4
        related_products = [
            p for p in all_category_products 
            if p.id != product.id
        ][:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'page_title': product.title,
    }
    
    return render(request, 'products/product_detail.html', context)


def category_list(request):
    """
    Display all categories as browsable cards
    
    URL: /categories/
    
    This page shows all product categories in a grid layout.
    Each category card shows:
    - Category image
    - Category name
    - Link to view products in that category
    
    Think of this like the directory in a mall showing all the different stores.
    """
    categories = PlatziAPIService.get_categories()
    
    context = {
        'categories': categories,
        'page_title': 'Shop by Category',
    }
    
    return render(request, 'products/category_list.html', context)


def search_products(request):
    """
    Search products by keyword
    
    URL: /products/search/?q=table
    
    This handles the search functionality. The Platzi API supports
    title-based searching, so we pass the query to the API.
    
    Query parameters:
    - q: The search term (what user typed in search box)
    - page: Page number for paginated results
    """
    # Get search query from URL
    query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1
    
    per_page = 12
    offset = (page_number - 1) * per_page
    
    if query:
        # Perform search via API
        # Note: API's search is title-only, doesn't search description
        # For database later, you can search both title and description
        all_results = PlatziAPIService.search_products(query, limit=100)
        
        # Manual pagination since we got all results
        start_idx = offset
        end_idx = offset + per_page
        products = all_results[start_idx:end_idx]
        has_next = end_idx < len(all_results)
        has_previous = page_number > 1
        
        # Show result count message
        if all_results:
            messages.success(request, f'Found {len(all_results)} products matching "{query}"')
        else:
            messages.warning(request, f'No products found matching "{query}"')
    else:
        # No query, show recent products
        products = PlatziAPIService.get_products(limit=per_page, offset=offset)
        has_next = len(products) == per_page
        has_previous = page_number > 1
    
    context = {
        'products': products,
        'search_query': query,
        'page_title': f'Search: {query}' if query else 'Search Products',
        # Pagination
        'page_number': page_number,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page': page_number + 1,
        'previous_page': page_number - 1,
    }
    
    return render(request, 'products/search_results.html', context)


def price_filter(request):
    """
    Filter products by price range
    
    URL: /products/filter/?min=100&max=1000
    
    The Platzi API supports price range filtering, which is super useful
    for customers with specific budgets.
    
    Common price ranges might be:
    - Under ₹500
    - ₹500 - ₹1000
    - ₹1000 - ₹5000
    - Over ₹5000
    """
    try:
        min_price = int(request.GET.get('min', 0))
        max_price = int(request.GET.get('max', 10000))
    except (ValueError, TypeError):
        min_price = 0
        max_price = 10000
    
    products = PlatziAPIService.filter_by_price_range(
        min_price=min_price,
        max_price=max_price,
        limit=50
    )
    
    # Paginate results
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    
    try:
        paginated_products = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_products = paginator.page(1)
    
    context = {
        'products': paginated_products,
        'min_price': min_price,
        'max_price': max_price,
        'page_title': f'Products ₹{min_price} - ₹{max_price}',
    }
    
    return render(request, 'products/product_list.html', context)


"""
View Patterns You're Learning:

1. LIST VIEW (product_list, category_list):
   - Fetch collection of items
   - Apply filters based on URL parameters
   - Paginate results
   - Render in grid/list layout

2. DETAIL VIEW (product_detail):
   - Fetch single item by ID
   - Handle 404 gracefully if not found
   - Show related items
   - Provide clear call-to-action (Add to Cart)

3. SEARCH VIEW (search_products):
   - Get search query from user
   - Filter items based on query
   - Show result count
   - Display results in same format as list view

4. FILTER VIEW (price_filter):
   - Get filter criteria from URL
   - Apply filters to data
   - Show filtered results
   - Allow combining filters

These patterns are universal in web development. Master them here,
use them everywhere. User list? Same pattern. Order list? Same pattern.
Blog posts? Same pattern.

The service layer keeps views clean. Views focus on:
- Getting user input (request.GET, request.POST)
- Fetching data (via service)
- Preparing context
- Rendering templates

All the API complexity is hidden in the service layer.
When you switch to database, views barely change!
"""