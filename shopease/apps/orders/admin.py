"""
========================================
ADMIN CONFIGURATION - Orders
========================================

Admin panel configuration for managing orders.

Copy this to: apps/orders/admin.py
"""

from django.contrib import admin
from .models import Order, OrderItem


# Inline admin for OrderItems
# Shows order items inside the Order admin page
class OrderItemInline(admin.TabularInline):
    """Display order items within order admin"""
    model = OrderItem
    extra = 0  # Don't show empty forms
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'get_subtotal')
    
    # Don't allow adding new items through admin
    # (Items created through checkout process)
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    # What columns to show in list view
    list_display = (
        'get_order_number',
        'user',
        'shipping_full_name',
        'status',
        'total_amount',
        'payment_method',
        'created_at'
    )
    
    # Filters in sidebar
    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )
    
    # Search fields
    search_fields = (
        'order_id',
        'shipping_email',
        'shipping_phone',
        'shipping_full_name',
    )
    
    # Read-only fields (can't be edited)
    readonly_fields = (
        'order_id',
        'created_at',
        'updated_at',
        'get_total_items',
    )
    
    # Show order items inline
    inlines = [OrderItemInline]
    
    # Organize fields in sections
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'payment_method')
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_full_name',
                'shipping_email',
                'shipping_phone',
                'shipping_address_line1',
                'shipping_address_line2',
                'shipping_city',
                'shipping_state',
                'shipping_postal_code',
                'shipping_country',
            )
        }),
        ('Payment Information', {
            'fields': ('total_amount', 'get_total_items')
        }),
        ('Notes', {
            'fields': ('order_notes', 'admin_notes'),
            'classes': ('collapse',),  # Collapsed by default
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Custom methods
    def get_order_number(self, obj):
        """Display short order number"""
        return f"#{str(obj.order_id)[:8]}"
    get_order_number.short_description = 'Order #'
    
    # Allow changing status through dropdown
    # (Click "Change" on order, update status, save)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    
    list_display = (
        'order',
        'product_name',
        'quantity',
        'price',
        'get_subtotal'
    )
    
    list_filter = (
        'order__created_at',
    )
    
    search_fields = (
        'product_name',
        'order__order_id',
    )
    
    readonly_fields = (
        'order',
        'product',
        'product_name',
        'product_sku',
        'price',
        'quantity',
        'get_subtotal',
    )
    
    # Don't allow adding/deleting through admin
    # (Items created through checkout process)
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False