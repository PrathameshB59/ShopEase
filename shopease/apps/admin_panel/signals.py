"""
========================================
EMAIL AUTOMATION SIGNALS
========================================

Automatically send emails when order status changes.

Uses Django signals to detect status changes and send
appropriate emails to customers.

Signals:
- pre_save on Order model: Detect status changes
- Send email with new status information
"""

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.orders.models import Order
from apps.cart.models import CartItem
from apps.admin_panel.models import ProductEngagement


@receiver(pre_save, sender=Order)
def send_order_status_email(sender, instance, **kwargs):
    """
    Send email notification when order status changes.

    Triggered before saving an Order instance.
    Compares old and new status, sends email if changed.

    Args:
        sender: Order model class
        instance: Order instance being saved
        **kwargs: Additional signal parameters
    """
    # Only process if this is an update (not a new order)
    if not instance.pk:
        return

    try:
        # Get the old order from database
        old_order = Order.objects.get(pk=instance.pk)

        # Check if status has changed
        if old_order.status == instance.status:
            return  # No change, don't send email

        # Prepare email context
        context = {
            'order': instance,
            'old_status': old_order.get_status_display(),
            'new_status': instance.get_status_display(),
            'customer_name': instance.shipping_full_name,
            'order_id_short': str(instance.order_id)[:8],
            'company_name': 'ShopEase',
            'support_email': settings.ADMIN_EMAIL,
        }

        # Render email templates
        subject = f'Order #{str(instance.order_id)[:8]} Status Update - {instance.get_status_display()}'

        # HTML version
        html_message = render_to_string(
            'emails/order_status_change.html',
            context
        )

        # Plain text version
        plain_message = render_to_string(
            'emails/order_status_change.txt',
            context
        )

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.shipping_email],
            html_message=html_message,
            fail_silently=True,  # Don't break order updates if email fails
        )

    except Order.DoesNotExist:
        # This shouldn't happen, but handle gracefully
        pass
    except Exception as e:
        # Log error but don't break the order save operation
        print(f"Error sending order status email: {str(e)}")
        pass


# ==========================================
# PRODUCT ENGAGEMENT TRACKING
# ==========================================

@receiver(post_save, sender=CartItem)
def track_cart_addition(sender, instance, created, **kwargs):
    """
    Track when a product is added to cart.

    Triggered after CartItem is created.
    Records engagement for analytics.
    """
    if created:  # Only track new additions, not updates
        try:
            ProductEngagement.objects.create(
                product=instance.product,
                user=instance.cart.user if instance.cart.user else None,
                session_key=instance.cart.session_key,
                action='ADD_TO_CART'
            )
        except Exception as e:
            # Don't break cart operations if tracking fails
            print(f"Error tracking cart addition: {str(e)}")
            pass


@receiver(post_delete, sender=CartItem)
def track_cart_removal(sender, instance, **kwargs):
    """
    Track when a product is removed from cart.

    Triggered after CartItem is deleted.
    """
    try:
        ProductEngagement.objects.create(
            product=instance.product,
            user=instance.cart.user if instance.cart.user else None,
            session_key=instance.cart.session_key,
            action='REMOVE_FROM_CART'
        )
    except Exception as e:
        # Don't break cart operations if tracking fails
        print(f"Error tracking cart removal: {str(e)}")
        pass
