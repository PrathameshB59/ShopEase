# products/admin.py
"""
ADMIN CONFIGURATION FOR PRODUCT MODELS
========================================
This file configures how Category, Product, and ProductImage appear in Django admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage


# ============================================================================
# PRODUCT IMAGE INLINE ADMIN
# ============================================================================
class ProductImageInline(admin.TabularInline):
    """
    INLINE ADMIN FOR PRODUCT IMAGES
    Allows adding/editing product images directly on the product page
    """
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    can_delete = True
    
    def image_preview(self, obj):
        """Display small thumbnail of the image in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    
    image_preview.short_description = 'Preview'


# ============================================================================
# CATEGORY ADMIN
# ============================================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """CATEGORY ADMIN CONFIGURATION"""
    
    list_display = [
        'name',
        'slug',
        'product_count',
        'is_active',
        'order',
        'image_preview',
        'created_at'
    ]
    
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('image', 'image_preview', 'is_active', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def product_count(self, obj):
        """Show number of active products in this category"""
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: red;">0</span>')
    
    product_count.short_description = 'Products'
    
    def image_preview(self, obj):
        """Show thumbnail of category image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 80px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    
    image_preview.short_description = 'Image'


# ============================================================================
# PRODUCT ADMIN
# ============================================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """PRODUCT ADMIN CONFIGURATION"""
    
    list_display = [
        'image_preview',
        'name',
        'category',
        'price',
        'sale_price',
        'stock',
        'stock_status',
        'is_active',
        'is_featured',
        'views',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_active',
        'is_featured',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'sku',
        'brand'
    ]
    
    prepopulated_fields = {'slug': ('name',)}
    
    list_editable = [
        'price',
        'stock',
        'is_active',
        'is_featured'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'views',
        'average_rating',
        'review_count',
        'slug',
        'sku'
    ]
    
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'brand', 'sku'),
        }),
        ('Description', {
            'fields': ('short_description', 'description'),
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold'),
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('Analytics', {
            'fields': ('views', 'average_rating', 'review_count'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    list_per_page = 25
    
    actions = [
        'make_active',
        'make_inactive',
        'make_featured',
        'remove_featured',
        'apply_10_percent_discount',
        'remove_discount'
    ]
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} product(s) activated.')
    make_active.short_description = "Activate selected products"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} product(s) deactivated.')
    make_inactive.short_description = "Deactivate selected products"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} product(s) marked as featured.')
    make_featured.short_description = "Mark as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} product(s) removed from featured.')
    remove_featured.short_description = "Remove featured status"
    
    def apply_10_percent_discount(self, request, queryset):
        for product in queryset:
            product.sale_price = product.price * 0.90
            product.save()
        self.message_user(request, f'{queryset.count()} product(s) now have 10% discount.')
    apply_10_percent_discount.short_description = "Apply 10% discount"
    
    def remove_discount(self, request, queryset):
        updated = queryset.update(sale_price=None)
        self.message_user(request, f'{updated} product(s) sale price removed.')
    remove_discount.short_description = "Remove discount"
    
    def image_preview(self, obj):
        """Show product's primary image as thumbnail"""
        primary_image = obj.get_primary_image()
        if primary_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" />',
                primary_image.image.url
            )
        return format_html(
            '<div style="width: 60px; height: 60px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #999;">No image</div>'
        )
    
    image_preview.short_description = 'Image'
    
    def stock_status(self, obj):
        """Visual indicator of stock status"""
        if obj.stock == 0:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">OUT OF STOCK</span>'
            )
        elif obj.is_low_stock():
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">LOW ({} left)</span>',
                obj.stock
            )
        else:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">IN STOCK</span>'
            )
    
    stock_status.short_description = 'Stock Status'


# ============================================================================
# PRODUCT IMAGE ADMIN
# ============================================================================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """STANDALONE ADMIN FOR PRODUCT IMAGES"""
    
    list_display = [
        'image_preview',
        'product',
        'alt_text',
        'is_primary',
        'order',
        'uploaded_at'
    ]
    
    list_filter = [
        'is_primary',
        'product__category',
        'uploaded_at'
    ]
    
    search_fields = [
        'product__name',
        'alt_text'
    ]
    
    list_editable = ['is_primary', 'order']
    ordering = ['product', 'order']
    readonly_fields = ['image_preview', 'uploaded_at']
    
    def image_preview(self, obj):
        """Show image thumbnail"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    
    image_preview.short_description = 'Preview'


# Customize admin site
admin.site.site_header = "ShopEase Admin Dashboard"
admin.site.site_title = "ShopEase Admin"
admin.site.index_title = "Welcome to ShopEase Administration"