# products/services.py

"""
Platzi Fake API Service - Enhanced Product Integration

This service integrates with the Platzi Fake Store API, which provides
a comprehensive e-commerce data set perfect for building and testing
shopping platforms.

API Documentation: https://fakeapi.platzi.com/en/rest/introduction
Base URL: https://api.escuelajs.co/api/v1

The API provides realistic e-commerce data including:
- Products with multiple images
- Hierarchical categories
- Price range filtering
- Title search
- Pagination support

Why this service layer approach matters:
When you eventually move to your own database, you'll only need to change
this file. Your views and templates continue working unchanged because
they interact with ProductData objects, not raw API responses.
"""

import requests
from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.core.cache import cache
import logging

# Set up logging to track API issues
logger = logging.getLogger(__name__)


class ProductData:
    """
    Represents a product from the API as a Python object
    
    This class takes the JSON response from the API and converts it into
    a clean Python object that templates can use easily. The benefit is that
    your templates work with product.title, product.price, etc. just like
    they would with Django database models.
    
    When you switch to database models later, templates don't need to change
    because the attribute names match.
    """
    
    def __init__(self, api_data: Dict[str, Any]):
        """
        Initialize product from API JSON response
        
        API returns data like this:
        {
            "id": 4,
            "title": "Handmade Fresh Table",
            "price": 687,
            "description": "Andy shoes are designed...",
            "images": [
                "https://picsum.photos/640/640?r=2677",
                "https://picsum.photos/640/640?r=3403",
                "https://picsum.photos/640/640?r=6835"
            ],
            "creationAt": "2024-01-20T00:00:00.000Z",
            "updatedAt": "2024-01-20T00:00:00.000Z",
            "category": {
                "id": 5,
                "name": "Others",
                "image": "https://picsum.photos/640/640?r=2361",
                "creationAt": "2024-01-20T00:00:00.000Z",
                "updatedAt": "2024-01-20T00:00:00.000Z"
            }
        }
        """
        # Basic product information
        self.id = api_data.get('id')
        self.title = api_data.get('title', 'Unnamed Product')
        self.name = self.title  # Alias for template compatibility
        
        # Price - convert to Decimal for accurate money calculations
        # Never use float for money! Decimal avoids rounding errors
        price_value = api_data.get('price', 0)
        self.price = Decimal(str(price_value))
        
        # Description
        self.description = api_data.get('description', 'No description available.')
        
        # Generate short description (first 150 characters)
        # This is perfect for product cards where space is limited
        if len(self.description) > 150:
            self.short_description = self.description[:147] + '...'
        else:
            self.short_description = self.description
        
        # Images - API provides array of image URLs
        # Filter out any invalid URLs (empty strings or non-HTTP URLs)
        self.images = api_data.get('images', [])
        self.images = [
            img for img in self.images 
            if img and isinstance(img, str) and img.startswith('http')
        ]
        
        # Remove any duplicate images
        self.images = list(dict.fromkeys(self.images))
        
        # Category information
        # API returns nested category object
        category_data = api_data.get('category', {})
        if isinstance(category_data, dict):
            self.category_id = category_data.get('id')
            self.category_name = category_data.get('name', 'Uncategorized')
            self.category_image = category_data.get('image', '')
        else:
            # Fallback if category data is missing or malformed
            self.category_id = None
            self.category_name = 'Uncategorized'
            self.category_image = ''
        
        # Generate URL-friendly slug from title
        # "Handmade Fresh Table" becomes "handmade-fresh-table"
        # This creates clean URLs like /products/handmade-fresh-table/
        from django.utils.text import slugify
        self.slug = slugify(self.title)
        
        # Timestamps
        self.created_at = api_data.get('creationAt', '')
        self.updated_at = api_data.get('updatedAt', '')
        
        # Simulate fields that a real e-commerce product would have
        # The API doesn't provide these, so we add reasonable defaults
        self.is_active = True  # Assume all API products are active
        self.is_featured = False  # We'll mark some as featured in our logic
        self.stock = 50  # Fake stock number since API doesn't track inventory
        self.is_in_stock = True
        self.sale_price = None  # No sale data from this API
        
        # Calculate if this should be "featured"
        # We'll mark products with certain IDs as featured for variety
        # In a real app, this would be a database field admins can set
        if self.id and self.id % 7 == 0:  # Every 7th product is featured
            self.is_featured = True
    
    @property
    def primary_image(self):
        """
        Get the main product image (first in the array)
        
        Returns URL string or None if no images available
        Templates can safely use: {{ product.primary_image }}
        """
        return self.images[0] if self.images else None
    
    @property
    def all_images(self):
        """
        Get all product images for gallery display
        Returns list of image URLs
        """
        return self.images
    
    @property
    def get_display_price(self):
        """
        Returns the price to display to customers
        
        In a real app with sales, this would check if sale_price exists
        and return that instead. For now, just returns regular price.
        
        This property maintains compatibility with templates expecting
        get_display_price from database models.
        """
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """Check if product has an active sale price"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    def get_absolute_url(self):
        """
        Generate URL for this product's detail page
        
        Returns: String like '/products/42/'
        Templates use this in: <a href="{{ product.get_absolute_url }}">
        """
        from django.urls import reverse
        return reverse('products:product-detail', kwargs={'product_id': self.id})
    
    def __str__(self):
        """String representation for debugging and logging"""
        return f"{self.title} (₹{self.price})"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"<ProductData: {self.id} - {self.title}>"


class CategoryData:
    """
    Represents a product category from the API
    
    Categories organize products into browsable groups.
    Think of them like departments in a physical store.
    """
    
    def __init__(self, api_data: Dict[str, Any]):
        """
        Initialize category from API response
        
        API returns:
        {
            "id": 1,
            "name": "Clothes",
            "image": "https://picsum.photos/640/640?r=9899",
            "creationAt": "2024-01-20T00:00:00.000Z",
            "updatedAt": "2024-01-20T00:00:00.000Z"
        }
        """
        self.id = api_data.get('id')
        self.name = api_data.get('name', 'Unnamed Category')
        self.image = api_data.get('image', '')
        
        # Generate URL-friendly slug
        from django.utils.text import slugify
        self.slug = slugify(self.name)
        
        # Description (API doesn't provide this, so we generate one)
        self.description = f"Browse our selection of {self.name.lower()}"
        
        # Timestamps
        self.created_at = api_data.get('creationAt', '')
        self.updated_at = api_data.get('updatedAt', '')
        
        # Status
        self.is_active = True
    
    def get_absolute_url(self):
        """Generate URL for category product listing"""
        from django.urls import reverse
        return reverse('products:category-products', kwargs={'category_id': self.id})
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<CategoryData: {self.id} - {self.name}>"


class PlatziAPIService:
    """
    Service class for Platzi Fake Store API
    
    This class provides methods to fetch products and categories from the API.
    All API communication is centralized here, making it easy to:
    - Add caching to improve performance
    - Handle errors consistently
    - Log API usage for monitoring
    - Switch to database later with minimal changes
    
    All methods are class methods because we don't need to create instances.
    We just call PlatziAPIService.get_products() directly.
    """
    
    BASE_URL = 'https://api.escuelajs.co/api/v1'
    CACHE_TIMEOUT = 300  # Cache for 5 minutes
    REQUEST_TIMEOUT = 10  # Wait max 10 seconds for API response
    
    @classmethod
    def _make_request(cls, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Make HTTP request to API with error handling
        
        This private method (note the underscore) handles all the messy
        details of making HTTP requests, handling timeouts, and parsing JSON.
        
        All other methods call this instead of duplicating request logic.
        
        Parameters:
            endpoint: API path like '/products' or '/products/1'
            params: Query parameters like {'limit': 10, 'offset': 0}
        
        Returns:
            Parsed JSON response (dict or list), or None if error occurred
        """
        try:
            url = f"{cls.BASE_URL}{endpoint}"
            
            logger.debug(f"API Request: {url} with params: {params}")
            
            # Make the HTTP GET request
            response = requests.get(
                url, 
                params=params, 
                timeout=cls.REQUEST_TIMEOUT
            )
            
            # Raise exception for 4xx or 5xx status codes
            response.raise_for_status()
            
            # Parse and return JSON
            data = response.json()
            logger.debug(f"API Response: Received {len(data) if isinstance(data, list) else 1} items")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"API timeout: {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to API: {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e}")
            return None
            
        except ValueError as e:
            # JSON parsing failed
            logger.error(f"Invalid JSON from API: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected API error: {e}")
            return None
    
    @classmethod
    def get_products(cls, limit: int = 20, offset: int = 0) -> List[ProductData]:
        """
        Fetch products with pagination
        
        The API supports offset and limit for pagination:
        - offset: How many products to skip (for going to page 2, 3, etc.)
        - limit: How many products to return
        
        Example:
            Page 1: get_products(limit=20, offset=0)  # Products 1-20
            Page 2: get_products(limit=20, offset=20) # Products 21-40
            Page 3: get_products(limit=20, offset=40) # Products 41-60
        
        Returns:
            List of ProductData objects
        """
        cache_key = f'platzi_products_{limit}_{offset}'
        cached = cache.get(cache_key)
        
        if cached:
            logger.debug(f"Cache hit: {cache_key}")
            return cached
        
        logger.debug(f"Cache miss: {cache_key}, fetching from API")
        
        params = {'limit': limit, 'offset': offset}
        data = cls._make_request('/products', params=params)
        
        if data is None:
            return []
        
        products = [ProductData(item) for item in data if isinstance(item, dict)]
        
        cache.set(cache_key, products, cls.CACHE_TIMEOUT)
        
        return products
    
    @classmethod
    def get_product_by_id(cls, product_id: int) -> Optional[ProductData]:
        """
        Fetch single product by ID
        
        Example:
            product = PlatziAPIService.get_product_by_id(5)
            if product:
                print(f"Found: {product.title}")
            else:
                print("Product not found")
        """
        cache_key = f'platzi_product_{product_id}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        data = cls._make_request(f'/products/{product_id}')
        
        if data is None or not isinstance(data, dict):
            return None
        
        product = ProductData(data)
        cache.set(cache_key, product, cls.CACHE_TIMEOUT)
        
        return product
    
    @classmethod
    def get_categories(cls) -> List[CategoryData]:
        """
        Fetch all categories
        
        Returns:
            List of CategoryData objects
        """
        cache_key = 'platzi_categories'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        data = cls._make_request('/categories')
        
        if data is None:
            return []
        
        categories = [CategoryData(item) for item in data if isinstance(item, dict)]
        
        cache.set(cache_key, categories, cls.CACHE_TIMEOUT)
        
        return categories
    
    @classmethod
    def get_category_by_id(cls, category_id: int) -> Optional[CategoryData]:
        """Fetch single category by ID"""
        cache_key = f'platzi_category_{category_id}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        data = cls._make_request(f'/categories/{category_id}')
        
        if data is None or not isinstance(data, dict):
            return None
        
        category = CategoryData(data)
        cache.set(cache_key, category, cls.CACHE_TIMEOUT)
        
        return category
    
    @classmethod
    def get_products_by_category(cls, category_id: int, limit: int = 20, offset: int = 0) -> List[ProductData]:
        """
        Fetch products in specific category
        
        The API provides a special endpoint for this:
        /categories/{id}/products
        
        This is more efficient than fetching all products and filtering.
        """
        cache_key = f'platzi_cat_products_{category_id}_{limit}_{offset}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        params = {'limit': limit, 'offset': offset}
        data = cls._make_request(f'/categories/{category_id}/products', params=params)
        
        if data is None:
            return []
        
        products = [ProductData(item) for item in data if isinstance(item, dict)]
        
        cache.set(cache_key, products, cls.CACHE_TIMEOUT)
        
        return products
    
    @classmethod
    def search_products(cls, query: str, limit: int = 20) -> List[ProductData]:
        """
        Search products by title
        
        The API supports title search with this endpoint:
        /products/?title=<search_term>
        
        Example:
            results = PlatziAPIService.search_products("table")
            # Returns all products with "table" in the title
        """
        if not query or not query.strip():
            return cls.get_products(limit=limit)
        
        cache_key = f'platzi_search_{query.lower()}_{limit}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        params = {'title': query, 'limit': limit}
        data = cls._make_request('/products', params=params)
        
        if data is None:
            return []
        
        products = [ProductData(item) for item in data if isinstance(item, dict)]
        
        cache.set(cache_key, products, cls.CACHE_TIMEOUT)
        
        return products
    
    @classmethod
    def filter_by_price_range(cls, min_price: int, max_price: int, limit: int = 20) -> List[ProductData]:
        """
        Filter products by price range
        
        The API supports price filtering:
        /products/?price_min=100&price_max=500
        
        Useful for "Under ₹1000" type filters
        """
        cache_key = f'platzi_price_{min_price}_{max_price}_{limit}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        params = {
            'price_min': min_price,
            'price_max': max_price,
            'limit': limit
        }
        data = cls._make_request('/products', params=params)
        
        if data is None:
            return []
        
        products = [ProductData(item) for item in data if isinstance(item, dict)]
        
        cache.set(cache_key, products, cls.CACHE_TIMEOUT)
        
        return products
    
    @classmethod
    def get_featured_products(cls, limit: int = 8) -> List[ProductData]:
        """
        Get featured products for homepage
        
        Since API doesn't have "featured" flag, we'll take first N products
        In real app, you'd filter by is_featured=True in database
        """
        return cls.get_products(limit=limit, offset=0)


"""
How This Service Integrates With Your App:

1. VIEWS call service methods:
   products = PlatziAPIService.get_products(limit=20)

2. SERVICE fetches from API:
   - Checks cache first (fast!)
   - Makes HTTP request if needed
   - Converts JSON to ProductData objects
   - Caches result for next time

3. VIEWS pass data to templates:
   context = {'products': products}
   return render(request, 'template.html', context)

4. TEMPLATES display data:
   {% for product in products %}
       {{ product.title }} - ₹{{ product.price }}
   {% endfor %}

The magic is that templates don't know or care whether data comes
from API or database. They just use product.title, product.price, etc.

When you switch to database models later, you change the service but
templates stay exactly the same!
"""