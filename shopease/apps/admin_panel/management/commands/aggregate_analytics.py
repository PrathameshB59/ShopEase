"""
========================================
AGGREGATE ANALYTICS MANAGEMENT COMMAND
========================================

Daily batch processing of product analytics.

This command:
- Runs daily (via cron/scheduler)
- Aggregates ProductView and ProductEngagement data
- Calculates purchase metrics from OrderItem
- Pulls review metrics from Review model
- Calculates featured_score for auto-suggestions
- Updates ProductAnalytics model

Usage:
    python manage.py aggregate_analytics
    python manage.py aggregate_analytics --date 2024-01-15

Schedule with cron (Linux/Mac):
    0 2 * * * cd /path/to/project && python manage.py aggregate_analytics

Schedule with Task Scheduler (Windows):
    Trigger: Daily at 2:00 AM
    Action: python manage.py aggregate_analytics
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import date, timedelta
from decimal import Decimal

from apps.admin_panel.models import (
    ProductView,
    ProductEngagement,
    ProductAnalytics
)
from apps.products.models import Product
from apps.orders.models import OrderItem


class Command(BaseCommand):
    help = 'Aggregate daily product analytics for featured product scoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to aggregate (YYYY-MM-DD). Defaults to yesterday.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Aggregate all active products (even with no activity)',
        )

    def handle(self, *args, **options):
        # Determine target date
        target_date = options.get('date')
        if target_date:
            try:
                target_date = date.fromisoformat(target_date)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid date format: {target_date}. Use YYYY-MM-DD.')
                )
                return
        else:
            # Default to yesterday
            target_date = (timezone.now() - timedelta(days=1)).date()

        self.stdout.write(
            self.style.SUCCESS(f'Aggregating analytics for {target_date}...')
        )

        # Get products to process
        if options.get('all'):
            products = Product.objects.filter(is_active=True)
        else:
            # Only products with activity on target date
            product_ids = set()

            # Products with views
            product_ids.update(
                ProductView.objects.filter(
                    viewed_at__date=target_date
                ).values_list('product_id', flat=True)
            )

            # Products with engagement
            product_ids.update(
                ProductEngagement.objects.filter(
                    timestamp__date=target_date
                ).values_list('product_id', flat=True)
            )

            # Products with purchases
            product_ids.update(
                OrderItem.objects.filter(
                    order__status='COMPLETED',
                    order__created_at__date=target_date
                ).values_list('product_id', flat=True)
            )

            products = Product.objects.filter(id__in=product_ids, is_active=True)

        self.stdout.write(f'Processing {products.count()} products...')

        processed_count = 0
        created_count = 0
        updated_count = 0

        for product in products:
            # === VIEW METRICS ===
            views = ProductView.objects.filter(
                product=product,
                viewed_at__date=target_date
            )

            view_count = views.count()

            # Unique viewers (by user or session)
            unique_viewers = views.values('user', 'session_key').distinct().count()

            # === ENGAGEMENT METRICS ===
            add_to_cart = ProductEngagement.objects.filter(
                product=product,
                action='ADD_TO_CART',
                timestamp__date=target_date
            ).count()

            wishlist = ProductEngagement.objects.filter(
                product=product,
                action='ADD_TO_WISHLIST',
                timestamp__date=target_date
            ).count()

            # === PURCHASE METRICS ===
            completed_orders = OrderItem.objects.filter(
                product=product,
                order__status='COMPLETED',
                order__created_at__date=target_date
            )

            purchase_count = completed_orders.count()

            # Calculate revenue
            revenue = Decimal('0.00')
            for item in completed_orders:
                revenue += Decimal(str(item.price)) * item.quantity

            # === REVIEW METRICS ===
            # Get all-time review stats (not just today's)
            reviews = product.reviews.filter(is_approved=True)
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            review_count = reviews.count()

            # Create or update ProductAnalytics
            analytics, created = ProductAnalytics.objects.update_or_create(
                product=product,
                date=target_date,
                defaults={
                    'view_count': view_count,
                    'unique_viewers': unique_viewers,
                    'add_to_cart_count': add_to_cart,
                    'wishlist_count': wishlist,
                    'purchase_count': purchase_count,
                    'revenue': revenue,
                    'average_rating': Decimal(str(avg_rating)) if avg_rating else None,
                    'review_count': review_count,
                    # featured_score will be calculated automatically on save
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            processed_count += 1

            # Progress indicator
            if processed_count % 10 == 0:
                self.stdout.write(f'Processed {processed_count}/{products.count()}...')

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Completed aggregation for {target_date}'
            )
        )
        self.stdout.write(f'  Products processed: {processed_count}')
        self.stdout.write(f'  Records created: {created_count}')
        self.stdout.write(f'  Records updated: {updated_count}')

        # Show top 5 products by featured score
        self.stdout.write('\nTop 5 products by featured score:')
        top_products = ProductAnalytics.objects.filter(
            date=target_date
        ).order_by('-featured_score')[:5]

        for i, analytics in enumerate(top_products, 1):
            self.stdout.write(
                f'  {i}. {analytics.product.name} - '
                f'Score: {analytics.featured_score} '
                f'(Views: {analytics.view_count}, '
                f'Purchases: {analytics.purchase_count}, '
                f'Revenue: ₹{analytics.revenue})'
            )

        self.stdout.write(self.style.SUCCESS('\nDone!'))
