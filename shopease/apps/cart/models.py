"""
========================================
SHOPPING CART MODELS
========================================

ARCHITECTURE DECISION: Session + Database Hybrid
-------------------------------------------------
We store cart in BOTH session AND database:

1. SESSION (Redis/Memory):
   - Fast reads (no DB queries)
   - Temporary storage
   - Survives server restart (if using DB backend)

2. DATABASE:
   - Permanent storage
   - Survives session expiry
   - Allows cart recovery
   - Analytics (abandoned carts)

SECURITY CONSIDERATIONS:
-------------------------
1. Price Validation:
   - NEVER trust prices from frontend
   - ALWAYS fetch current price from database
   - Prevents: User changing price in DevTools

2. Stock Validation:
   - Check stock before adding to cart
   - Check again at checkout
   - Prevents: Overselling products

3. User Association:
   - Anonymous users: session_key
   - Logged-in users: user_id
   - Allows: Cart merging on login

Real-world example: Amazon's cart works offline (session),
syncs to account when you login (database).
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from apps.products.models import Product
from decimal import Decimal


class Cart(models.Model):
    """
    Shopping cart container.
    
    One cart per user/session.
    Contains multiple CartItems.
    
    Why separate Cart and CartItem models?
    - Allows metadata on cart (coupons, shipping, tax)
    - Enables cart-level operations (clear all, save for later)
    - Cleaner database structure
    """
    
    # User Association
    # NULL = Anonymous user (uses session_key)
    # NOT NULL = Logged-in user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete cart if user deleted
        null=True,                  # Allow anonymous carts
        blank=True,
        related_name='carts'
    )
    
    # Session key for anonymous users
    # Django generates: 'abcd1234efgh5678'
    # Stored in cookie, maps to session data
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True  # Fast lookups by session
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Cart status
    is_active = models.BooleanField(
        default=True,
        help_text="False = Checked out or abandoned"
    )
    
    class Meta:
        # One cart per user OR session
        # Prevents duplicate carts
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(user__isnull=False, is_active=True),
                name='unique_active_user_cart'
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=models.Q(session_key__isnull=False, is_active=True),
                name='unique_active_session_cart'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key', 'is_active']),
            models.Index(fields=['updated_at']),  # For finding abandoned carts
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key[:8]}..."
    
    # ==========================================
    # BUSINESS LOGIC METHODS
    # ==========================================
    
    def get_total_items(self):
        """
        Total number of items in cart.
        
        Returns: Integer (sum of all quantities)
        Example: 2 shirts + 3 socks = 5 items
        """
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """
        Cart subtotal (before tax/shipping).
        
        Returns: Decimal
        Security: Calculates from current product prices
                 (not stored prices that could be outdated)
        """
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_price(self):
        """
        Final cart total (subtotal + tax + shipping).
        
        TODO: Add tax and shipping calculation
        """
        subtotal = self.get_subtotal()
        # tax = subtotal * Decimal('0.08')  # 8% tax
        # shipping = Decimal('5.99') if subtotal < 50 else Decimal('0.00')
        # return subtotal + tax + shipping
        return subtotal
    
    def clear(self):
        """
        Remove all items from cart.
        
        Use cases:
        - User clicks "Clear Cart"
        - After successful checkout
        - When merging carts (delete old cart)
        """
        self.items.all().delete()
    
    def get_item_count_by_product(self, product_id):
        """
        Get quantity of specific product in cart.
        
        Used for: "Already have 2 in cart" messages
        """
        try:
            item = self.items.get(product_id=product_id)
            return item.quantity
        except CartItem.DoesNotExist:
            return 0


class CartItem(models.Model):
    """
    Individual item in shopping cart.
    
    Represents: Product + Quantity + Snapshot Price
    
    Why store price snapshot?
    - Product price might change while in cart
    - User sees consistent price during session
    - At checkout, validate against current price
    """
    
    # Relationships
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'  # cart.items.all()
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
        # Don't use related_name to avoid conflicts
    )
    
    # Quantity
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]  # Minimum 1 item
    )
    
    # Price snapshot (at time of adding to cart)
    # Decimal is CRITICAL for money (never use Float)
    # Float has rounding errors: 19.99 * 3 = 59.97000000001
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price when added to cart"
    )
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # One entry per product per cart
        # Prevents duplicate items
        unique_together = ['cart', 'product']
        ordering = ['added_at']  # Show oldest items first
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    # ==========================================
    # BUSINESS LOGIC METHODS
    # ==========================================
    
    def get_total_price(self):
        """
        Line item total.
        
        Returns: Decimal (price × quantity)
        Example: $19.99 × 2 = $39.98
        """
        return self.price_snapshot * self.quantity
    
    def update_quantity(self, quantity):
        """
        Update quantity with validation.
        
        Args:
            quantity: New quantity (integer)
        
        Returns:
            Boolean (True if updated, False if out of stock)
        
        Security:
        - Validates against current stock
        - Prevents overselling
        """
        # Check if product has enough stock
        if quantity > self.product.stock:
            return False  # Not enough stock
        
        if quantity <= 0:
            # Delete item if quantity is 0
            self.delete()
        else:
            self.quantity = quantity
            self.save()
        
        return True
    
    def increase_quantity(self, amount=1):
        """
        Increase quantity by amount.
        
        Used when: User clicks "+" button
        """
        new_quantity = self.quantity + amount
        return self.update_quantity(new_quantity)
    
    def decrease_quantity(self, amount=1):
        """
        Decrease quantity by amount.
        
        Used when: User clicks "-" button
        """
        new_quantity = self.quantity - amount
        return self.update_quantity(new_quantity)
    
    def is_price_current(self):
        """
        Check if snapshot price matches current product price.
        
        Used at checkout to warn about price changes.
        
        Returns: Boolean
        """
        current_price = self.product.get_display_price()
        return self.price_snapshot == current_price
    
    def update_price_snapshot(self):
        """
        Update snapshot to current product price.
        
        Call this:
        - At checkout
        - When user refreshes cart
        - After price change notifications
        """
        self.price_snapshot = self.product.get_display_price()
        self.save()