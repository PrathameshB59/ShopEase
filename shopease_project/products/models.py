# products/models.py
"""
PRODUCT MODELS
===============
This file defines three models for managing products in our e-commerce store:
1. Category - Product categories (Electronics, Clothing, Books, etc.)
2. Product - Individual products with pricing, stock, descriptions
3. ProductImage - Multiple images for each product

These models work together:
Category (1) -----> (Many) Products (1) -----> (Many) ProductImages

Example:
- Category: "Electronics"
  - Product: "iPhone 15 Pro"
    - ProductImage: Front view
    - ProductImage: Back view
    - ProductImage: Side view
"""

# Import Django's models module - contains all field types
from django.db import models

# Import Django's timezone utilities for timestamps
from django.utils import timezone

# Import slugify to create URL-friendly strings
# Example: "Blue T-Shirt" becomes "blue-t-shirt"
from django.utils.text import slugify

# Import settings to access AUTH_USER_MODEL
from django.conf import settings

# Import reverse for generating URLs from view names
from django.urls import reverse


# ============================================================================
# CATEGORY MODEL
# ============================================================================
class Category(models.Model):
    """
    PRODUCT CATEGORY MODEL
    =======================
    Organizes products into categories for easy browsing.
    
    Database table: products_category
    
    Examples:
    - Electronics
    - Men's Clothing
    - Women's Clothing
    - Books & Media
    - Home & Kitchen
    - Sports & Outdoors
    
    Each product belongs to one category.
    Each category can have many products.
    """
    
    # NAME FIELD
    # ===========
    # CharField: Stores short text (up to max_length characters)
    # max_length=100: Category name can be up to 100 characters
    # unique=True: No two categories can have the same name
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name (e.g., Electronics, Clothing)'
    )
    
    # SLUG FIELD
    # ===========
    # A slug is a URL-friendly version of the name
    # Example: "Men's Clothing" becomes "mens-clothing"
    # Used in URLs: yoursite.com/category/mens-clothing
    # unique=True: Each category needs unique URL
    # blank=True: Can be empty when creating (we'll auto-generate it)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text='URL-friendly version of name (auto-generated)'
    )
    
    # DESCRIPTION FIELD
    # ==================
    # TextField: Stores long text (no character limit)
    # blank=True: Field not required
    # null=True: Can be NULL in database
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Description of what products belong in this category'
    )
    
    # CATEGORY IMAGE
    # ===============
    # ImageField: Stores image files
    # upload_to='categories/': Images saved in media/categories/ folder
    # blank=True, null=True: Image is optional
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Category thumbnail image'
    )
    
    # IS ACTIVE FIELD
    # ================
    # BooleanField: True or False value
    # default=True: Categories are active by default
    # If False, category won't show on website (soft delete)
    is_active = models.BooleanField(
        default=True,
        help_text='Is this category visible on the website?'
    )
    
    # ORDER FIELD
    # ============
    # IntegerField: Stores whole numbers
    # default=0: Default order is 0
    # Used to control display order on website
    # Lower numbers appear first (0, 1, 2, 3...)
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    
    # TIMESTAMPS
    # ===========
    # Track when category was created and last updated
    # auto_now_add=True: Set automatically when created (never changes)
    # auto_now=True: Updates automatically every time category is saved
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # META CLASS
    # ===========
    # Defines metadata about the model
    class Meta:
        # Plural name in admin interface
        # By default, Django would show "Categorys" (wrong!)
        # We set it to "Categories" (correct!)
        verbose_name_plural = 'Categories'
        
        # Default ordering when fetching categories
        # ['order', 'name'] means: sort by order first, then by name
        # Categories with order=0 come first, then order=1, etc.
        # Within same order, sort alphabetically by name
        ordering = ['order', 'name']
    
    # STRING REPRESENTATION
    # ======================
    # How the category appears when printed or shown in admin
    # Example: print(category) shows "Electronics"
    def __str__(self):
        return self.name
    
    # SAVE METHOD OVERRIDE
    # =====================
    # This method runs every time a category is saved
    # We override it to auto-generate the slug from name
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name
        
        How it works:
        1. Check if slug is empty
        2. If empty, generate slug from name using slugify()
        3. Save to database
        
        Example:
        - name = "Men's Clothing"
        - slug = "mens-clothing" (auto-generated)
        """
        if not self.slug:
            # slugify() converts text to URL-friendly format
            # "Men's Clothing" -> "mens-clothing"
            # "Electronics & Gadgets" -> "electronics-gadgets"
            self.slug = slugify(self.name)
        
        # Call the parent class's save method to actually save to database
        super().save(*args, **kwargs)
    
    # CUSTOM METHODS
    # ===============
    
    def get_absolute_url(self):
        """
        Returns the URL to view this category
        Used in templates: {{ category.get_absolute_url }}
        Returns: /products/category/electronics/
        """
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    def product_count(self):
        """
        Count how many active products are in this category
        Returns: Integer (number of products)
        Used in admin and templates to show product count
        """
        return self.product_set.filter(is_active=True).count()
    
    # Set a custom name for this method in admin
    product_count.short_description = 'Products'


# ============================================================================
# PRODUCT MODEL
# ============================================================================
class Product(models.Model):
    """
    PRODUCT MODEL
    ==============
    Represents individual products sold in the store.
    
    Database table: products_product
    
    Contains:
    - Basic info: name, description, SKU
    - Pricing: regular price, sale price
    - Inventory: stock quantity, low stock threshold
    - Organization: category, brand
    - Display: featured products, active/inactive
    - SEO: slug for URLs
    - Media: multiple images through ProductImage model
    
    Example product:
    - Name: "iPhone 15 Pro 256GB"
    - Category: Electronics
    - Price: $999.00
    - Sale Price: $899.00 (10% off!)
    - Stock: 50 units
    - Images: 5 product photos
    """
    
    # BASIC INFORMATION
    # ==================
    
    # Product name
    # Max 200 characters, required field
    name = models.CharField(
        max_length=200,
        help_text='Product name shown to customers'
    )
    
    # URL slug for product page
    # Example: "iphone-15-pro-256gb"
    # unique=True: Each product needs unique URL
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text='URL-friendly version (auto-generated from name)'
    )
    
    # Short description (shown in product listings)
    # Max 300 characters for quick overview
    short_description = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text='Brief description (shown in product cards)'
    )
    
    # Full description (shown on product detail page)
    # TextField = unlimited characters
    description = models.TextField(
        help_text='Full product description with all details'
    )
    
    # PRICING
    # ========
    
    # Regular price
    # DecimalField: Stores numbers with decimal points
    # max_digits=10: Maximum 10 digits total (including decimals)
    # decimal_places=2: Exactly 2 digits after decimal (cents)
    # Example: 999.99, 1234.50, 12345678.99
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Regular price in your currency'
    )
    
    # Sale price (optional discount price)
    # If set, this price shows instead of regular price
    # blank=True, null=True: Sale price is optional
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Discounted price (leave empty if no sale)'
    )
    
    # INVENTORY MANAGEMENT
    # =====================
    
    # Stock quantity
    # How many units are available to sell
    # default=0: Start with 0 stock (must be added manually)
    stock = models.IntegerField(
        default=0,
        help_text='Number of units available'
    )
    
    # Low stock warning threshold
    # When stock drops below this, admin gets warning
    # default=10: Warn when only 10 or fewer items left
    low_stock_threshold = models.IntegerField(
        default=10,
        help_text='Alert when stock drops below this number'
    )
    
    # SKU (Stock Keeping Unit)
    # Unique identifier for inventory management
    # Example: "IPH15-PRO-256-BLK"
    # blank=True, null=True: SKU is optional but recommended
    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text='Stock Keeping Unit (unique product code)'
    )
    
    # ORGANIZATION
    # =============
    
    # Category (Foreign Key relationship)
    # ForeignKey: Links product to one category
    # on_delete=models.SET_NULL: If category deleted, keep product but set category to NULL
    # related_name='products': Access products from category: category.products.all()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        help_text='Product category'
    )
    
    # Brand name
    # Optional field for product brand
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Brand or manufacturer name'
    )
    
    # DISPLAY SETTINGS
    # =================
    
    # Is product active?
    # If False, product won't show on website (soft delete)
    # Useful for temporarily hiding products without deleting
    is_active = models.BooleanField(
        default=True,
        help_text='Is product visible on website?'
    )
    
    # Is product featured?
    # Featured products show on homepage and special sections
    # Only set this for best sellers or promoted items
    is_featured = models.BooleanField(
        default=False,
        help_text='Show on homepage and featured sections?'
    )
    
    # RATINGS & REVIEWS
    # ==================
    
    # Average rating (1.0 to 5.0)
    # FloatField: Stores decimal numbers
    # default=0.0: New products start with 0 rating
    # We'll calculate this from customer reviews
    average_rating = models.FloatField(
        default=0.0,
        help_text='Average customer rating (calculated from reviews)'
    )
    
    # Total number of reviews
    # Used to show "Based on X reviews"
    review_count = models.IntegerField(
        default=0,
        help_text='Total number of customer reviews'
    )
    
    # VIEW COUNT
    # ===========
    # Track how many times product page was viewed
    # Useful for analytics and "trending products"
    views = models.IntegerField(
        default=0,
        help_text='Number of times product page was viewed'
    )
    
    # TIMESTAMPS
    # ===========
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # META CLASS
    # ===========
    class Meta:
        # Default ordering: featured products first, then newest first
        # '-' means descending (reverse order)
        ordering = ['-is_featured', '-created_at']
        
        # Indexes improve database query speed
        # We create indexes on commonly searched/filtered fields
        indexes = [
            models.Index(fields=['slug']),           # Fast lookup by slug
            models.Index(fields=['category']),       # Fast category filtering
            models.Index(fields=['-created_at']),    # Fast "new arrivals" sorting
            models.Index(fields=['is_active']),      # Fast active products filter
        ]
    
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        return self.name
    
    # SAVE METHOD OVERRIDE
    # =====================
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided
        Also auto-generate SKU if not provided
        """
        if not self.slug:
            # Create slug from name
            self.slug = slugify(self.name)
            
            # Handle duplicate slugs by adding number
            # If "blue-shirt" exists, create "blue-shirt-2"
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-generate SKU if not provided
        if not self.sku:
            # Create SKU from name (first 3 letters) + random number
            import random
            prefix = self.name[:3].upper()
            random_num = random.randint(10000, 99999)
            self.sku = f"{prefix}-{random_num}"
            
            # Ensure SKU is unique
            while Product.objects.filter(sku=self.sku).exists():
                random_num = random.randint(10000, 99999)
                self.sku = f"{prefix}-{random_num}"
        
        super().save(*args, **kwargs)
    
    # CUSTOM METHODS
    # ===============
    
    def get_absolute_url(self):
        """
        Get URL for product detail page
        Returns: /products/iphone-15-pro-256gb/
        """
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def get_price(self):
        """
        Get the actual selling price
        If product is on sale, return sale_price
        Otherwise return regular price
        
        Returns: Decimal (the price customer pays)
        """
        if self.sale_price:
            return self.sale_price
        return self.price
    
    def get_discount_percentage(self):
        """
        Calculate discount percentage if on sale
        
        Returns: Integer (percentage) or None if not on sale
        Example: If price=$100, sale_price=$80, returns 20 (20% off)
        """
        if self.sale_price and self.sale_price < self.price:
            # Formula: ((regular - sale) / regular) * 100
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return None
    
    def is_on_sale(self):
        """
        Check if product is currently on sale
        Returns: True if sale_price exists and is less than regular price
        """
        return self.sale_price and self.sale_price < self.price
    
    def is_in_stock(self):
        """
        Check if product is available for purchase
        Returns: True if stock > 0
        """
        return self.stock > 0
    
    def is_low_stock(self):
        """
        Check if stock is running low
        Returns: True if stock is below threshold but not zero
        """
        return 0 < self.stock <= self.low_stock_threshold
    
    def get_primary_image(self):
        """
        Get the main product image
        Returns: ProductImage object or None
        Used to show main image in product listings
        """
        # Try to get image marked as primary
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        
        # If no primary image, return first image
        return self.images.first()
    
    def get_all_images(self):
        """
        Get all product images ordered by their order field
        Returns: QuerySet of ProductImage objects
        """
        return self.images.all().order_by('order')
    
    def increment_views(self):
        """
        Increase view count by 1
        Call this when someone views the product page
        """
        self.views += 1
        self.save(update_fields=['views'])  # Only update views field (more efficient)


