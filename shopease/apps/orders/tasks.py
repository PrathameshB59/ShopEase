"""
========================================
ORDER BACKGROUND TASKS
========================================

Celery tasks for order processing:
- Send order confirmation emails
- Send order status update emails
- Log order events to MongoDB
- Generate invoices
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    """
    Send order confirmation email to customer.

    Args:
        order_id: The ID of the order

    Retries: 3 times with exponential backoff
    """
    try:
        order = Order.objects.select_related('user').get(id=order_id)

        subject = f'Order Confirmation #{str(order.order_id)[:8]}'

        # Simple text email (you can create HTML template later)
        message = f'''
        Dear {order.user.first_name or order.user.username},

        Thank you for your order!

        Order Details:
        - Order Number: {str(order.order_id)[:8]}
        - Total Amount: ₹{order.total_amount}
        - Status: {order.get_status_display()}

        We'll send you another email when your order ships.

        Thank you for shopping with ShopEase!

        Best regards,
        The ShopEase Team
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )

        logger.info(f"Order confirmation email sent for order {str(order.order_id)[:8]}")
        return f"Email sent to {order.user.email}"

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Order {order_id} not found"

    except Exception as exc:
        logger.error(f"Error sending email for order {order_id}: {exc}")
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_order_status_update_email(self, order_id, new_status):
    """
    Send email when order status changes.

    Args:
        order_id: The ID of the order
        new_status: The new order status
    """
    try:
        order = Order.objects.select_related('user').get(id=order_id)

        status_messages = {
            'PROCESSING': 'is being processed',
            'SHIPPED': 'has been shipped',
            'DELIVERED': 'has been delivered',
            'CANCELLED': 'has been cancelled',
        }

        subject = f'Order Update #{str(order.order_id)[:8]}'
        message = f'''
        Dear {order.user.first_name or order.user.username},

        Your order #{str(order.order_id)[:8]} {status_messages.get(new_status, 'has been updated')}.

        Order Details:
        - Total: ₹{order.total_amount}
        - Status: {order.get_status_display()}

        Track your order at: http://localhost:8000/orders/{order.id}/

        Thank you for shopping with ShopEase!
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )

        logger.info(f"Status update email sent for order {str(order.order_id)[:8]}")
        return f"Status update email sent to {order.user.email}"

    except Exception as exc:
        logger.error(f"Error sending status update email: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def log_order_to_mongodb(order_id, event_type='ORDER_CREATED'):
    """
    Log order events to MongoDB for analytics.

    Args:
        order_id: The ID of the order
        event_type: Type of event (ORDER_CREATED, STATUS_CHANGED, etc.)
    """
    try:
        from django.conf import settings
        from datetime import datetime

        order = Order.objects.select_related('user').get(id=order_id)

        if hasattr(settings, 'mongo_db') and settings.mongo_db:
            event_data = {
                'event_type': event_type,
                'order_id': order.id,
                'order_number': str(order.order_id)[:8],
                'user_id': order.user.id,
                'user_email': order.user.email,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'timestamp': datetime.utcnow(),
            }

            settings.mongo_db.order_events.insert_one(event_data)
            logger.info(f"Order {str(order.order_id)[:8]} logged to MongoDB")
        else:
            logger.warning("MongoDB not configured - skipping order logging")

    except Exception as exc:
        logger.error(f"Error logging to MongoDB: {exc}")


@shared_task
def update_stock_after_order(order_id):
    """
    Update product stock counts after order is placed.

    This is redundant if done in the view, but useful for
    order imports or manual order creation.
    """
    try:
        order = Order.objects.prefetch_related('items__product').get(id=order_id)

        for item in order.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        logger.info(f"Stock updated for order {str(order.order_id)[:8]}")

    except Exception as exc:
        logger.error(f"Error updating stock for order {order_id}: {exc}")
