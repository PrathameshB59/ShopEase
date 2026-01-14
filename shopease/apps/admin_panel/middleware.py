"""
========================================
PRODUCT VIEW TRACKING MIDDLEWARE
========================================

Automatically tracks product page views for analytics.

This middleware:
- Detects when a product detail page is accessed
- Records the view in ProductView model
- Captures user/session information
- Works for both authenticated and anonymous users

Minimal performance impact - uses async database write.
"""

from apps.admin_panel.models import ProductView
from apps.products.models import Product


class ProductViewTrackingMiddleware:
    """
    Middleware to automatically track product page views.

    Intercepts requests to product detail pages and creates
    ProductView records for analytics.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Track product views after response (non-blocking)
        self._track_product_view(request)

        return response

    def _track_product_view(self, request):
        """
        Track product detail page views.

        Only tracks GET requests to product detail pages.
        Extracts product slug from URL and creates ProductView record.
        """
        # Only track GET requests
        if request.method != 'GET':
            return

        # Check if this is a product detail page
        # URL pattern: /products/<slug>/
        if not request.path.startswith('/products/'):
            return

        # Get URL resolver match
        if not hasattr(request, 'resolver_match') or not request.resolver_match:
            return

        # Check if this is the product detail view
        if request.resolver_match.url_name != 'product_detail':
            return

        # Extract product slug from URL kwargs
        slug = request.resolver_match.kwargs.get('slug')
        if not slug:
            return

        try:
            # Get the product
            product = Product.objects.get(slug=slug, is_active=True)

            # Ensure session exists
            if not request.session.session_key:
                request.session.create()

            # Create ProductView record
            ProductView.objects.create(
                product=product,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )

        except Product.DoesNotExist:
            # Product not found or not active
            pass
        except Exception as e:
            # Don't break the request if tracking fails
            # In production, you might want to log this
            print(f"Error tracking product view: {str(e)}")
            pass

    def _get_client_ip(self, request):
        """
        Extract client IP address from request.

        Handles proxies via X-Forwarded-For header.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
