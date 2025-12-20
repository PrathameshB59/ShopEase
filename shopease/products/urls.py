from django.urls import path
from . import views

app_name = 'products'  # This creates the namespace!

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product-list'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('products/search/', views.search_products, name='product-search'),
]