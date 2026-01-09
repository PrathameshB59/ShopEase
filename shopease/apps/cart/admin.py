"""
========================================
CART ADMIN - Django Admin Interface
========================================
Admin interface for managing carts (debugging/support).
"""

from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for Cart model.
    
    Use cases:
    - Support: View customer carts
    - Debug: Check cart data
    - Analytics: Find abandoned carts
    """
    
    list_display = [
        'id',
        'user_display',
        'session_key_short',
        'total_items',
        'subtotal',
        'is_active',
        'updated_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'session_key'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'total_items',
        'subtotal'
    ]
    
    def user_display(self, obj):
        """Display username or 'Anonymous'"""
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'User'
    
    def session_key_short(self, obj):
        """Display shortened session key"""
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return '-'
    session_key_short.short_description = 'Session'
    
    def total_items(self, obj):
        """Display total items in cart"""
        return obj.get_total_items()
    total_items.short_description = 'Items'
    
    def subtotal(self, obj):
        """Display cart subtotal"""
        return f"${obj.get_subtotal()}"
    subtotal.short_description = 'Subtotal'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin interface for CartItem model.
    
    Use cases:
    - Debug: Check specific cart items
    - Support: Modify quantities
    """
    
    list_display = [
        'id',
        'cart',
        'product',
        'quantity',
        'price_snapshot',
        'total_price',
        'added_at'
    ]
    
    list_filter = [
        'added_at',
        'updated_at'
    ]
    
    search_fields = [
        'product__name',
        'cart__user__username',
        'cart__session_key'
    ]
    
    readonly_fields = [
        'added_at',
        'updated_at',
        'total_price'
    ]
    
    def total_price(self, obj):
        """Display line item total"""
        return f"${obj.get_total_price()}"
    total_price.short_description = 'Total'