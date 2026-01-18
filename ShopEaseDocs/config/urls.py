"""
URL configuration for ShopEase Documentation project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('code/', include('apps.code_docs.urls', namespace='code_docs')),
    path('help/', include('apps.help_center.urls', namespace='help_center')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
