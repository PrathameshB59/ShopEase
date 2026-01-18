"""
Views for Help Center app.

All views in this module are publicly accessible (no authentication required).
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import HelpCategory, HelpArticle, FAQ


def index(request):
    """Help Center home page."""
    categories = HelpCategory.objects.filter(is_active=True)
    featured_articles = HelpArticle.objects.filter(
        is_published=True,
        is_featured=True
    )[:6]
    recent_articles = HelpArticle.objects.filter(is_published=True)[:5]

    context = {
        'title': 'Help Center',
        'categories': categories,
        'featured_articles': featured_articles,
        'recent_articles': recent_articles,
    }
    return render(request, 'help_center/index.html', context)


def category_detail(request, slug):
    """Display articles in a category."""
    category = get_object_or_404(HelpCategory, slug=slug, is_active=True)
    articles = category.articles.filter(is_published=True)

    context = {
        'title': category.name,
        'category': category,
        'articles': articles,
    }
    return render(request, 'help_center/category_detail.html', context)


def article_detail(request, slug):
    """Display a single help article."""
    article = get_object_or_404(HelpArticle, slug=slug, is_published=True)

    # Increment view count
    article.increment_views()

    # Get related articles from the same category
    related_articles = HelpArticle.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(pk=article.pk)[:4]

    context = {
        'title': article.title,
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'help_center/article_detail.html', context)


def faq_list(request):
    """Display all FAQs."""
    faqs = FAQ.objects.filter(is_active=True)
    categories = HelpCategory.objects.filter(
        is_active=True,
        faqs__is_active=True
    ).distinct()

    context = {
        'title': 'Frequently Asked Questions',
        'faqs': faqs,
        'categories': categories,
    }
    return render(request, 'help_center/faq_list.html', context)


def search(request):
    """Search help articles and FAQs."""
    query = request.GET.get('q', '').strip()
    articles = []
    faqs = []

    if query:
        articles = HelpArticle.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_published=True
        )
        faqs = FAQ.objects.filter(
            Q(question__icontains=query) | Q(answer__icontains=query),
            is_active=True
        )

    context = {
        'title': f'Search Results for "{query}"' if query else 'Search Help',
        'query': query,
        'articles': articles,
        'faqs': faqs,
    }
    return render(request, 'help_center/search.html', context)
