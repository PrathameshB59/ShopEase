"""
Admin URL Configuration - Dashboard and admin functionality
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.admin_panel.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-currency/', dashboard.set_currency, name='set_currency'),
    path('dashboard/', include('apps.admin_panel.urls', namespace='admin_panel')),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),  # Smart landing page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
