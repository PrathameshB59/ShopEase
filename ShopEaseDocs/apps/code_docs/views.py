"""
Code Documentation views for ShopEase Documentation.

All views in this module require superuser privileges.
"""
from django.shortcuts import render
from apps.accounts.decorators import superadmin_required


@superadmin_required
def overview(request):
    """Code documentation overview page."""
    context = {
        'title': 'Code Documentation Overview',
    }
    return render(request, 'code_docs/overview.html', context)


@superadmin_required
def folder_structure(request):
    """ShopEase folder structure documentation."""
    context = {
        'title': 'Folder Structure',
    }
    return render(request, 'code_docs/folder_structure.html', context)


@superadmin_required
def app_detail(request, app_name):
    """Detailed documentation for a specific app."""
    # Map of valid app names to their display names
    apps_info = {
        'core': 'Core App',
        'products': 'Products App',
        'accounts': 'Accounts App',
        'cart': 'Cart App',
        'orders': 'Orders App',
        'admin_panel': 'Admin Panel App',
    }

    if app_name not in apps_info:
        app_name = 'core'

    context = {
        'title': f'{apps_info.get(app_name, app_name)} Documentation',
        'app_name': app_name,
        'app_display_name': apps_info.get(app_name, app_name),
    }
    return render(request, f'code_docs/apps/{app_name}.html', context)


@superadmin_required
def models_docs(request):
    """Models documentation."""
    context = {
        'title': 'Models Documentation',
    }
    return render(request, 'code_docs/models.html', context)


@superadmin_required
def views_docs(request):
    """Views documentation."""
    context = {
        'title': 'Views Documentation',
    }
    return render(request, 'code_docs/views.html', context)


@superadmin_required
def templates_docs(request):
    """Templates documentation."""
    context = {
        'title': 'Templates Documentation',
    }
    return render(request, 'code_docs/templates.html', context)


@superadmin_required
def api_docs(request):
    """API documentation."""
    context = {
        'title': 'API Documentation',
    }
    return render(request, 'code_docs/api.html', context)
