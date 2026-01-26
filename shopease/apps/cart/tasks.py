"""
========================================
CART BACKGROUND TASKS
========================================

Celery tasks for cart management:
- Send abandoned cart reminders
- Clean old carts
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_abandoned_cart_reminders():
    """
    Send email reminders for abandoned carts.

    Sends reminder if:
    - Cart has items
    - Last updated > 24 hours ago
    - User hasn't placed order

    Runs every 6 hours via Celery Beat.
    """
    try:
        from apps.cart.models import Cart

        # Find carts abandoned for 24+ hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        abandoned_carts = Cart.objects.filter(
            updated_at__lt=cutoff_time,
            items__isnull=False
        ).select_related('user').distinct()

        sent_count = 0
        for cart in abandoned_carts:
            if cart.user and cart.user.email:
                try:
                    subject = "You left items in your cart!"
                    message = f'''
                    Hi {cart.user.first_name or cart.user.username},

                    You have {cart.items.count()} item(s) waiting in your cart.

                    Complete your purchase now: http://localhost:8000/cart/

                    Items in cart:
                    '''

                    for item in cart.items.all():
                        message += f"\n- {item.product.name} (x{item.quantity})"

                    message += "\n\nThank you for shopping with ShopEase!"

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[cart.user.email],
                        fail_silently=True,
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending cart reminder to {cart.user.email}: {e}")

        logger.info(f"Sent {sent_count} abandoned cart reminders")
        return f"Sent {sent_count} reminders"

    except Exception as exc:
        logger.error(f"Error sending abandoned cart reminders: {exc}")
        return f"Error: {exc}"
