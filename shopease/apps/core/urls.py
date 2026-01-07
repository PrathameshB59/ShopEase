from django.urls import path
from django.views.generic import TemplateView

# app_name = 'core'  # Add this line

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]