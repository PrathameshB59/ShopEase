"""
========================================
ADMIN PANEL BACKGROUND TASKS
========================================

Celery tasks for analytics and admin operations:
- Update product analytics
- Generate reports
- Send admin notifications
"""

from celery import shared_task
from django.conf import settings
from django.db.models import Count, Sum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_product_analytics():
    """
    Update product analytics in MongoDB.

    Calculates and stores:
    - View counts
    - Conversion rates
    - Popular products

    Runs every hour via Celery Beat.
    """
    try:
        from apps.products.models import Product
        from apps.orders.models import OrderItem

        # Check if MongoDB is configured
        mongo_db = getattr(settings, 'mongo_db', None)
        if not mongo_db:
            logger.warning("MongoDB not configured - skipping analytics update")
            return "MongoDB not configured"

        # Get products with view counts from middleware tracking
        products = Product.objects.all()

        analytics_data = []
        for product in products:
            # Calculate metrics
            total_sold = OrderItem.objects.filter(
                product=product
            ).aggregate(total=Sum('quantity'))['total'] or 0

            analytics_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'total_sold': total_sold,
                'current_stock': product.stock,
                'price': float(product.price),
                'timestamp': datetime.utcnow(),
            })

        # Store in MongoDB
        if analytics_data:
            mongo_db.product_analytics.insert_many(analytics_data)
            logger.info(f"Updated analytics for {len(analytics_data)} products")
            return f"Updated {len(analytics_data)} products"
        else:
            logger.info("No products to update")
            return "No products found"

    except Exception as exc:
        logger.error(f"Error updating product analytics: {exc}")
        return f"Error: {exc}"


@shared_task
def send_low_stock_alert(product_id, current_stock):
    """
    Send email alert when product stock is low.

    Args:
        product_id: Product ID
        current_stock: Current stock level
    """
    try:
        from django.core.mail import send_mail
        from apps.products.models import Product

        product = Product.objects.get(id=product_id)

        subject = f'Low Stock Alert: {product.name}'
        message = f'''
        Product: {product.name}
        Current Stock: {current_stock}
        Reorder Level: 10

        Please restock this item soon.
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        logger.info(f"Low stock alert sent for {product.name}")
        return f"Alert sent for {product.name}"

    except Exception as exc:
        logger.error(f"Error sending low stock alert: {exc}")
        return f"Error: {exc}"
