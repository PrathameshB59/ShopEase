"""
URL patterns for code_docs app.

All URLs require superuser authentication.
"""
from django.urls import path
from . import views

app_name = 'code_docs'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('structure/', views.folder_structure, name='folder_structure'),
    path('apps/<slug:app_name>/', views.app_detail, name='app_detail'),
    path('models/', views.models_docs, name='models'),
    path('views/', views.views_docs, name='views'),
    path('templates/', views.templates_docs, name='templates'),
    path('api/', views.api_docs, name='api'),
]
