"""
========================================
SHOPEASE MIDDLEWARE
========================================

1. ProductViewTrackingMiddleware - Tracks product page views for analytics
2. AdminPortAccessMiddleware - Restricts admin server to staff users only
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from apps.admin_panel.models import ProductView
from apps.products.models import Product


class AdminPortAccessMiddleware:
    """
    Middleware to restrict admin server (port 8080) to staff users only.

    Behavior:
    - Redirects unauthenticated users to customer port login (8000)
    - Allows authenticated staff users to access admin portal
    - Redirects non-staff users to customer server
    - Allows static/media files

    Only active when SERVER_TYPE = 'admin'
    """

    # Paths that should be accessible without authentication
    ALLOWED_PATHS = [
        '/static/',
        '/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply on admin server
        if getattr(settings, 'SERVER_TYPE', None) != 'admin':
            return self.get_response(request)

        customer_port = getattr(settings, 'CUSTOMER_SERVER_PORT', 8000)

        # Allow static/media files
        if self._is_allowed_path(request.path):
            return self.get_response(request)

        # Check authentication
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                # Staff user - allow access
                return self.get_response(request)
            else:
                # Non-staff user - redirect to customer server
                messages.error(
                    request,
                    'Access denied. This portal is for staff members only.'
                )
                return redirect(f'http://localhost:{customer_port}/')
        else:
            # Not authenticated - redirect to customer port login
            return redirect(f'http://localhost:{customer_port}/accounts/auth/')

    def _is_allowed_path(self, path):
        """Check if the path is in the allowed list."""
        for allowed in self.ALLOWED_PATHS:
            if path.startswith(allowed):
                return True
        return False


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
