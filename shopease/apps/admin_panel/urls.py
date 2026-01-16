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
from apps.admin_panel.views import dashboard, orders, products, reviews, users, reports

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard - Main landing page
    path('', dashboard.dashboard_view, name='dashboard'),

    # Phase 2: Order management
    path('orders/', orders.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', orders.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/update-status/', orders.update_order_status, name='update_order_status'),
    path('orders/<uuid:order_id>/invoice/', orders.generate_invoice, name='generate_invoice'),
    path('orders/bulk-update/', orders.bulk_update_status, name='bulk_update_status'),
    path('refunds/<uuid:refund_id>/', orders.refund_detail, name='refund_detail'),
    path('refunds/<uuid:refund_id>/process/', orders.process_refund, name='process_refund'),

    # Phase 3: Product Management (CRUD)
    path('products/manage/', products.product_list, name='product_list'),
    path('products/create/', products.product_create, name='product_create'),
    path('products/<int:product_id>/detail/', products.product_detail, name='product_detail'),
    path('products/<int:product_id>/update/', products.product_update, name='product_update'),
    path('products/<int:product_id>/delete/', products.product_delete, name='product_delete'),
    path('products/bulk-action/', products.product_bulk_action, name='product_bulk_action'),

    # Phase 3: Products & analytics
    path('products/analytics/', products.product_analytics_list, name='product_analytics_list'),
    path('products/analytics/<int:product_id>/', products.product_analytics_detail, name='product_analytics_detail'),
    path('products/featured/dashboard/', products.featured_products_dashboard, name='featured_products_dashboard'),
    path('products/featured/manage/', products.manage_featured_products, name='manage_featured_products'),
    path('products/featured/auto-suggest/', products.auto_suggest_featured, name='auto_suggest_featured'),

    # Phase 4: Reviews
    path('reviews/', reviews.review_list, name='review_list'),
    path('reviews/pending/', reviews.review_pending, name='review_pending'),
    path('reviews/analytics/', reviews.review_analytics, name='review_analytics'),
    path('reviews/<int:review_id>/', reviews.review_detail, name='review_detail'),
    path('reviews/<int:review_id>/approve/', reviews.approve_review, name='approve_review'),
    path('reviews/<int:review_id>/reject/', reviews.reject_review, name='reject_review'),
    path('reviews/<int:review_id>/delete/', reviews.delete_review, name='delete_review'),
    path('reviews/bulk-approve/', reviews.bulk_approve_reviews, name='bulk_approve_reviews'),
    path('reviews/bulk-reject/', reviews.bulk_reject_reviews, name='bulk_reject_reviews'),
    path('reviews/bulk-delete/', reviews.bulk_delete_reviews, name='bulk_delete_reviews'),

    # Phase 5: Users & Roles
    path('users/', users.user_list, name='user_list'),
    path('users/staff/', users.staff_list, name='staff_list'),
    path('users/create-staff/', users.create_staff_user, name='create_staff_user'),
    path('users/<int:user_id>/', users.user_detail, name='user_detail'),
    path('users/<int:user_id>/assign-role/', users.assign_role, name='assign_role'),
    path('users/<int:user_id>/remove-role/', users.remove_role, name='remove_role'),
    path('users/<int:user_id>/toggle-status/', users.toggle_user_status, name='toggle_user_status'),
    path('activity/', users.activity_log, name='activity_log'),

    # Phase 6: Reports & Analytics
    path('reports/', reports.dashboard_overview, name='reports_dashboard'),
    path('reports/sales/', reports.sales_report, name='sales_report'),
    path('reports/revenue/', reports.revenue_report, name='revenue_report'),
    path('reports/products/', reports.product_performance, name='product_performance'),
    path('reports/export/sales/', reports.export_sales_csv, name='export_sales_csv'),
    path('reports/export/products/', reports.export_products_csv, name='export_products_csv'),
]
