"""
========================================
ADMIN PANEL MODELS - Role & Permissions
========================================

This module defines the database models for the custom admin panel including:
- AdminRole: Custom role-based access control system
- AdminActivity: Audit trail for admin actions

Additional models (analytics) will be added in later phases.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


# ==========================================
# ROLE & PERMISSION SYSTEM
# ==========================================

class AdminRole(models.Model):
    """
    Custom role system for granular admin permissions.

    Extends Django's Group system with custom permissions for:
    - Order management
    - Product/inventory management
    - Review moderation
    - User/role management
    - Analytics access

    Each staff user can have one role with specific permissions.
    """

    ROLE_CHOICES = [
        ('CUSTOMER_SERVICE', 'Customer Service'),
        ('INVENTORY_MANAGER', 'Inventory Manager'),
        ('MARKETING_MANAGER', 'Marketing Manager'),
        ('ORDER_MANAGER', 'Order Manager'),
        ('SUPER_ADMIN', 'Super Admin'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_role',
        help_text="Staff user assigned to this role"
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        help_text="Role type determines default permissions (blank for custom roles)"
    )

    # Custom Role Fields (for dynamically created roles)
    is_custom_role = models.BooleanField(
        default=False,
        help_text="True if this is a custom-created role"
    )
    custom_role_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Name of the custom role"
    )
    role_description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what this role does"
    )

    # Order Management Permissions
    can_view_orders = models.BooleanField(
        default=False,
        help_text="Can view order list and details"
    )
    can_edit_orders = models.BooleanField(
        default=False,
        help_text="Can change order status and add notes"
    )
    can_process_refunds = models.BooleanField(
        default=False,
        help_text="Can approve and process refund requests"
    )

    # Product Management Permissions
    can_view_products = models.BooleanField(
        default=False,
        help_text="Can view product list and analytics"
    )
    can_edit_products = models.BooleanField(
        default=False,
        help_text="Can edit products and manage inventory"
    )
    can_manage_featured = models.BooleanField(
        default=False,
        help_text="Can select/modify featured products"
    )

    # Review Management Permissions
    can_moderate_reviews = models.BooleanField(
        default=False,
        help_text="Can approve/reject customer reviews"
    )

    # User Management Permissions
    can_view_users = models.BooleanField(
        default=False,
        help_text="Can view user list and profiles"
    )
    can_manage_roles = models.BooleanField(
        default=False,
        help_text="Can assign roles to staff users"
    )

    # Analytics & Reporting Permissions
    can_view_analytics = models.BooleanField(
        default=False,
        help_text="Can access analytics and reports"
    )
    can_export_data = models.BooleanField(
        default=False,
        help_text="Can export data to CSV/Excel"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Role"
        verbose_name_plural = "Admin Roles"
        indexes = [
            models.Index(fields=['user', 'role']),
        ]

    def __str__(self):
        if self.is_custom_role and self.custom_role_name:
            return f"{self.user.username} - {self.custom_role_name} (Custom)"
        return f"{self.user.username} - {self.get_role_display()}"

    def get_role_name(self):
        """Get the display name of the role (custom or predefined)."""
        if self.is_custom_role and self.custom_role_name:
            return self.custom_role_name
        return self.get_role_display() if self.role else "No Role"

    @classmethod
    def get_default_permissions(cls, role):
        """
        Get default permissions for a given role type.

        Args:
            role: Role type string (e.g., 'CUSTOMER_SERVICE')

        Returns:
            Dictionary of permission field names and their default values
        """
        ROLE_PERMISSIONS = {
            'CUSTOMER_SERVICE': {
                'can_view_orders': True,
                'can_edit_orders': True,
                'can_moderate_reviews': True,
                'can_view_analytics': False,
            },
            'INVENTORY_MANAGER': {
                'can_view_products': True,
                'can_edit_products': True,
                'can_view_analytics': True,
            },
            'MARKETING_MANAGER': {
                'can_view_products': True,
                'can_manage_featured': True,
                'can_view_analytics': True,
                'can_export_data': True,
            },
            'ORDER_MANAGER': {
                'can_view_orders': True,
                'can_edit_orders': True,
                'can_process_refunds': True,
                'can_view_analytics': True,
            },
            'SUPER_ADMIN': {
                'can_view_orders': True,
                'can_edit_orders': True,
                'can_process_refunds': True,
                'can_view_products': True,
                'can_edit_products': True,
                'can_manage_featured': True,
                'can_moderate_reviews': True,
                'can_view_users': True,
                'can_manage_roles': True,
                'can_view_analytics': True,
                'can_export_data': True,
            },
        }

        return ROLE_PERMISSIONS.get(role, {})

    def save(self, *args, **kwargs):
        """
        Auto-assign default permissions based on role if this is a new instance.
        """
        if not self.pk:  # New instance
            default_perms = self.get_default_permissions(self.role)
            for perm_name, perm_value in default_perms.items():
                setattr(self, perm_name, perm_value)
        super().save(*args, **kwargs)


# ==========================================
# ACTIVITY LOGGING - AUDIT TRAIL
# ==========================================

class AdminActivity(models.Model):
    """
    Track admin user actions for audit trail and compliance.

    Every significant action in the admin panel is logged with:
    - Who performed the action
    - What action was performed
    - When it happened
    - IP address for security
    - Optional references to affected objects

    This provides accountability and helps investigate issues.
    """

    ACTION_CHOICES = [
        ('ORDER_STATUS_CHANGE', 'Changed Order Status'),
        ('REFUND_PROCESSED', 'Processed Refund'),
        ('PRODUCT_UPDATED', 'Updated Product'),
        ('FEATURED_CHANGED', 'Changed Featured Products'),
        ('REVIEW_MODERATED', 'Moderated Review'),
        ('ROLE_ASSIGNED', 'Assigned Role'),
        ('BULK_ACTION', 'Performed Bulk Action'),
        ('USER_CREATED', 'Created User'),
        ('USER_UPDATED', 'Updated User'),
        ('INVOICE_GENERATED', 'Generated Invoice'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_activities',
        help_text="Admin user who performed the action"
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed"
    )

    description = models.TextField(
        help_text="Detailed description of the action"
    )

    # Optional references to specific objects
    order_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Related order ID (if applicable)"
    )

    product_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Related product ID (if applicable)"
    )

    # Security & metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the admin user"
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action was performed"
    )

    class Meta:
        verbose_name = "Admin Activity"
        verbose_name_plural = "Admin Activities"
        ordering = ['-timestamp']  # Newest first
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        username = self.user.username if self.user else 'Unknown'
        return f"{username} - {self.get_action_display()} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# ==========================================
# REFUND MANAGEMENT
# ==========================================

class Refund(models.Model):
    """
    Refund and return management system.

    Tracks refund requests from customers and allows admins to:
    - Approve or reject refund requests
    - Process approved refunds
    - Track return status
    - Restore product stock on completion

    Workflow:
    1. Customer requests refund (or admin creates on behalf)
    2. Admin reviews and approves/rejects
    3. If approved, admin processes refund
    4. Stock is restored if return is received
    """

    STATUS_CHOICES = [
        ('REQUESTED', 'Refund Requested'),
        ('APPROVED', 'Approved'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    REASON_CHOICES = [
        ('DEFECTIVE', 'Defective Product'),
        ('WRONG_ITEM', 'Wrong Item Received'),
        ('NOT_AS_DESCRIBED', 'Not As Described'),
        ('CHANGED_MIND', 'Changed Mind'),
        ('DAMAGED', 'Damaged in Shipping'),
        ('OTHER', 'Other'),
    ]

    refund_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique refund identifier"
    )

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='refunds',
        help_text="Order associated with this refund"
    )

    # Refund details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Refund amount"
    )

    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        help_text="Reason for refund"
    )

    description = models.TextField(
        help_text="Detailed explanation for the refund"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REQUESTED',
        db_index=True,
        help_text="Current status of refund"
    )

    # Processing information
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds',
        help_text="Admin who processed this refund"
    )

    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to customer)"
    )

    # Return tracking
    return_requested = models.BooleanField(
        default=False,
        help_text="Whether customer needs to return the product"
    )

    return_received = models.BooleanField(
        default=False,
        help_text="Whether returned product has been received"
    )

    restore_stock = models.BooleanField(
        default=True,
        help_text="Restore product stock when refund is completed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When refund was approved/rejected"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When refund was completed"
    )

    class Meta:
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Refund #{str(self.refund_id)[:8]} - Order {str(self.order.order_id)[:8]}"

    def approve(self, admin_user):
        """
        Approve the refund request.

        Args:
            admin_user: User who is approving the refund
        """
        self.status = 'APPROVED'
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_by', 'processed_at'])

    def reject(self, admin_user, reason=''):
        """
        Reject the refund request.

        Args:
            admin_user: User who is rejecting the refund
            reason: Reason for rejection
        """
        self.status = 'REJECTED'
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        if reason:
            self.admin_notes += f"\nRejection reason: {reason}"
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'admin_notes'])

    def complete(self, admin_user):
        """
        Mark refund as completed and restore stock if needed.

        Args:
            admin_user: User who is completing the refund
        """
        self.status = 'COMPLETED'
        self.processed_by = admin_user
        self.completed_at = timezone.now()

        # Restore stock if needed
        if self.restore_stock and self.return_received:
            for item in self.order.items.all():
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])

        self.save(update_fields=['status', 'processed_by', 'completed_at'])


# ==========================================
# PRODUCT ANALYTICS & TRACKING
# ==========================================

class ProductView(models.Model):
    """
    Track individual product page views.

    Captures every time a product detail page is viewed.
    Used to calculate view counts and engagement metrics.

    Tracks both authenticated users and anonymous visitors via session.
    """

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='views',
        help_text="Product that was viewed"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who viewed (if authenticated)"
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Session key for anonymous users"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of viewer"
    )

    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="Browser user agent string"
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the product was viewed"
    )

    class Meta:
        verbose_name = "Product View"
        verbose_name_plural = "Product Views"
        indexes = [
            models.Index(fields=['product', '-viewed_at']),
            models.Index(fields=['-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"{self.product.name} - {user_info} at {self.viewed_at.strftime('%Y-%m-%d %H:%M')}"


class ProductEngagement(models.Model):
    """
    Track product engagement actions (add to cart, wishlist, etc.).

    Captures customer interaction with products beyond just viewing.
    Higher engagement = higher interest = better candidate for featuring.
    """

    ACTION_CHOICES = [
        ('ADD_TO_CART', 'Added to Cart'),
        ('ADD_TO_WISHLIST', 'Added to Wishlist'),
        ('REMOVE_FROM_CART', 'Removed from Cart'),
        ('REMOVE_FROM_WISHLIST', 'Removed from Wishlist'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='engagements',
        help_text="Product being interacted with"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who performed action (if authenticated)"
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Session key for anonymous users"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of engagement action"
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )

    class Meta:
        verbose_name = "Product Engagement"
        verbose_name_plural = "Product Engagements"
        indexes = [
            models.Index(fields=['product', 'action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"{self.product.name} - {self.get_action_display()} by {user_info}"


class ProductAnalytics(models.Model):
    """
    Aggregated daily analytics per product.

    Updated via scheduled management command (aggregate_analytics).
    Stores all metrics needed for the featured product scoring algorithm.

    Featured Score Formula:
    - Revenue: 40%
    - Purchase count: 20%
    - Engagement (cart+wishlist): 15%
    - Views: 10%
    - Rating: 10%
    - Reviews: 5%
    """

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='analytics',
        help_text="Product these analytics belong to"
    )

    date = models.DateField(
        db_index=True,
        help_text="Date of these analytics"
    )

    # View metrics
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Total page views for this day"
    )

    unique_viewers = models.PositiveIntegerField(
        default=0,
        help_text="Unique visitors (by user or session)"
    )

    # Engagement metrics
    add_to_cart_count = models.PositiveIntegerField(
        default=0,
        help_text="Times added to cart"
    )

    wishlist_count = models.PositiveIntegerField(
        default=0,
        help_text="Times added to wishlist"
    )

    # Purchase metrics (from OrderItem)
    purchase_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times purchased"
    )

    revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Revenue generated from this product"
    )

    # Review metrics (from Review model)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average customer rating"
    )

    review_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of reviews"
    )

    # Calculated featured score (0-100)
    featured_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Calculated score for auto-featuring (0-100)"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Analytics"
        verbose_name_plural = "Product Analytics"
        unique_together = ['product', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', '-featured_score']),
            models.Index(fields=['product', '-date']),
            models.Index(fields=['-featured_score']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.date} (Score: {self.featured_score})"

    def calculate_featured_score(self):
        """
        Calculate weighted score for auto-featuring.

        Weights (customizable):
        - Revenue: 40% (max 40 points)
        - Purchase count: 20% (max 20 points)
        - Engagement: 15% (max 15 points)
        - Views: 10% (max 10 points)
        - Rating: 10% (max 10 points)
        - Reviews: 5% (max 5 points)

        Returns:
            Decimal: Score from 0-100
        """
        score = Decimal('0.00')

        # Revenue component (40 points max)
        # Normalize: ₹1000 revenue = 40 points
        score += min(float(self.revenue) / 1000 * 40, 40)

        # Purchase count component (20 points max)
        # Each purchase = 2 points, capped at 20
        score += min(self.purchase_count * 2, 20)

        # Engagement component (15 points max)
        # Cart adds worth more than wishlist adds
        engagement = self.add_to_cart_count + (self.wishlist_count * 0.5)
        score += min(engagement / 10 * 15, 15)

        # View count component (10 points max)
        # 100 views = 10 points
        score += min(self.view_count / 100 * 10, 10)

        # Rating component (10 points max)
        # 5-star rating = 10 points
        if self.average_rating:
            score += float(self.average_rating) * 2

        # Review count component (5 points max)
        # 10 reviews = 5 points
        score += min(self.review_count / 10 * 5, 5)

        return Decimal(str(round(score, 2)))

    def save(self, *args, **kwargs):
        """Auto-calculate featured score on save."""
        self.featured_score = self.calculate_featured_score()
        super().save(*args, **kwargs)


class FeaturedProduct(models.Model):
    """
    Manual featured product selection with override capability.

    Allows admins to:
    - Manually select products to feature
    - Override auto-suggestions
    - Set priority order
    - Set expiry dates for temporary promotions
    """

    SOURCE_CHOICES = [
        ('MANUAL', 'Manually Selected'),
        ('AUTO', 'Auto-suggested'),
    ]

    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='featured_entry',
        help_text="Featured product"
    )

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='MANUAL',
        help_text="How this product was featured"
    )

    priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Display priority (lower = higher priority)"
    )

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='featured_selections',
        help_text="Admin who featured this product"
    )

    reason = models.TextField(
        blank=True,
        help_text="Why this product is featured (internal notes)"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this feature is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Auto-remove from featured after this date"
    )

    class Meta:
        verbose_name = "Featured Product"
        verbose_name_plural = "Featured Products"
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'priority']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_source_display()} (Priority: {self.priority})"

    def is_expired(self):
        """Check if this featured entry has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
