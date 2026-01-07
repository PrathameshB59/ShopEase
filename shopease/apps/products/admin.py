"""
========================================
PRODUCT ADMIN - Django Admin Configuration
========================================
Professional admin interface for managing products, categories, and reviews.

Features:
- Inline editing of related models
- Custom list displays with filters
- Search functionality
- Bulk actions for efficiency
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review


# ==========================================
# INLINE ADMINS - Edit Related Objects
# ==========================================

class ProductImageInline(admin.TabularInline):
    """
    Allows adding/editing product images directly on product page.
    
    Benefits:
    - No need to navigate to separate page
    - See all product images at once
    - Easier workflow for admins
    """
    model = ProductImage
    extra = 1  # Show 1 empty form for new images
    fields = ['image', 'caption', 'order']


class ReviewInline(admin.TabularInline):
    """Show product reviews on product detail page"""
    model = Review
    extra = 0  # Don't show empty forms
    readonly_fields = ['user', 'rating', 'title', 'comment', 'created_at']
    can_delete = True  # Allow deleting inappropriate reviews
    fields = ['user', 'rating', 'title', 'is_approved', 'created_at']


# ==========================================
# CATEGORY ADMIN
# ==========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category management interface.
    
    Features:
    - Auto-generate slug from name
    - See product count per category
    - Filter by active status
    """
    
    list_display = ['name', 'slug', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def product_count(self, obj):
        """Display count of products in category"""
        count = obj.get_product_count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    product_count.short_description = 'Products'


# ==========================================
# PRODUCT ADMIN
# ==========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Main product management interface.
    
    Features:
    - Inline image management
    - Price display with sale indicators
    - Stock level tracking
    - Bulk actions for status changes
    """
    
    list_display = [
        'image_thumbnail',
        'name',
        'category',
        'price_display',
        'stock_level',
        'rating_display',
        'is_featured',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'is_featured',
        'category',
        'created_at'
    ]
    
    search_fields = ['name', 'description', 'slug']
    
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = [ProductImageInline, ReviewInline]
    
    # Organize fields into logical sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
            'description': 'Set sale_price lower than price to show discount'
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    # Bulk actions for efficiency
    actions = ['mark_as_featured', 'remove_featured', 'mark_in_stock', 'mark_out_of_stock']
    
    def image_thumbnail(self, obj):
        """Display small product image in list"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_thumbnail.short_description = 'Image'
    
    def price_display(self, obj):
        """Show price with sale indicator"""
        if obj.is_on_sale():
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span> '
                '<span style="color: #e74c3c; font-weight: bold;">${}</span> '
                '<span style="background: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">-{}%</span>',
                obj.price,
                obj.sale_price,
                obj.get_discount_percentage()
            )
        return format_html('<span style="font-weight: bold;">${}</span>', obj.price)
    price_display.short_description = 'Price'
    
    def stock_level(self, obj):
        """Visual stock indicator"""
        if obj.stock == 0:
            color = '#e74c3c'  # Red
            text = 'Out of Stock'
        elif obj.stock < 10:
            color = '#f39c12'  # Orange
            text = f'Low ({obj.stock})'
        else:
            color = '#27ae60'  # Green
            text = f'In Stock ({obj.stock})'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    stock_level.short_description = 'Stock'
    
    def rating_display(self, obj):
        """Show average rating with star emoji"""
        avg_rating = obj.get_average_rating()
        review_count = obj.get_review_count()
        
        if avg_rating:
            return format_html(
                '<span style="color: #f39c12;">★ {}</span> <span style="color: #999;">({} reviews)</span>',
                avg_rating, review_count
            )
        return format_html('<span style="color: #999;">No reviews</span>')
    rating_display.short_description = 'Rating'
    
    # Bulk action methods
    def mark_as_featured(self, request, queryset):
        """Bulk mark products as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} product(s) marked as featured.')
    mark_as_featured.short_description = 'Mark as featured'
    
    def remove_featured(self, request, queryset):
        """Bulk remove featured status"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} product(s) removed from featured.')
    remove_featured.short_description = 'Remove featured status'
    
    def mark_in_stock(self, request, queryset):
        """Bulk set stock to 100"""
        updated = queryset.update(stock=100)
        self.message_user(request, f'{updated} product(s) marked as in stock (100 units).')
    mark_in_stock.short_description = 'Mark as in stock (100 units)'
    
    def mark_out_of_stock(self, request, queryset):
        """Bulk set stock to 0"""
        updated = queryset.update(stock=0)
        self.message_user(request, f'{updated} product(s) marked as out of stock.')
    mark_out_of_stock.short_description = 'Mark as out of stock'


# ==========================================
# REVIEW ADMIN
# ==========================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review moderation interface"""
    
    list_display = [
        'user',
        'product',
        'rating_stars',
        'title',
        'is_approved',
        'created_at'
    ]
    
    list_filter = [
        'rating',
        'is_approved',
        'created_at'
    ]
    
    search_fields = [
        'user__username',
        'product__name',
        'title',
        'comment'
    ]
    
    readonly_fields = ['user', 'product', 'created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'product', 'rating', 'title', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #f39c12; font-size: 16px;">{}</span>',
            stars
        )
    rating_stars.short_description = 'Rating'
    
    def approve_reviews(self, request, queryset):
        """Bulk approve reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review(s) approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def unapprove_reviews(self, request, queryset):
        """Bulk unapprove reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review(s) unapproved.')
    unapprove_reviews.short_description = 'Unapprove selected reviews'