# products/models.py

"""
Product Models - The Foundation of Your Shopping Site

These models define what products look like in your database.
Think of them as the blueprint for your product catalog.
Every product in your store is stored according to these definitions.
"""

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """
    Category Model - Organizes products into groups
    
    Just like a physical store has sections (Electronics, Clothing, Books),
    your online store has categories. This helps customers find what they want.
    
    Example categories:
    - Electronics (contains phones, laptops, headphones)
    - Clothing (contains shirts, pants, shoes)
    - Books (contains fiction, non-fiction, textbooks)
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Electronics', 'Clothing')"
    )
    
    # Slug is URL-friendly version: "Men's Clothing" becomes "mens-clothing"
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        blank=True,
        help_text="Brief description of this category"
    )
    
    # Category image for display on category pages
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text="Category banner image"
    )
    
    # Control visibility - you can hide categories without deleting them
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this category from customers"
    )
    
    # Display order - lower numbers appear first
    order = models.IntegerField(
        default=0,
        help_text="Display order (0 = first)"
    )
    
    # Timestamps - Django automatically manages these
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name when saving
        This ensures every category has a clean URL
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        """What you see when you print a category"""
        return self.name
    
    def get_absolute_url(self):
        """URL to view products in this category"""
        return reverse('products:category-products', kwargs={'slug': self.slug})
    
    @property
    def product_count(self):
        """How many products are in this category"""
        return self.products.filter(is_active=True).count()
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']


class Product(models.Model):
    """
    Product Model - Individual items for sale
    
    This is the heart of your store. Each product has:
    - Basic info (name, description, price)
    - Inventory tracking (stock count)
    - Organization (category)
    - Display settings (featured, active)
    - SEO fields (slug for URLs)
    """
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        help_text="Product name as shown to customers"
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly version of name (auto-generated)"
    )
    
    description = models.TextField(
        help_text="Detailed product description"
    )
    
    # Short description for product listings
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description shown in product cards"
    )
    
    # Pricing Information
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Regular price"
    )
    
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
        help_text="Sale price (leave empty if not on sale)"
    )
    
    # Inventory Management
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantity in stock"
    )
    
    # Low stock threshold for warnings
    low_stock_threshold = models.IntegerField(
        default=10,
        help_text="Warn when stock falls below this number"
    )
    
    # Product Details
    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Stock Keeping Unit - unique product code"
    )
    
    brand = models.CharField(
        max_length=100,
        blank=True,
        help_text="Product brand or manufacturer"
    )
    
    # Category Relationship
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Product category"
    )
    
    # Display Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Active products are visible to customers"
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured products appear on homepage"
    )
    
    # Rating and Reviews (we'll implement review system later)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average customer rating (0-5 stars)"
    )
    
    review_count = models.IntegerField(
        default=0,
        help_text="Number of customer reviews"
    )
    
    # Sales tracking
    total_sales = models.IntegerField(
        default=0,
        help_text="Total units sold"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug and SKU if not provided
        """
        if not self.slug:
            self.slug = slugify(self.name)
        
        if not self.sku:
            # Generate SKU from category and timestamp
            import time
            self.sku = f"{self.category.slug[:3].upper()}-{int(time.time())}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """URL to view this product's detail page"""
        return reverse('products:product-detail', kwargs={'slug': self.slug})
    
    @property
    def get_display_price(self):
        """
        Returns the price to show to customers
        If on sale, return sale price, otherwise regular price
        """
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """Check if product has active sale price"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is available for purchase"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Check if stock is running low"""
        return 0 < self.stock <= self.low_stock_threshold
    
    @property
    def stock_status(self):
        """Human-readable stock status"""
        if self.stock == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return f"Only {self.stock} left!"
        else:
            return "In Stock"
    
    @property
    def primary_image(self):
        """Get the main product image"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        # If no primary image set, return first image
        return self.images.first()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        # Add index for faster queries on commonly filtered fields
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]


class ProductImage(models.Model):
    """
    ProductImage Model - Multiple photos for each product
    
    Most products need multiple images:
    - Front view
    - Back view
    - Close-up details
    - Product in use
    
    This model lets you upload multiple images per product
    """
    
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE,
        help_text="Product this image belongs to"
    )
    
    image = models.ImageField(
        upload_to='products/',
        help_text="Product image file"
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Image description for accessibility and SEO"
    )
    
    # Display order for image gallery
    order = models.IntegerField(
        default=0,
        help_text="Display order (0 = first)"
    )
    
    # Mark one image as primary/main image
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary image shows in product listings"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """
        Ensure only one primary image per product
        If this image is marked primary, remove primary from others
        """
        if self.is_primary:
            # Remove primary status from other images of same product
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # If this is the first image, make it primary automatically
        if not self.pk and not ProductImage.objects.filter(product=self.product).exists():
            self.is_primary = True
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    class Meta:
        ordering = ['order', '-uploaded_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'


"""
Why We Built Models This Way:

1. CATEGORY MODEL:
   - Keeps products organized
   - Makes navigation easy for customers
   - Allows filtering and searching
   - Can be displayed as menu items

2. PRODUCT MODEL:
   - Contains all info customers need to make purchase decision
   - Tracks inventory to prevent overselling
   - Supports both regular and sale pricing
   - Has SEO-friendly URLs (slug)
   - Tracks sales and ratings for analytics

3. PRODUCTIMAGE MODEL:
   - Separate model allows multiple images per product
   - Images can be reordered
   - One image marked as primary for thumbnails
   - Keeps Product model clean

This structure supports everything a real e-commerce site needs:
- Browse by category
- Search products
- View detailed product pages
- See multiple product photos
- Track inventory
- Show sale prices
- Display featured products on homepage
"""