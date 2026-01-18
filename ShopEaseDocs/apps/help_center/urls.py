"""
URL patterns for help_center app.

All URLs are publicly accessible.
"""
from django.urls import path
from . import views

app_name = 'help_center'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('faq/', views.faq_list, name='faq_list'),
    path('search/', views.search, name='search'),
]
