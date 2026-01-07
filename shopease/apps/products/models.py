"""
========================================
PRODUCT MODELS - E-commerce Core
========================================
This module defines the database structure for products, categories, and reviews.

Security Notes:
- All user-uploaded content uses FileField validation
- Slug fields use SlugField for URL safety (prevents XSS)
- Decimal fields for prices prevent floating-point errors
- Foreign keys use on_delete to maintain referential integrity

Performance Notes:
- Indexes on frequently queried fields (slug, is_active, created_at)
- Select_related and prefetch_related in views to prevent N+1 queries
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal


# ==========================================
# CATEGORY MODEL - Product Organization
# ==========================================

class Category(models.Model):
    """
    Product categories for organizing inventory.
    
    Why we need this:
    - Allows customers to browse by category
    - Enables category-specific promotions
    - Improves SEO with category pages
    
    Security:
    - slug field auto-sanitizes for URLs
    - name limited to 100 chars to prevent DOS via huge inputs
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        unique=True,  # Prevents duplicate categories
        help_text="Category name (e.g., 'Electronics', 'Fashion')"
    )
    
    # URL-safe version of name for routing
    # Example: "Men's Clothing" → "mens-clothing"
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="URL-friendly version of name (auto-generated)"
    )
    
    # Optional category description for SEO
    description = models.TextField(
        blank=True,
        help_text="Category description for SEO"
    )
    
    # Category image for display
    image = models.ImageField(
        upload_to='categories/',  # Uploaded to MEDIA_ROOT/categories/
        blank=True,
        null=True,
        help_text="Category thumbnail image"
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive categories are hidden from customers"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"  # Proper pluralization in admin
        ordering = ['name']  # Alphabetical by default
        indexes = [
            models.Index(fields=['slug']),  # Fast category lookups by URL
            models.Index(fields=['is_active']),  # Fast filtering of active categories
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug from name.
        
        Why: Ensures URL-safe slugs without manual input
        Security: slugify() removes special characters, prevents XSS
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        """String representation for admin interface"""
        return self.name
    
    def get_product_count(self):
        """Helper method to count active products in category"""
        return self.products.filter(is_active=True).count()


# ==========================================
# PRODUCT MODEL - Core Product Data
# ==========================================

class Product(models.Model):
    """
    Main product model containing all product information.
    
    Real-world considerations:
    - Prices stored as Decimal to avoid floating-point errors
    - Stock tracking for inventory management
    - Multiple images supported via ProductImage model
    - SEO-friendly fields (slug, meta_description)
    
    Security considerations:
    - User input sanitized via Django ORM
    - File uploads restricted to images only
    - Slugs auto-generated to prevent XSS
    """
    
    # Basic Product Information
    name = models.CharField(
        max_length=200,
        help_text="Product name as shown to customers"
    )
    
    # URL-safe slug for product detail pages
    # Example: "Apple iPhone 15 Pro" → "apple-iphone-15-pro"
    slug = models.SlugField(
        max_length=220,
        unique=True,
        help_text="URL-friendly product identifier"
    )
    
    # Full product description (supports HTML via template safe filter)
    description = models.TextField(
        help_text="Detailed product description"
    )
    
    # Short description for cards/listings
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description for product cards (optional)"
    )
    
    # Category Relationship
    # on_delete=models.CASCADE: If category deleted, delete products
    # Alternative: on_delete=models.SET_NULL keeps products, removes category
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',  # Access via category.products.all()
        help_text="Product category"
    )
    
    # Pricing
    # Using DecimalField prevents floating-point calculation errors
    # Example: 19.99 stays exactly 19.99, not 19.989999999
    price = models.DecimalField(
        max_digits=10,  # Max: 99,999,999.99 (supports up to $99M products)
        decimal_places=2,  # Always 2 decimal places (e.g., $19.99)
        validators=[MinValueValidator(Decimal('0.01'))],  # Minimum $0.01
        help_text="Regular price"
    )
    
    # Sale price for discounts (optional)
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Discounted price (optional)"
    )
    
    # Inventory Management
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Current stock quantity"
    )
    
    # Product Status
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive products are hidden from store"
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured products appear on homepage"
    )
    
    # Main Product Image
    image = models.ImageField(
        upload_to='products/',  # Uploads to MEDIA_ROOT/products/
        help_text="Main product image"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Product creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest products first
        indexes = [
            models.Index(fields=['slug']),  # Fast lookups by URL
            models.Index(fields=['category', 'is_active']),  # Fast category filtering
            models.Index(fields=['is_featured', 'is_active']),  # Fast homepage queries
            models.Index(fields=['-created_at']),  # Fast "new arrivals" queries
        ]
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from product name if not provided.
        
        Production consideration: In high-volume stores, add uniqueness check:
        base_slug = slugify(self.name)
        if Product.objects.filter(slug=base_slug).exists():
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    # ==========================================
    # HELPER METHODS - Business Logic
    # ==========================================
    
    def get_display_price(self):
        """
        Returns the price to display (sale price if available).
        
        Why: Centralizes pricing logic instead of repeating in templates
        Usage: {{ product.get_display_price }}
        """
        return self.sale_price if self.sale_price else self.price
    
    def is_on_sale(self):
        """Check if product is currently on sale"""
        return self.sale_price is not None and self.sale_price < self.price
    
    def get_discount_percentage(self):
        """
        Calculate discount percentage for display.
        
        Returns: Integer percentage (e.g., 25 for 25% off)
        Returns None if not on sale
        """
        if not self.is_on_sale():
            return None
        
        discount = ((self.price - self.sale_price) / self.price) * 100
        return int(discount)
    
    def is_in_stock(self):
        """Check if product has available stock"""
        return self.stock > 0
    
    def get_average_rating(self):
        """
        Calculate average rating from reviews.
        
        Performance: Uses database aggregation (single query)
        Returns: Float between 0-5, or None if no reviews
        """
        from django.db.models import Avg
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None
    
    def get_review_count(self):
        """Count total reviews"""
        return self.reviews.count()


# ==========================================
# PRODUCT IMAGE MODEL - Additional Images
# ==========================================

class ProductImage(models.Model):
    """
    Additional product images for gallery view.
    
    Why separate model:
    - Products can have multiple images
    - Keeps Product model clean
    - Allows reordering images via 'order' field
    
    Usage in views:
    product.images.all() - Get all images
    product.images.order_by('order') - Get ordered gallery
    """
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,  # Delete images if product deleted
        related_name='images'  # Access via product.images.all()
    )
    
    image = models.ImageField(
        upload_to='products/gallery/',
        help_text="Additional product image"
    )
    
    # Display order for gallery
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    
    # Optional caption
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Image caption (optional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']  # Order by order field, then date
        verbose_name_plural = "Product Images"
    
    def __str__(self):
        return f"Image for {self.product.name}"


# ==========================================
# REVIEW MODEL - Customer Feedback
# ==========================================

class Review(models.Model):
    """
    Customer product reviews with ratings.
    
    Security considerations:
    - User authentication required (prevents spam)
    - One review per user per product (prevents review bombing)
    - Rating validated to 1-5 range
    - Comment sanitized by Django (prevents XSS)
    
    Moderation:
    - is_approved field allows admin review before publishing
    - Useful for filtering spam/inappropriate content
    """
    
    # Relationships
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),  # Minimum 1 star
            MaxValueValidator(5)   # Maximum 5 stars
        ],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Review text
    title = models.CharField(
        max_length=100,
        help_text="Review title/headline"
    )
    
    comment = models.TextField(
        help_text="Detailed review comment"
    )
    
    # Moderation
    is_approved = models.BooleanField(
        default=True,  # Auto-approve (change to False for manual moderation)
        help_text="Unapproved reviews are hidden"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest reviews first
        # Prevent duplicate reviews: One review per user per product
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"