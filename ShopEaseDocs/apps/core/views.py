"""
Core views for ShopEase Documentation.
"""
from django.shortcuts import render


def home(request):
    """Documentation home page."""
    context = {
        'title': 'ShopEase Documentation',
    }
    return render(request, 'core/home.html', context)


def search(request):
    """Global search across documentation."""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Search in help articles if available
        try:
            from apps.help_center.models import HelpArticle
            help_results = HelpArticle.objects.filter(
                title__icontains=query,
                is_published=True
            )[:10]
            results.extend([
                {'title': a.title, 'url': f'/help/article/{a.slug}/', 'type': 'Help Article'}
                for a in help_results
            ])
        except Exception:
            pass

    context = {
        'title': f'Search Results for "{query}"' if query else 'Search',
        'query': query,
        'results': results,
    }
    return render(request, 'core/search_results.html', context)
