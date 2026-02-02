"""
Customer URL Configuration - Customer-facing storefront
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.admin_panel.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-currency/', dashboard.set_currency, name='set_currency'),
    path('products/', include('apps.products.urls', namespace='products')),
    path('', include('apps.core.urls')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
