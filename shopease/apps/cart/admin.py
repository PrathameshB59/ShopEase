"""
Cart Admin - Simple Registration
"""
from django.contrib import admin
from .models import Cart, CartItem

# Simple registration - basic admin interface
admin.site.register(Cart)
admin.site.register(CartItem)