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
        help_text="Role type determines default permissions"
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
        return f"{self.user.username} - {self.get_role_display()}"

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
