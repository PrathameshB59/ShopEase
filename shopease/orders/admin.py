from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Show order items directly on order page"""
    model = OrderItem
    extra = 0  # Don't show empty forms (orders are usually created by customers)
    readonly_fields = ['product', 'product_name', 'price', 'quantity', 'total_price']
    can_delete = False  # Prevent deleting items from completed orders

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'shipping_email', 'shipping_phone']
    
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    # Show order items on the order page
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Shipping Details', {
            'fields': (
                'shipping_name', 'shipping_address', 'shipping_city',
                'shipping_state', 'shipping_zip_code', 'shipping_country',
                'shipping_phone', 'shipping_email'
            )
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total', 'payment_method', 'payment_status')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='SHIPPED', shipped_at=timezone.now())
    mark_as_shipped.short_description = "Mark selected orders as Shipped"