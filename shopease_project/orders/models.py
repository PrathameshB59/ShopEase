# orders/models.py
"""
ORDER MODELS
=============
This file defines models for managing customer orders.

Models:
1. Order - Main order with shipping info, payment details, status
2. OrderItem - Individual products within an order (line items)

Relationship: One Order has Many OrderItems

Example:
Order #12345
  - OrderItem: iPhone 15 Pro x 1 @ $999
  - OrderItem: AirPods Pro x 2 @ $249
  - Total: $1,497
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product
import uuid


# ============================================================================
# ORDER MODEL
# ============================================================================
class Order(models.Model):
    """
    ORDER MODEL
    ============
    Represents a customer's order/purchase.
    
    Database table: orders_order
    
    Contains:
    - Order identification (order number)
    - Customer information (user, shipping address)
    - Order items (through OrderItem model)
    - Financial details (subtotal, tax, shipping, total)
    - Status tracking (pending, confirmed, shipped, delivered, cancelled)
    - Payment information
    - Timestamps
    """
    
    # ORDER STATUS CHOICES
    # =====================
    # Different stages an order goes through
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),           # Just created, awaiting payment
        ('CONFIRMED', 'Confirmed'),       # Payment confirmed, processing
        ('PROCESSING', 'Processing'),     # Being prepared for shipment
        ('SHIPPED', 'Shipped'),           # Shipped to customer
        ('DELIVERED', 'Delivered'),       # Successfully delivered
        ('CANCELLED', 'Cancelled'),       # Order cancelled
        ('REFUNDED', 'Refunded'),         # Payment refunded
    )
    
    # PAYMENT STATUS CHOICES
    # =======================
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),           # Payment not yet received
        ('PAID', 'Paid'),                 # Payment successful
        ('FAILED', 'Failed'),             # Payment failed
        ('REFUNDED', 'Refunded'),         # Payment refunded to customer
    )
    
    # PAYMENT METHOD CHOICES
    # =======================
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),      # Pay when product arrives
        ('CARD', 'Credit/Debit Card'),    # Online card payment
        ('UPI', 'UPI'),                   # UPI payment (India)
        ('WALLET', 'Digital Wallet'),     # PayPal, Google Pay, etc.
        ('BANK', 'Bank Transfer'),        # Direct bank transfer
    )
    
    # ORDER IDENTIFICATION
    # =====================
    
    # Unique order number shown to customers
    # Example: "ORD-20240115-A1B2C3"
    # max_length=50: Up to 50 characters
    # unique=True: Every order has unique number
    # editable=False: Can't be manually changed (auto-generated)
    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text='Unique order identifier'
    )
    
    # CUSTOMER INFORMATION
    # =====================
    
    # Link to user who placed the order
    # ForeignKey: Many orders can belong to one user
    # on_delete=models.CASCADE: If user deleted, delete their orders too
    # related_name='orders': Access user's orders: user.orders.all()
    # null=True: Allows guest checkout (orders without user account)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        help_text='Customer who placed the order (null for guest checkout)'
    )
    
    # SHIPPING INFORMATION
    # =====================
    # These fields store where to ship the order
    # We store this separately from user profile because:
    # 1. User might want to ship to different address
    # 2. Need permanent record even if user changes their address later
    
    shipping_name = models.CharField(
        max_length=200,
        help_text='Recipient full name'
    )
    
    shipping_email = models.EmailField(
        help_text='Contact email for shipping updates'
    )
    
    shipping_phone = models.CharField(
        max_length=15,
        help_text='Contact phone number'
    )
    
    shipping_address = models.TextField(
        help_text='Full street address'
    )
    
    shipping_city = models.CharField(
        max_length=100,
        help_text='City name'
    )
    
    shipping_state = models.CharField(
        max_length=100,
        help_text='State/Province'
    )
    
    shipping_zip_code = models.CharField(
        max_length=10,
        help_text='Postal/ZIP code'
    )
    
    shipping_country = models.CharField(
        max_length=100,
        default='India',
        help_text='Country'
    )
    
    # FINANCIAL INFORMATION
    # ======================
    
    # Subtotal (sum of all product prices)
    # DecimalField: Exact decimal numbers (important for money!)
    # max_digits=10: Total 10 digits (including decimals)
    # decimal_places=2: Exactly 2 decimal places (cents)
    # Example: 12345.67 or 999999.99
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Sum of all product prices'
    )
    
    # Tax amount
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Tax amount charged'
    )
    
    # Shipping cost
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Shipping/delivery charges'
    )
    
    # Discount amount (if coupon applied)
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Discount applied (if any)'
    )
    
    # Final total amount
    # subtotal + tax + shipping - discount = total
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Final amount to be paid'
    )
    
    # ORDER STATUS & PAYMENT
    # =======================
    
    # Current order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Current order status'
    )
    
    # Payment status
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text='Payment status'
    )
    
    # Payment method used
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='COD',
        help_text='How customer will pay'
    )
    
    # Transaction ID from payment gateway
    # Stores reference from Stripe, Razorpay, PayPal, etc.
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Payment gateway transaction ID'
    )
    
    # TRACKING INFORMATION
    # =====================
    
    # Shipping tracking number
    # Provided by courier (FedEx, UPS, India Post, etc.)
    tracking_number = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Courier tracking number'
    )
    
    # When order was shipped
    shipped_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date and time when order was shipped'
    )
    
    # When order was delivered
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date and time when order was delivered'
    )
    
    # NOTES
    # ======
    
    # Customer's special instructions
    # Example: "Please deliver after 6 PM", "Gift wrap requested"
    customer_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Special instructions from customer'
    )
    
    # Internal notes for admin/staff only
    # Not visible to customer
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal notes (not visible to customer)'
    )
    
    # TIMESTAMPS
    # ===========
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When order was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When order was last updated'
    )
    
    # META CLASS
    # ===========
    class Meta:
        # Default ordering: newest orders first
        ordering = ['-created_at']
        
        # Indexes for faster queries
        indexes = [
            models.Index(fields=['order_number']),      # Fast order lookup
            models.Index(fields=['user']),              # Fast user orders lookup
            models.Index(fields=['status']),            # Fast status filtering
            models.Index(fields=['-created_at']),       # Fast date sorting
        ]
        
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        # Example: "Order ORD-20240115-A1B2C3 by john_doe"
        user_name = self.user.username if self.user else "Guest"
        return f"Order {self.order_number} by {user_name}"
    
    # SAVE METHOD OVERRIDE
    # =====================
    def save(self, *args, **kwargs):
        """
        Auto-generate order number if not set
        Format: ORD-YYYYMMDD-XXXXXX (random 6 characters)
        Example: ORD-20240115-A1B2C3
        """
        if not self.order_number:
            # Get current date in YYYYMMDD format
            date_str = timezone.now().strftime('%Y%m%d')
            
            # Generate random 6-character code
            # uuid4().hex gives random hex string
            # [:6] takes first 6 characters
            # .upper() converts to uppercase
            random_code = uuid.uuid4().hex[:6].upper()
            
            # Combine: ORD-20240115-A1B2C3
            self.order_number = f"ORD-{date_str}-{random_code}"
            
            # Ensure it's unique (very rare collision, but be safe)
            while Order.objects.filter(order_number=self.order_number).exists():
                random_code = uuid.uuid4().hex[:6].upper()
                self.order_number = f"ORD-{date_str}-{random_code}"
        
        super().save(*args, **kwargs)
    
    # CUSTOM METHODS
    # ===============
    
    def calculate_total(self):
        """
        Calculate and update order total
        Formula: subtotal + tax + shipping - discount
        Call this after adding/removing order items
        """
        # Calculate subtotal from order items
        self.subtotal = sum(item.get_total() for item in self.items.all())
        
        # Calculate total (you can add tax calculation logic here)
        self.total = self.subtotal + self.tax + self.shipping_cost - self.discount
        
        self.save()
    
    def get_total_items(self):
        """
        Get total number of items in order
        Returns: Integer (sum of all quantities)
        Example: 2 iPhones + 3 cases = 5 items
        """
        return sum(item.quantity for item in self.items.all())
    
    def can_be_cancelled(self):
        """
        Check if order can be cancelled
        Returns: True if order is in cancellable status
        Usually can't cancel once shipped
        """
        return self.status in ['PENDING', 'CONFIRMED', 'PROCESSING']
    
    def get_status_display_color(self):
        """
        Get color for status badge in templates
        Returns: CSS color class
        """
        status_colors = {
            'PENDING': 'warning',
            'CONFIRMED': 'info',
            'PROCESSING': 'primary',
            'SHIPPED': 'info',
            'DELIVERED': 'success',
            'CANCELLED': 'danger',
            'REFUNDED': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_full_shipping_address(self):
        """
        Get formatted shipping address as string
        Returns: Multi-line address string
        """
        return f"""{self.shipping_name}
{self.shipping_address}
{self.shipping_city}, {self.shipping_state} {self.shipping_zip_code}
{self.shipping_country}
Phone: {self.shipping_phone}
Email: {self.shipping_email}"""


# ============================================================================
# ORDER ITEM MODEL
# ============================================================================
class OrderItem(models.Model):
    """
    ORDER ITEM MODEL
    =================
    Represents individual products within an order (line items).
    
    Database table: orders_orderitem
    
    Example:
    Order #12345 contains:
      - OrderItem 1: iPhone 15 Pro, qty=1, price=$999
      - OrderItem 2: AirPods Pro, qty=2, price=$249
    
    Why separate model?
    - One order can have multiple products
    - Each product can have different quantity
    - Need to store price at time of purchase (product price might change later)
    """
    
    # ORDER RELATIONSHIP
    # ===================
    # ForeignKey: Links item to one order
    # on_delete=models.CASCADE: If order deleted, delete its items too
    # related_name='items': Access order items: order.items.all()
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Which order this item belongs to'
    )
    
    # PRODUCT RELATIONSHIP
    # =====================
    # ForeignKey: Links item to the product
    # on_delete=models.SET_NULL: If product deleted, keep order item but set product to NULL
    # null=True: Product can be NULL if deleted (we keep the order record)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Product that was ordered'
    )
    
    # PRODUCT SNAPSHOT
    # =================
    # We store product name and price at time of purchase
    # Why? Product details might change or be deleted later
    # Order is a permanent record of what was purchased at what price
    
    product_name = models.CharField(
        max_length=200,
        help_text='Product name at time of purchase'
    )
    
    # Price per unit at time of purchase
    # Even if product price changes later, order shows what customer paid
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price per unit at time of purchase'
    )
    
    # QUANTITY
    # =========
    # How many units of this product
    # default=1: At least 1 item
    quantity = models.IntegerField(
        default=1,
        help_text='Quantity ordered'
    )
    
    # TIMESTAMP
    # ==========
    created_at = models.DateTimeField(auto_now_add=True)
    
    # META CLASS
    # ===========
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    # STRING REPRESENTATION
    # ======================
    def __str__(self):
        # Example: "2x iPhone 15 Pro ($999 each)"
        return f"{self.quantity}x {self.product_name} (${self.price} each)"
    
    # CUSTOM METHODS
    # ===============
    
    def get_total(self):
        """
        Calculate total price for this line item
        Formula: price × quantity
        Returns: Decimal
        Example: $999 × 2 = $1,998
        """
        return self.price * self.quantity
    
    # Make get_total available as a property
    total_price = property(get_total)
    
    def save(self, *args, **kwargs):
        """
        Auto-populate product_name and price from product if not set
        This happens when creating order item from product
        """
        if self.product and not self.product_name:
            # Copy product name to order item
            self.product_name = self.product.name
        
        if self.product and not self.price:
            # Copy current product price to order item
            # Use sale price if available, otherwise regular price
            self.price = self.product.get_price()
        
        super().save(*args, **kwargs)


# ============================================================================
# DATABASE RELATIONSHIP SUMMARY
# ============================================================================
"""
RELATIONSHIPS:
==============

User (1) -----> (Many) Orders
Order (1) -----> (Many) OrderItems
OrderItem (Many) -----> (1) Product

In code:
--------
# Get all orders for a user:
user_orders = user.orders.all()

# Get all items in an order:
order_items = order.items.all()

# Get total items in order:
total_items = order.get_total_items()

# Calculate order total:
order.calculate_total()

# Get item's product:
product = order_item.product

# Get item's total price:
item_total = order_item.get_total()
"""