# orders/admin.py
"""
ADMIN CONFIGURATION FOR ORDER MODELS
======================================
Admin interface for managing customer orders
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem


# ============================================================================
# ORDER ITEM INLINE ADMIN
# ============================================================================
class OrderItemInline(admin.TabularInline):
    """
    Show order items directly on order page
    Allows viewing (but not editing) items in completed orders
    """
    model = OrderItem
    
    # Don't show empty forms (orders are created by customers)
    extra = 0
    
    # These fields are read-only (can view but not edit)
    # We don't want to change order items after order is placed
    readonly_fields = ['product', 'product_name', 'price', 'quantity', 'total_price']
    
    # Can't delete items from completed orders
    can_delete = False
    
    # Which fields to show in the table
    fields = ['product', 'product_name', 'price', 'quantity', 'total_price']
    
    def total_price(self, obj):
        """Display total for this line item"""
        return f"${obj.get_total():.2f}"
    
    total_price.short_description = 'Total'


# ============================================================================
# ORDER ADMIN
# ============================================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Main admin interface for managing orders
    """
    
    # LIST DISPLAY
    # =============
    list_display = [
        'order_number',
        'customer_name',
        'shipping_email',
        'status_badge',
        'payment_badge',
        'total_display',
        'items_count',
        'created_at'
    ]
    
    # LIST FILTER
    # ============
    list_filter = [
        'status',
        'payment_status',
        'payment_method',
        'created_at',
        'shipped_at'
    ]
    
    # SEARCH FIELDS
    # ==============
    search_fields = [
        'order_number',
        'user__username',
        'user__email',
        'shipping_email',
        'shipping_phone',
        'shipping_name',
        'transaction_id'
    ]
    
    # READONLY FIELDS
    # ================
    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'subtotal',
        'total'
    ]
    
    # INLINES
    # ========
    inlines = [OrderItemInline]
    
    # FIELDSETS
    # ==========
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'user',
                'status',
                'created_at',
                'updated_at'
            )
        }),
        ('Shipping Details', {
            'fields': (
                'shipping_name',
                'shipping_email',
                'shipping_phone',
                'shipping_address',
                'shipping_city',
                'shipping_state',
                'shipping_zip_code',
                'shipping_country'
            )
        }),
        ('Financial Information', {
            'fields': (
                'subtotal',
                'tax',
                'shipping_cost',
                'discount',
                'total',
                'payment_method',
                'payment_status',
                'transaction_id'
            )
        }),
        ('Tracking & Delivery', {
            'fields': (
                'tracking_number',
                'shipped_at',
                'delivered_at'
            )
        }),
        ('Notes', {
            'fields': (
                'customer_notes',
                'admin_notes'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # ORDERING
    # =========
    ordering = ['-created_at']
    
    # LIST PER PAGE
    # ==============
    list_per_page = 50
    
    # ACTIONS
    # ========
    actions = [
        'mark_as_confirmed',
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]
    
    def mark_as_confirmed(self, request, queryset):
        """Bulk action: Confirm orders"""
        updated = queryset.update(status='CONFIRMED')
        self.message_user(request, f'{updated} order(s) marked as confirmed.')
    mark_as_confirmed.short_description = "Mark as Confirmed"
    
    def mark_as_processing(self, request, queryset):
        """Bulk action: Mark as processing"""
        updated = queryset.update(status='PROCESSING')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = "Mark as Processing"
    
    def mark_as_shipped(self, request, queryset):
        """Bulk action: Mark as shipped"""
        updated = queryset.update(status='SHIPPED', shipped_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        """Bulk action: Mark as delivered"""
        updated = queryset.update(status='DELIVERED', delivered_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark as Delivered"
    
    def mark_as_cancelled(self, request, queryset):
        """Bulk action: Cancel orders"""
        # Only cancel orders that can be cancelled
        cancellable = queryset.filter(status__in=['PENDING', 'CONFIRMED', 'PROCESSING'])
        updated = cancellable.update(status='CANCELLED')
        self.message_user(request, f'{updated} order(s) cancelled.')
    mark_as_cancelled.short_description = "Cancel Orders"
    
    # CUSTOM DISPLAY METHODS
    # =======================
    
    def customer_name(self, obj):
        """Display customer name"""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return obj.shipping_name
    customer_name.short_description = 'Customer'
    
    def status_badge(self, obj):
        """Display colored status badge"""
        color_map = {
            'PENDING': '#ffc107',      # Yellow
            'CONFIRMED': '#17a2b8',    # Cyan
            'PROCESSING': '#007bff',   # Blue
            'SHIPPED': '#6f42c1',      # Purple
            'DELIVERED': '#28a745',    # Green
            'CANCELLED': '#dc3545',    # Red
            'REFUNDED': '#6c757d',     # Gray
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        """Display colored payment status badge"""
        color_map = {
            'PENDING': '#ffc107',
            'PAID': '#28a745',
            'FAILED': '#dc3545',
            'REFUNDED': '#6c757d',
        }
        color = color_map.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_badge.short_description = 'Payment'
    
    def total_display(self, obj):
        """Display total with currency symbol"""
        return format_html(
            '<strong style="color: #28a745; font-size: 14px;">${:.2f}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def items_count(self, obj):
        """Display number of items in order"""
        count = obj.items.count()
        return format_html(
            '<span style="background: #e9ecef; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{} item(s)</span>',
            count
        )
    items_count.short_description = 'Items'


# Customize admin site
admin.site.site_header = "ShopEase Admin Dashboard"
admin.site.site_title = "ShopEase Admin"
admin.site.index_title = "Welcome to ShopEase Administration"