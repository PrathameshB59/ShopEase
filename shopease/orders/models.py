# orders/models.py

"""
Order Models - Tracking Customer Purchases

When a customer completes checkout, we create an Order.
Think of an Order like a receipt - it records:
- Who bought what
- How many of each item
- What they paid
- Where to ship it
- Current status (pending, shipped, delivered)

Orders are permanent records. Even after products are deleted,
the order remembers what was purchased.
"""

from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator
import uuid


class Order(models.Model):
    """
    Order Model - A customer's purchase
    
    Each order represents one complete transaction.
    One customer can have many orders over time.
    Each order contains multiple items (OrderItem).
    
    Order lifecycle:
    1. Customer adds items to cart
    2. Customer goes to checkout
    3. Order is created with status='PENDING'
    4. Payment is processed (we'll add this later)
    5. Status changes to 'CONFIRMED'
    6. Admin/Staff ships the order: status='SHIPPED'
    7. Customer receives it: status='DELIVERED'
    """
    
    # Order Status Choices
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),           # Order placed, awaiting confirmation
        ('CONFIRMED', 'Confirmed'),       # Payment confirmed, ready to ship
        ('PROCESSING', 'Processing'),     # Being prepared for shipment
        ('SHIPPED', 'Shipped'),          # On its way to customer
        ('DELIVERED', 'Delivered'),       # Successfully delivered
        ('CANCELLED', 'Cancelled'),       # Order cancelled
        ('REFUNDED', 'Refunded'),        # Money returned to customer
    )
    
    # Unique order number for tracking
    # UUID ensures it's globally unique
    order_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        help_text="Unique order identifier"
    )
    
    # Customer who placed the order
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Points to our custom User model
        on_delete=models.CASCADE,   # If user deleted, keep order for records
        related_name='orders',
        help_text="Customer who placed this order"
    )
    
    # Order Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current order status"
    )
    
    # Shipping Information
    shipping_name = models.CharField(
        max_length=200,
        help_text="Full name for delivery"
    )
    
    shipping_address = models.TextField(
        help_text="Complete shipping address"
    )
    
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_country = models.CharField(
        max_length=100,
        default='India'
    )
    
    # Contact Information
    shipping_phone = models.CharField(
        max_length=20,
        help_text="Contact number for delivery"
    )
    
    shipping_email = models.EmailField(
        help_text="Email for order updates"
    )
    
    # Order Financial Details
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Sum of all items before tax and shipping"
    )
    
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tax amount"
    )
    
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Shipping charges"
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Final amount charged to customer"
    )
    
    # Payment Information (we'll add payment gateway later)
    payment_method = models.CharField(
        max_length=50,
        default='COD',
        help_text="Payment method (COD, Card, UPI, etc.)"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded'),
        ),
        default='PENDING'
    )
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment gateway transaction ID"
    )
    
    # Additional Notes
    customer_notes = models.TextField(
        blank=True,
        help_text="Special instructions from customer"
    )
    
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to customer)"
    )
    
    # Tracking
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shipping carrier tracking number"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When order was placed"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification time"
    )
    
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was shipped"
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was delivered"
    )
    
    def save(self, *args, **kwargs):
        """
        Auto-generate order number if not set
        Format: ORD-{8 character UUID}
        Example: ORD-A3B5C7D9
        """
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('orders:order-detail', kwargs={'order_number': self.order_number})
    
    @property
    def item_count(self):
        """Total number of items in order"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def can_cancel(self):
        """Check if order can be cancelled by customer"""
        return self.status in ['PENDING', 'CONFIRMED']
    
    @property
    def is_paid(self):
        """Check if payment is completed"""
        return self.payment_status == 'COMPLETED'
    
    def calculate_totals(self):
        """
        Calculate order totals from items
        This should be called when items are added/removed
        """
        self.subtotal = sum(
            item.total_price for item in self.items.all()
        )
        
        # Calculate tax (18% GST for India)
        self.tax = self.subtotal * 0.18
        
        # Free shipping over ₹500, otherwise ₹50
        if self.subtotal >= 500:
            self.shipping_cost = 0
        else:
            self.shipping_cost = 50
        
        # Calculate final total
        self.total = self.subtotal + self.tax + self.shipping_cost
        
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        # Index for faster queries
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]


class OrderItem(models.Model):
    """
    OrderItem Model - Individual items within an order
    
    One order contains many items.
    Each OrderItem represents:
    - One product
    - Quantity ordered
    - Price at time of purchase (important! product price might change later)
    
    Why separate model from Order?
    - One order can have multiple products
    - We need to track quantity of each
    - We need to preserve price at purchase time
    - Makes database queries more efficient
    """
    
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        help_text="Order this item belongs to"
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # Don't delete if product is deleted
        help_text="Product purchased"
    )
    
    # Snapshot of product details at time of purchase
    # These don't change even if product is updated later
    product_name = models.CharField(
        max_length=200,
        help_text="Product name at time of purchase"
    )
    
    product_sku = models.CharField(
        max_length=50,
        blank=True,
        help_text="Product SKU at time of purchase"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per unit at time of purchase"
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        help_text="Quantity ordered"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """
        Capture product details at time of order
        This creates a snapshot so we have correct info even if
        product is modified or deleted later
        """
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.price:
            self.price = self.product.get_display_price
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order: {self.order.order_number})"
    
    @property
    def total_price(self):
        """Calculate total for this line item"""
        return self.price * self.quantity
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


"""
How Orders Work in Practice:

1. SHOPPING FLOW:
   - Customer browses products
   - Adds items to cart (stored in session)
   - Goes to checkout
   - Fills in shipping info
   - Confirms order
   - Order and OrderItems are created
   - Cart is cleared

2. ORDER CREATION:
   When customer clicks "Place Order":
   
   order = Order.objects.create(
       user=request.user,
       shipping_name=...,
       shipping_address=...,
       ...
   )
   
   # Create OrderItem for each cart item
   for cart_item in cart:
       OrderItem.objects.create(
           order=order,
           product=cart_item.product,
           quantity=cart_item.quantity
       )
   
   # Calculate totals
   order.calculate_totals()

3. ORDER MANAGEMENT:
   - Customer can view their orders
   - Admin can see all orders
   - Staff can update order status
   - Status changes trigger notifications (email/SMS)

4. WHY WE SNAPSHOT PRODUCT DATA:
   Imagine customer orders "Blue T-Shirt" for ₹500.
   Next week, you change the product name to "Classic Blue Tee"
   and price to ₹600.
   
   Without snapshot: Their order shows wrong name and price
   With snapshot: Order shows exactly what they bought and paid
   
   This is legally important! Order is a contract.

5. ORDER STATUS WORKFLOW:
   PENDING → Customer places order
      ↓
   CONFIRMED → Payment verified
      ↓
   PROCESSING → Admin prepares shipment
      ↓
   SHIPPED → Shipped with tracking number
      ↓
   DELIVERED → Customer receives order
   
   At any point: CANCELLED or REFUNDED if issues occur
"""