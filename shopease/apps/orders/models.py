"""
========================================
ORDER MODELS - FAKE VERSION (Development)
========================================

This is a simplified version for development.
Real payment processing will be added later.

Copy this to: apps/orders/models.py
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

# Import from your products app
from apps.products.models import Product


class Order(models.Model):
    """
    Order model - represents a customer purchase.
    
    For now, all orders will be marked as COMPLETED immediately.
    Later, we'll add real payment processing.
    """
    
    # Order status choices
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),       # Not used yet
        ('COMPLETED', 'Completed'),           # All orders go here for now
        ('PROCESSING', 'Processing'),         # Not used yet
        ('SHIPPED', 'Shipped'),              # Admin can change to this
        ('DELIVERED', 'Delivered'),          # Admin can change to this
        ('CANCELLED', 'Cancelled'),          # Users can cancel
    ]
    
    # Payment method choices (for future use)
    PAYMENT_METHOD_CHOICES = [
        ('FAKE', 'Fake Payment (Testing)'),  # Current method
        ('COD', 'Cash on Delivery'),         # Future
        ('ONLINE', 'Online Payment'),        # Future
    ]
    
    # Unique order ID
    # Uses UUID so it can't be guessed
    # Example: 550e8400-e29b-41d4-a716-446655440000
    order_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique order identifier"
    )
    
    # Who placed this order?
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Customer who placed order"
    )
    
    # Shipping information
    # These fields store where to ship the order
    shipping_full_name = models.CharField(max_length=100)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='India')
    
    # Payment information
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total order amount"
    )
    
    # Order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='COMPLETED',  # All orders complete immediately (fake)
        db_index=True
    )
    
    # Payment method (always FAKE for now)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='FAKE'
    )
    
    # Order notes from customer
    order_notes = models.TextField(
        blank=True,
        help_text="Customer's special instructions"
    )
    
    # Admin notes (not visible to customer)
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest first
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Order #{str(self.order_id)[:8]} by {self.user.email}"
    
    def get_total_items(self):
        """
        Calculate total number of items in order.
        Example: 2 shirts + 3 pants = 5 items
        """
        total = self.items.aggregate(models.Sum('quantity'))['quantity__sum']
        return total or 0
    
    def can_be_cancelled(self):
        """
        Check if order can be cancelled.
        For now, only completed orders can be cancelled.
        """
        return self.status == 'COMPLETED'
    
    def cancel_order(self, reason=''):
        """
        Cancel order and restore product stock.
        
        When order is cancelled:
        1. Restore stock (add back to inventory)
        2. Change status to CANCELLED
        3. Log the reason
        """
        if not self.can_be_cancelled():
            raise ValueError(f"Order {self.order_id} cannot be cancelled")
        
        # Restore stock for each item
        for item in self.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        
        # Update order status
        self.status = 'CANCELLED'
        
        # Log cancellation
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        cancel_note = f"[{timestamp}] Cancelled. Reason: {reason or 'Not specified'}"
        self.admin_notes += f"\n{cancel_note}" if self.admin_notes else cancel_note
        
        self.save(update_fields=['status', 'admin_notes'])


class OrderItem(models.Model):
    """
    Individual item in an order.
    
    Think of this as one line on a receipt:
    - Product name
    - Quantity
    - Price
    - Subtotal
    """
    
    # Which order does this belong to?
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Which product was ordered?
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    
    # Product details at time of order
    # We store these because product might change later
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    
    # Price at time of order
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # How many?
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        # Each product should appear only once per order
        unique_together = [('order', 'product')]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def get_subtotal(self):
        """
        Calculate subtotal for this line item.
        Example: Price ₹100 × Quantity 3 = ₹300
        """
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        """
        Auto-fill product details when saving.
        
        This saves developer time - just set product and quantity,
        everything else is filled automatically.
        """
        if not self.product_name and self.product:
            self.product_name = self.product.name
        
        if not self.product_sku and self.product:
            self.product_sku = self.product.sku
        
        if self.price is None and self.product:
            self.price = self.product.price
        
        super().save(*args, **kwargs)