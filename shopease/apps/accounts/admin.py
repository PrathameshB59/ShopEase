"""
========================================
ACCOUNTS ADMIN
========================================
Admin interface for user profiles.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    Inline profile editor on User admin page.
    
    Allows editing profile directly from user page.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('phone',)
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address_line1',
                'shipping_address_line2',
                'shipping_city',
                'shipping_state',
                'shipping_postal_code',
                'shipping_country'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_same_as_shipping',
                'billing_address_line1',
                'billing_address_line2',
                'billing_city',
                'billing_state',
                'billing_postal_code',
                'billing_country'
            )
        }),
        ('Profile', {
            'fields': ('avatar', 'newsletter_subscribed')
        })
    )


# Extend User admin to include Profile
class UserAdmin(BaseUserAdmin):
    """Extended User admin with Profile inline."""
    inlines = (ProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Standalone profile admin.
    
    For viewing/editing profiles directly.
    """
    
    list_display = [
        'user',
        'phone',
        'shipping_city',
        'newsletter_subscribed',
        'created_at'
    ]
    
    list_filter = [
        'newsletter_subscribed',
        'created_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'phone',
        'shipping_city'
    ]
    
    readonly_fields = ['created_at', 'updated_at']