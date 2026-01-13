"""
========================================
ADMIN PANEL URL CONFIGURATION
========================================

URL patterns for the custom admin panel at /dashboard/.

This will be expanded in later phases with:
- Order management routes
- Product analytics routes
- Review moderation routes
- User management routes
- Reports routes
"""

from django.urls import path
from apps.admin_panel.views import dashboard

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard - Main landing page
    path('', dashboard.dashboard_view, name='dashboard'),

    # Phase 2: Order management (to be added)
    # path('orders/', ..., name='order_list'),
    # path('orders/<uuid:order_id>/', ..., name='order_detail'),

    # Phase 3: Products & analytics (to be added)
    # path('products/', ..., name='product_list'),
    # path('products/analytics/', ..., name='product_analytics'),

    # Phase 4: Reviews (to be added)
    # path('reviews/', ..., name='review_list'),

    # Phase 5: Users (to be added)
    # path('users/', ..., name='user_list'),

    # Phase 6: Reports (to be added)
    # path('reports/sales/', ..., name='sales_report'),
]
