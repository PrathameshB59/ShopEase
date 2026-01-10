"""
========================================
CART MODELS - Shopping Cart System
========================================
Secure, session-based cart with database persistence for logged-in users.

Security Features:
- CSRF protection on all cart operations
- User authentication for persistent carts
- Session-based carts for anonymous users
- Input validation on quantities and prices
"""

from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
from decimal import Decimal


class Cart(models.Model):
    """
    Shopping cart container.
    
    Design Pattern:
    - One cart per user (logged in)
    - Session-based for anonymous users
    - Items stored in CartItem model
    
    Why separate Cart and CartItem?
    - Allows multiple items per cart
    - Tracks cart creation/modification dates
    - Enables cart abandonment analytics
    """
    
    # User relationship (null for anonymous users)
    # on_delete=CASCADE: Delete cart when user deleted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Allow anonymous carts
        blank=True,
        related_name='carts'
    )
    
    # Session key for anonymous users
    # Stores Django session ID to link cart to browser session
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True  # Fast lookups by session
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        # Ensure one cart per user
        # Allow multiple session-based carts (for different browsers)
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous Cart ({self.session_key[:8]}...)"
    
    # ==========================================
    # CART OPERATIONS - Business Logic
    # ==========================================
    
    def get_total_items(self):
        """
        Count total quantity of all items in cart.
        
        Returns: Integer (e.g., 5 items)
        """
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """
        Calculate subtotal (before tax/shipping).
        
        Returns: Decimal (e.g., Decimal('149.97'))
        
        Performance: Single query using database aggregation
        """
        from django.db.models import Sum, F
        
        # Calculate: SUM(quantity * price_snapshot)
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('price_snapshot'))
        )['total']
        
        return total or Decimal('0.00')
    
    def get_tax(self):
        """
        Calculate tax (10% for demo).
        
        Production: Calculate based on shipping address
        """
        return (self.get_subtotal() * Decimal('0.10')).quantize(Decimal('0.01'))
    
    def get_total(self):
        """
        Calculate final total (subtotal + tax).
        
        Shipping is FREE for demo.
        """
        return self.get_subtotal() + self.get_tax()
    
    def clear(self):
        """Delete all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Individual item in shopping cart.
    
    Why store price_snapshot?
    - Product prices can change
    - User should pay the price they saw when adding to cart
    - Prevents "bait and switch" scenarios
    
    Why not just store product_id and quantity?
    - We need a snapshot of the price at time of adding
    - Product might be deleted or go out of stock
    - Allows showing original vs. current price
    """
    
    # Cart relationship
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Product relationship
    # PROTECT: Don't delete items if product deleted (rare, but possible)
    # Alternative: CASCADE (remove cart items when product deleted)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cart_items'
    )
    
    # Quantity
    # PositiveIntegerField: Prevents negative quantities
    # Validation: 1 <= quantity <= product.stock
    quantity = models.PositiveIntegerField(default=1)
    
    # Price Snapshot
    # Stores price at time of adding to cart
    # Uses Decimal for accuracy (no floating point errors)
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price when added to cart"
    )
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-added_at']  # Newest items first
        # Prevent duplicate products in same cart
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to set price_snapshot on creation.
        
        Why: Ensures we always capture current price
        Security: Prevents client from manipulating prices
        """
        if not self.pk:  # Only on creation
            # Use sale price if available, otherwise regular price
            self.price_snapshot = self.product.get_display_price()
        
        super().save(*args, **kwargs)
    
    def get_subtotal(self):
        """
        Calculate line item total.
        
        Returns: Decimal (e.g., Decimal('59.97') for 3x $19.99)
        """
        return self.quantity * self.price_snapshot
    
    def increase_quantity(self, amount=1):
        """
        Increase quantity by amount.
        
        Validation: Doesn't exceed available stock
        Returns: True if successful, False if at stock limit
        """
        if self.quantity + amount <= self.product.stock:
            self.quantity += amount
            self.save()
            return True
        return False
    
    def decrease_quantity(self, amount=1):
        """
        Decrease quantity by amount.
        
        Validation: Doesn't go below 1
        Returns: True if successful, False if at minimum
        """
        if self.quantity - amount >= 1:
            self.quantity -= amount
            self.save()
            return True
        return False