# ============================================================================
# PRODUCT IMAGE MODEL
# ============================================================================
class ProductImage(models.Model):
    """
    PRODUCT IMAGE MODEL
    ====================
    Stores multiple images for each product.
    
    Database table: products_productimage
    
    Relationship: Many ProductImages belong to one Product
    
    Features:
    - Multiple images per product
    - One image marked as "primary" (main image)
    - Order control (which image shows first, second, etc.)
    - Alt text for accessibility and SEO
    
    Example:
    Product: "iPhone 15 Pro"
      - Image 1: Front view (primary, order=1)
      - Image 2: Back view (order=2)
      - Image 3: Side view (order=3)
      - Image 4: In hand (order=4)
    """
    
    # PRODUCT RELATIONSHIP
    # =====================
    # ForeignKey: Links image to one product
    # related_name='images': Access images from product: product.images.all()
    # on_delete=models.CASCADE: If product deleted, delete all its images too
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Which product this image belongs to'
    )
    
    # IMAGE FILE
    # ===========
    # ImageField: Stores uploaded image files
    # upload_to='products/': Save in media/products/ folder
    # Django automatically handles file uploads
    image = models.ImageField(
        upload_to='products/',
        help_text='Product photo (recommended: 800x800px or larger)'
    )
    
    # ALT TEXT
    # =========
    # Alternative text for accessibility (screen readers)
    # Also helps with SEO (search engines)
    # Example: "iPhone 15 Pro in Space Black - Front View"
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Description for accessibility and SEO'
    )
    
    # IS PRIMARY
    # ===========
    # BooleanField: Is this the main product image?
    # Only one image per product should be primary
    # Primary image shows in product listings
    is_primary = models.BooleanField(
        default=False,
        help_text='Is this the main product image?'
    )
    
    # DISPLAY ORDER
    # ==============
    # IntegerField: Controls order images appear
    # Lower numbers first (1, 2, 3, 4...)
    # Used in image gallery sliders
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers first)'
    )
    
    # TIMESTAMP
    # ==========
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # META CLASS
    # ===========
    class Meta:
        # Default ordering by display order
        ordering = ['order']
        
        # Verbose names for admin interface
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        # Example: "iPhone 15 Pro - Image 1"
        primary_text = " (Primary)" if self.is_primary else ""
        return f"{self.product.name} - Image {self.order}{primary_text}"
    
    # SAVE METHOD OVERRIDE
    # =====================
    def save(self, *args, **kwargs):
        """
        Ensure only one primary image per product
        If this image is set as primary, unset all other primary images
        """
        if self.is_primary:
            # Unset primary flag from all other images of this product
            # exclude(pk=self.pk) means "all images except this one"
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # If this is the first image for the product, make it primary
        if not ProductImage.objects.filter(product=self.product).exists():
            self.is_primary = True
        
        super().save(*args, **kwargs)
    
    # CUSTOM METHODS
    # ===============
    
    def get_thumbnail_url(self):
        """
        Get URL for thumbnail version of image
        In production, you'd use a library like easy-thumbnails or sorl-thumbnail
        For now, just return the regular image URL
        
        Returns: String (image URL)
        """
        if self.image:
            return self.image.url
        return None


# ============================================================================
# DATABASE RELATIONSHIP SUMMARY
# ============================================================================
"""
RELATIONSHIPS BETWEEN MODELS:
==============================

Category
   ↓ (one-to-many)
Product
   ↓ (one-to-many)
ProductImage

In code:
--------
# Get all products in a category:
electronics = Category.objects.get(name='Electronics')
products = electronics.products.all()

# Get all images for a product:
iphone = Product.objects.get(name='iPhone 15 Pro')
images = iphone.images.all()

# Get primary image:
primary_img = iphone.get_primary_image()

# Get product's category:
category = iphone.category

# Get image's product:
product = image.product
"""