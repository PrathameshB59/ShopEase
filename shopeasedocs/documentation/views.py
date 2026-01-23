from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction

from .models import (
    DocCategory, Documentation, CodeExplanation, FAQ,
    DeveloperDiscussion, DeveloperMessage, AppVersion, DailyIssueHelp,
    HelpScreenshot, CodeLearningProgress
)
from .forms import (
    DocCategoryForm, DocumentationForm, CodeExplanationForm, FAQForm,
    DeveloperDiscussionForm, DeveloperMessageForm, AppVersionForm,
    DailyIssueHelpForm, SearchForm
)


# ====================================
# PERMISSION DECORATORS
# ====================================

def admin_permission_required(permission_name):
    """
    Decorator to check if user has specific admin permission
    Works with ShopEase AdminRole model
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('login')

            # Superusers have all permissions
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check AdminRole permission
            if hasattr(request.user, 'admin_role'):
                if getattr(request.user.admin_role, permission_name, False):
                    return view_func(request, *args, **kwargs)

            messages.error(request, 'You do not have permission to access this page.')
            return HttpResponseForbidden('Permission denied')
        return wrapper
    return decorator


def superuser_required(view_func):
    """Decorator to restrict access to superusers only"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')

        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superuser privileges required.')
            return redirect('documentation:doc_home')

        return view_func(request, *args, **kwargs)
    return wrapper


# ====================================
# PUBLIC DOCUMENTATION VIEWS
# ====================================

def doc_home(request):
    """Documentation homepage with categories and featured docs"""
    categories = DocCategory.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('subcategories').order_by('order', 'name')

    # Get featured documentation
    featured_docs = Documentation.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category', 'author').order_by('-created_at')[:6]

    # Get recent documentation (audience-aware)
    recent_docs_query = Documentation.objects.filter(is_published=True)

    # Filter by audience
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass  # Show all
        elif hasattr(request.user, 'admin_role'):
            recent_docs_query = recent_docs_query.filter(
                Q(audience='ALL') | Q(audience='ADMIN') | Q(audience='SUPERUSER')
            )
        else:
            recent_docs_query = recent_docs_query.filter(
                Q(audience='ALL') | Q(audience='CUSTOMER')
            )
    else:
        recent_docs_query = recent_docs_query.filter(audience='ALL')

    recent_docs = recent_docs_query.select_related('category', 'author').order_by('-created_at')[:8]

    # Popular FAQs
    popular_faqs = FAQ.objects.filter(
        status='published'
    ).order_by('-view_count')[:5]

    context = {
        'categories': categories,
        'featured_docs': featured_docs,
        'recent_docs': recent_docs,
        'popular_faqs': popular_faqs,
    }
    return render(request, 'documentation/public/doc_home.html', context)


def doc_detail(request, slug):
    """Individual documentation page"""
    doc = get_object_or_404(Documentation, slug=slug, is_published=True)

    # Check audience permissions
    if doc.audience == 'SUPERUSER' and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this documentation.')
        return redirect('documentation:doc_home')

    if doc.audience == 'ADMIN':
        if not request.user.is_authenticated or (
            not request.user.is_superuser and not hasattr(request.user, 'admin_role')
        ):
            messages.error(request, 'This documentation is for admin users only.')
            return redirect('documentation:doc_home')

    # Increment view count
    Documentation.objects.filter(pk=doc.pk).update(views_count=F('views_count') + 1)
    doc.refresh_from_db()

    # Get related docs from same category
    related_docs = Documentation.objects.filter(
        category=doc.category,
        is_published=True
    ).exclude(pk=doc.pk).order_by('-created_at')[:4]

    context = {
        'doc': doc,
        'related_docs': related_docs,
    }
    return render(request, 'documentation/public/doc_detail.html', context)


def category_docs(request, category_slug):
    """List all documentation in a category"""
    category = get_object_or_404(DocCategory, slug=category_slug, is_active=True)

    docs_query = Documentation.objects.filter(
        category=category,
        is_published=True
    )

    # Audience filtering
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass
        elif hasattr(request.user, 'admin_role'):
            docs_query = docs_query.filter(Q(audience='ALL') | Q(audience='ADMIN'))
        else:
            docs_query = docs_query.filter(Q(audience='ALL') | Q(audience='CUSTOMER'))
    else:
        docs_query = docs_query.filter(audience='ALL')

    docs = docs_query.select_related('author').order_by('-created_at')

    # Pagination
    paginator = Paginator(docs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'documentation/public/category_docs.html', context)


def faq_list(request):
    """FAQ listing by category"""
    categories = DocCategory.objects.filter(is_active=True).prefetch_related(
        'faqs'
    ).order_by('order', 'name')

    # Filter FAQs by audience
    faqs_query = FAQ.objects.filter(status='published')

    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass
        elif hasattr(request.user, 'admin_role'):
            faqs_query = faqs_query.filter(Q(audience='ALL') | Q(audience='ADMIN'))
        else:
            faqs_query = faqs_query.filter(Q(audience='ALL') | Q(audience='CUSTOMER'))
    else:
        faqs_query = faqs_query.filter(audience='ALL')

    faqs = faqs_query.select_related('category').order_by('category', 'order')

    context = {
        'categories': categories,
        'faqs': faqs,
    }
    return render(request, 'documentation/public/faq_list.html', context)


def faq_by_category(request, category_slug):
    """FAQs filtered by specific category"""
    category = get_object_or_404(DocCategory, slug=category_slug, is_active=True)

    faqs = FAQ.objects.filter(
        category=category,
        status='published'
    ).order_by('order')

    context = {
        'category': category,
        'faqs': faqs,
    }
    return render(request, 'documentation/public/faq_category.html', context)


def help_center(request):
    """Help center with daily issue help articles"""
    issue_type = request.GET.get('type', '')

    help_query = DailyIssueHelp.objects.filter(status='published')

    if issue_type:
        help_query = help_query.filter(issue_type=issue_type)

    # Audience filtering
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass
        elif hasattr(request.user, 'admin_role'):
            help_query = help_query.filter(Q(audience='ALL') | Q(audience='ADMIN'))
        else:
            help_query = help_query.filter(Q(audience='ALL') | Q(audience='CUSTOMER'))
    else:
        help_query = help_query.filter(audience='ALL')

    help_articles = help_query.order_by('-created_at')

    # Pagination
    paginator = Paginator(help_articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'issue_types': DailyIssueHelp.ISSUE_TYPE,
        'selected_type': issue_type,
    }
    return render(request, 'documentation/public/help_center.html', context)


def help_detail(request, help_id):
    """Individual help article detail"""
    help_article = get_object_or_404(DailyIssueHelp, pk=help_id, status='published')

    # Check audience
    if help_article.audience == 'ADMIN' and not (
        request.user.is_authenticated and (
            request.user.is_superuser or hasattr(request.user, 'admin_role')
        )
    ):
        messages.error(request, 'This help article is for admin users only.')
        return redirect('documentation:help_center')

    # Increment view count
    DailyIssueHelp.objects.filter(pk=help_article.pk).update(views_count=F('views_count') + 1)
    help_article.refresh_from_db()

    # Related articles
    related_articles = DailyIssueHelp.objects.filter(
        issue_type=help_article.issue_type,
        status='published'
    ).exclude(pk=help_article.pk).order_by('-views_count')[:4]

    context = {
        'help_article': help_article,
        'related_articles': related_articles,
    }
    return render(request, 'documentation/public/help_detail.html', context)


def doc_search(request):
    """Search documentation, FAQs, and help articles"""
    form = SearchForm(request.GET)
    results = []
    query = ''

    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        category = form.cleaned_data.get('category')
        audience = form.cleaned_data.get('audience')

        if query:
            # Search Documentation
            docs_query = Documentation.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(keywords__icontains=query),
                is_published=True
            )

            if category:
                docs_query = docs_query.filter(category=category)

            if audience:
                docs_query = docs_query.filter(audience=audience)

            # Audience filtering
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    pass
                elif hasattr(request.user, 'admin_role'):
                    docs_query = docs_query.filter(Q(audience='ALL') | Q(audience='ADMIN'))
                else:
                    docs_query = docs_query.filter(Q(audience='ALL') | Q(audience='CUSTOMER'))
            else:
                docs_query = docs_query.filter(audience='ALL')

            docs = docs_query.select_related('category', 'author')

            # Search FAQs
            faqs = FAQ.objects.filter(
                Q(question__icontains=query) | Q(answer__icontains=query),
                status='published'
            ).select_related('category')

            # Search Help Articles
            help_articles = DailyIssueHelp.objects.filter(
                Q(title__icontains=query) |
                Q(problem_description__icontains=query) |
                Q(solution_steps__icontains=query),
                status='published'
            )

            results = {
                'docs': docs,
                'faqs': faqs,
                'help_articles': help_articles,
            }

    context = {
        'form': form,
        'results': results,
        'query': query,
    }
    return render(request, 'documentation/public/search_results.html', context)


def version_list(request):
    """List all app versions"""
    versions = AppVersion.objects.all().select_related('created_by').order_by('-release_date')

    context = {
        'versions': versions,
    }
    return render(request, 'documentation/public/version_list.html', context)


def version_detail(request, version_number):
    """Detailed version information and release notes"""
    version = get_object_or_404(AppVersion, version_number=version_number)

    context = {
        'version': version,
    }
    return render(request, 'documentation/public/version_detail.html', context)


@require_POST
def mark_helpful(request):
    """AJAX endpoint to mark content as helpful/not helpful"""
    model_type = request.POST.get('model_type')
    object_id = request.POST.get('object_id')
    is_helpful = request.POST.get('is_helpful') == 'true'

    model_map = {
        'documentation': Documentation,
        'faq': FAQ,
        'help': DailyIssueHelp,
    }

    if model_type not in model_map:
        return JsonResponse({'success': False, 'error': 'Invalid model type'})

    try:
        obj = model_map[model_type].objects.get(pk=object_id)

        if is_helpful:
            obj.helpful_count += 1
        else:
            obj.not_helpful_count += 1

        obj.save()

        return JsonResponse({
            'success': True,
            'helpful_count': obj.helpful_count,
            'not_helpful_count': obj.not_helpful_count,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ====================================
# ADMIN MANAGEMENT VIEWS
# ====================================

@login_required
@admin_permission_required('can_view_documentation')
def doc_admin_dashboard(request):
    """Admin dashboard with documentation statistics"""
    stats = {
        'total_docs': Documentation.objects.count(),
        'published_docs': Documentation.objects.filter(is_published=True).count(),
        'draft_docs': Documentation.objects.filter(is_published=False).count(),
        'total_faqs': FAQ.objects.filter(status='published').count(),
        'total_help': DailyIssueHelp.objects.filter(status='published').count(),
        'total_views': Documentation.objects.aggregate(total=Count('views_count'))['total'] or 0,
    }

    # Recent activity
    recent_docs = Documentation.objects.select_related('category', 'author').order_by('-created_at')[:5]
    most_viewed = Documentation.objects.filter(is_published=True).order_by('-views_count')[:5]
    most_helpful = Documentation.objects.filter(is_published=True).order_by('-helpful_count')[:5]

    context = {
        'stats': stats,
        'recent_docs': recent_docs,
        'most_viewed': most_viewed,
        'most_helpful': most_helpful,
    }
    return render(request, 'documentation/admin/dashboard.html', context)


@login_required
@admin_permission_required('can_view_documentation')
def manage_docs(request):
    """Manage all documentation articles"""
    docs_query = Documentation.objects.select_related('category', 'author').order_by('-created_at')

    # Filters
    category_id = request.GET.get('category')
    audience = request.GET.get('audience')
    status = request.GET.get('status')

    if category_id:
        docs_query = docs_query.filter(category_id=category_id)
    if audience:
        docs_query = docs_query.filter(audience=audience)
    if status == 'published':
        docs_query = docs_query.filter(is_published=True)
    elif status == 'draft':
        docs_query = docs_query.filter(is_published=False)

    # Pagination
    paginator = Paginator(docs_query, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = DocCategory.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'documentation/admin/manage_docs.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def create_doc(request):
    """Create new documentation"""
    if request.method == 'POST':
        form = DocumentationForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.author = request.user
            if doc.is_published and not doc.published_at:
                doc.published_at = timezone.now()
            doc.save()
            messages.success(request, f'Documentation "{doc.title}" created successfully.')
            return redirect('documentation:manage_docs')
    else:
        form = DocumentationForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/admin/doc_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def edit_doc(request, doc_id):
    """Edit existing documentation"""
    doc = get_object_or_404(Documentation, pk=doc_id)

    if request.method == 'POST':
        form = DocumentationForm(request.POST, instance=doc)
        if form.is_valid():
            doc = form.save(commit=False)
            if doc.is_published and not doc.published_at:
                doc.published_at = timezone.now()
            doc.save()
            messages.success(request, f'Documentation "{doc.title}" updated successfully.')
            return redirect('documentation:manage_docs')
    else:
        form = DocumentationForm(instance=doc)

    context = {
        'form': form,
        'action': 'Edit',
        'doc': doc,
    }
    return render(request, 'documentation/admin/doc_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
@require_POST
def delete_doc(request, doc_id):
    """Delete documentation"""
    doc = get_object_or_404(Documentation, pk=doc_id)
    title = doc.title
    doc.delete()
    messages.success(request, f'Documentation "{title}" deleted successfully.')
    return redirect('documentation:manage_docs')


@login_required
@admin_permission_required('can_edit_documentation')
@require_POST
def publish_doc(request, doc_id):
    """Toggle publish status of documentation"""
    doc = get_object_or_404(Documentation, pk=doc_id)
    doc.is_published = not doc.is_published
    if doc.is_published and not doc.published_at:
        doc.published_at = timezone.now()
    doc.save()

    status = 'published' if doc.is_published else 'unpublished'
    messages.success(request, f'Documentation "{doc.title}" {status} successfully.')
    return redirect('documentation:manage_docs')


# Category Management Views
@login_required
@admin_permission_required('can_edit_documentation')
def manage_categories(request):
    """Manage documentation categories"""
    categories = DocCategory.objects.all().order_by('order', 'name')

    context = {
        'categories': categories,
    }
    return render(request, 'documentation/admin/manage_categories.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def create_category(request):
    """Create new category"""
    if request.method == 'POST':
        form = DocCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('documentation:manage_categories')
    else:
        form = DocCategoryForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/admin/category_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def edit_category(request, cat_id):
    """Edit existing category"""
    category = get_object_or_404(DocCategory, pk=cat_id)

    if request.method == 'POST':
        form = DocCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('documentation:manage_categories')
    else:
        form = DocCategoryForm(instance=category)

    context = {
        'form': form,
        'action': 'Edit',
        'category': category,
    }
    return render(request, 'documentation/admin/category_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
@require_POST
def delete_category(request, cat_id):
    """Delete category"""
    category = get_object_or_404(DocCategory, pk=cat_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted successfully.')
    return redirect('documentation:manage_categories')


# FAQ Management Views
@login_required
@admin_permission_required('can_manage_faqs')
def manage_faqs(request):
    """Manage FAQs"""
    faqs = FAQ.objects.select_related('category').order_by('category', 'order')

    context = {
        'faqs': faqs,
    }
    return render(request, 'documentation/admin/manage_faqs.html', context)


@login_required
@admin_permission_required('can_manage_faqs')
def create_faq(request):
    """Create new FAQ"""
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            messages.success(request, 'FAQ created successfully.')
            return redirect('documentation:manage_faqs')
    else:
        form = FAQForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/admin/faq_form.html', context)


@login_required
@admin_permission_required('can_manage_faqs')
def edit_faq(request, faq_id):
    """Edit existing FAQ"""
    faq = get_object_or_404(FAQ, pk=faq_id)

    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            faq = form.save()
            messages.success(request, 'FAQ updated successfully.')
            return redirect('documentation:manage_faqs')
    else:
        form = FAQForm(instance=faq)

    context = {
        'form': form,
        'action': 'Edit',
        'faq': faq,
    }
    return render(request, 'documentation/admin/faq_form.html', context)


@login_required
@admin_permission_required('can_manage_faqs')
@require_POST
def delete_faq(request, faq_id):
    """Delete FAQ"""
    faq = get_object_or_404(FAQ, pk=faq_id)
    faq.delete()
    messages.success(request, 'FAQ deleted successfully.')
    return redirect('documentation:manage_faqs')


# Help Issue Management Views
@login_required
@admin_permission_required('can_edit_documentation')
def manage_help_issues(request):
    """Manage daily issue help articles"""
    help_articles = DailyIssueHelp.objects.all().order_by('-created_at')

    context = {
        'help_articles': help_articles,
    }
    return render(request, 'documentation/admin/manage_help.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def create_help_issue(request):
    """Create new help issue"""
    if request.method == 'POST':
        form = DailyIssueHelpForm(request.POST, request.FILES)
        if form.is_valid():
            help_article = form.save()
            messages.success(request, 'Help article created successfully.')
            return redirect('documentation:manage_help_issues')
    else:
        form = DailyIssueHelpForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/admin/help_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
def edit_help_issue(request, help_id):
    """Edit existing help issue"""
    help_article = get_object_or_404(DailyIssueHelp, pk=help_id)

    if request.method == 'POST':
        form = DailyIssueHelpForm(request.POST, request.FILES, instance=help_article)
        if form.is_valid():
            help_article = form.save()
            messages.success(request, 'Help article updated successfully.')
            return redirect('documentation:manage_help_issues')
    else:
        form = DailyIssueHelpForm(instance=help_article)

    context = {
        'form': form,
        'action': 'Edit',
        'help_article': help_article,
    }
    return render(request, 'documentation/admin/help_form.html', context)


@login_required
@admin_permission_required('can_edit_documentation')
@require_POST
def delete_help_issue(request, help_id):
    """Delete help issue"""
    help_article = get_object_or_404(DailyIssueHelp, pk=help_id)
    help_article.delete()
    messages.success(request, 'Help article deleted successfully.')
    return redirect('documentation:manage_help_issues')


# Version Management Views
@login_required
@admin_permission_required('can_manage_versions')
def manage_versions(request):
    """Manage app versions"""
    versions = AppVersion.objects.select_related('created_by').order_by('-release_date')

    context = {
        'versions': versions,
    }
    return render(request, 'documentation/admin/manage_versions.html', context)


@login_required
@admin_permission_required('can_manage_versions')
def create_version(request):
    """Create new version"""
    if request.method == 'POST':
        form = AppVersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.created_by = request.user
            version.save()
            messages.success(request, f'Version {version.version_number} created successfully.')
            return redirect('documentation:manage_versions')
    else:
        form = AppVersionForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/admin/version_form.html', context)


@login_required
@admin_permission_required('can_manage_versions')
def edit_version(request, version_id):
    """Edit existing version"""
    version = get_object_or_404(AppVersion, pk=version_id)

    if request.method == 'POST':
        form = AppVersionForm(request.POST, instance=version)
        if form.is_valid():
            version = form.save()
            messages.success(request, f'Version {version.version_number} updated successfully.')
            return redirect('documentation:manage_versions')
    else:
        form = AppVersionForm(instance=version)

    context = {
        'form': form,
        'action': 'Edit',
        'version': version,
    }
    return render(request, 'documentation/admin/version_form.html', context)


@login_required
@admin_permission_required('can_manage_versions')
@require_POST
def delete_version(request, version_id):
    """Delete version"""
    version = get_object_or_404(AppVersion, pk=version_id)
    version_number = version.version_number
    version.delete()
    messages.success(request, f'Version {version_number} deleted successfully.')
    return redirect('documentation:manage_versions')


@login_required
@admin_permission_required('can_manage_versions')
@require_POST
def set_current_version(request, version_id):
    """Set a version as current"""
    version = get_object_or_404(AppVersion, pk=version_id)

    # Unmark all other versions
    AppVersion.objects.filter(is_current=True).update(is_current=False)

    # Mark this version as current
    version.is_current = True
    version.save()

    messages.success(request, f'Version {version.version_number} set as current.')
    return redirect('documentation:manage_versions')


# ====================================
# CODE EXPLANATION VIEWS (SUPERUSER-ONLY)
# ====================================

@superuser_required
def code_index(request):
    """List all code explanations grouped by module"""
    module_filter = request.GET.get('module', '')
    complexity_filter = request.GET.get('complexity', '')

    code_query = CodeExplanation.objects.select_related('author')

    if module_filter:
        code_query = code_query.filter(module=module_filter)
    if complexity_filter:
        code_query = code_query.filter(complexity=complexity_filter)

    code_explanations = code_query.order_by('module', '-created_at')

    # Group by module
    modules_dict = {}
    for code in code_explanations:
        if code.module not in modules_dict:
            modules_dict[code.module] = []
        modules_dict[code.module].append(code)

    context = {
        'modules_dict': modules_dict,
        'module_choices': CodeExplanation.MODULE_CHOICES,
        'complexity_choices': CodeExplanation.COMPLEXITY_CHOICES,
        'selected_module': module_filter,
        'selected_complexity': complexity_filter,
    }
    return render(request, 'documentation/code/code_index.html', context)


@superuser_required
def code_detail(request, slug):
    """Detailed code explanation with syntax highlighting"""
    code = get_object_or_404(CodeExplanation, slug=slug)

    # Increment view count
    CodeExplanation.objects.filter(pk=code.pk).update(views_count=F('views_count') + 1)
    code.refresh_from_db()

    # Related code explanations from same module
    related_code = CodeExplanation.objects.filter(
        module=code.module
    ).exclude(pk=code.pk).order_by('-created_at')[:4]

    context = {
        'code': code,
        'related_code': related_code,
    }
    return render(request, 'documentation/code/code_detail.html', context)


@superuser_required
def code_by_module(request, module):
    """Filter code explanations by module"""
    code_explanations = CodeExplanation.objects.filter(
        module=module
    ).select_related('author').order_by('-created_at')

    context = {
        'code_explanations': code_explanations,
        'module': module,
        'module_display': dict(CodeExplanation.MODULE_CHOICES).get(module, module),
    }
    return render(request, 'documentation/code/code_by_module.html', context)


@superuser_required
def create_code_explanation(request):
    """Create new code explanation"""
    if request.method == 'POST':
        form = CodeExplanationForm(request.POST)
        if form.is_valid():
            code = form.save(commit=False)
            code.author = request.user
            code.save()
            form.save_m2m()  # Save related_docs many-to-many
            messages.success(request, f'Code explanation "{code.title}" created successfully.')
            return redirect('documentation:code_index')
    else:
        form = CodeExplanationForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'documentation/code/code_form.html', context)


@superuser_required
def edit_code_explanation(request, code_id):
    """Edit existing code explanation"""
    code = get_object_or_404(CodeExplanation, pk=code_id)

    if request.method == 'POST':
        form = CodeExplanationForm(request.POST, instance=code)
        if form.is_valid():
            code = form.save()
            messages.success(request, f'Code explanation "{code.title}" updated successfully.')
            return redirect('documentation:code_index')
    else:
        form = CodeExplanationForm(instance=code)

    context = {
        'form': form,
        'action': 'Edit',
        'code': code,
    }
    return render(request, 'documentation/code/code_form.html', context)


@superuser_required
@require_POST
def delete_code_explanation(request, code_id):
    """Delete code explanation"""
    code = get_object_or_404(CodeExplanation, pk=code_id)
    title = code.title
    code.delete()
    messages.success(request, f'Code explanation "{title}" deleted successfully.')
    return redirect('documentation:code_index')


# ====================================
# DEVELOPER CHAT VIEWS
# ====================================

@login_required
@admin_permission_required('can_participate_dev_chat')
def dev_chat_list(request):
    """List all developer discussion threads"""
    status_filter = request.GET.get('status', 'OPEN')

    threads_query = DeveloperDiscussion.objects.select_related('created_by').annotate(
        message_count_db=Count('messages')
    )

    if status_filter:
        threads_query = threads_query.filter(status=status_filter)

    threads = threads_query.order_by('-last_message_at')

    # Pagination
    paginator = Paginator(threads, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': DeveloperDiscussion.THREAD_STATUS,
        'selected_status': status_filter,
    }
    return render(request, 'documentation/dev_chat/chat_list.html', context)


@login_required
@admin_permission_required('can_participate_dev_chat')
def create_thread(request):
    """Create new discussion thread"""
    if request.method == 'POST':
        form = DeveloperDiscussionForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.created_by = request.user
            thread.save()
            messages.success(request, f'Discussion thread "{thread.title}" created successfully.')
            return redirect('documentation:thread_detail', thread_id=thread.id)
    else:
        form = DeveloperDiscussionForm()

    context = {
        'form': form,
    }
    return render(request, 'documentation/dev_chat/create_thread.html', context)


@login_required
@admin_permission_required('can_participate_dev_chat')
def thread_detail(request, thread_id):
    """View discussion thread with messages"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)

    # Get all messages
    messages_list = thread.messages.select_related('author').order_by('created_at')

    # For AJAX polling (JSON response)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        since_timestamp = request.GET.get('since')

        if since_timestamp:
            from datetime import datetime
            since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
            new_messages = messages_list.filter(created_at__gt=since_dt)
        else:
            new_messages = messages_list

        messages_data = [{
            'id': msg.id,
            'author': msg.author.username,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_edited': msg.is_edited,
            'attachment_url': msg.attachment.url if msg.attachment else None,
        } for msg in new_messages]

        return JsonResponse({
            'messages': messages_data,
            'thread_status': thread.status,
        })

    # Regular page view
    message_form = DeveloperMessageForm()

    context = {
        'thread': thread,
        'messages': messages_list,
        'message_form': message_form,
    }
    return render(request, 'documentation/dev_chat/thread_detail.html', context)


@login_required
@admin_permission_required('can_participate_dev_chat')
def edit_thread(request, thread_id):
    """Edit discussion thread"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)

    # Only creator or superuser can edit
    if thread.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'You can only edit threads you created.')
        return redirect('documentation:thread_detail', thread_id=thread.id)

    if request.method == 'POST':
        form = DeveloperDiscussionForm(request.POST, instance=thread)
        if form.is_valid():
            thread = form.save()
            messages.success(request, f'Thread "{thread.title}" updated successfully.')
            return redirect('documentation:thread_detail', thread_id=thread.id)
    else:
        form = DeveloperDiscussionForm(instance=thread)

    context = {
        'form': form,
        'thread': thread,
    }
    return render(request, 'documentation/dev_chat/edit_thread.html', context)


@login_required
@admin_permission_required('can_participate_dev_chat')
@require_POST
def resolve_thread(request, thread_id):
    """Mark thread as resolved"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)
    thread.status = 'RESOLVED'
    thread.save()
    messages.success(request, f'Thread "{thread.title}" marked as resolved.')
    return redirect('documentation:thread_detail', thread_id=thread.id)


@login_required
@admin_permission_required('can_participate_dev_chat')
@require_POST
def archive_thread(request, thread_id):
    """Archive thread"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)
    thread.status = 'ARCHIVED'
    thread.save()
    messages.success(request, f'Thread "{thread.title}" archived.')
    return redirect('documentation:dev_chat_list')


@login_required
@admin_permission_required('can_participate_dev_chat')
def get_messages(request, thread_id):
    """AJAX endpoint to fetch new messages"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)

    since_timestamp = request.GET.get('since')
    messages_query = thread.messages.select_related('author').order_by('created_at')

    if since_timestamp:
        from datetime import datetime
        since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
        messages_query = messages_query.filter(created_at__gt=since_dt)

    messages_data = [{
        'id': msg.id,
        'author': msg.author.username,
        'author_id': msg.author.id,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'is_edited': msg.is_edited,
        'attachment_url': msg.attachment.url if msg.attachment else None,
    } for msg in messages_query]

    return JsonResponse({
        'messages': messages_data,
        'thread_status': thread.status,
    })


@login_required
@admin_permission_required('can_participate_dev_chat')
@require_POST
def post_message(request, thread_id):
    """AJAX endpoint to post new message"""
    thread = get_object_or_404(DeveloperDiscussion, pk=thread_id)

    form = DeveloperMessageForm(request.POST, request.FILES)
    if form.is_valid():
        message = form.save(commit=False)
        message.thread = thread
        message.author = request.user
        message.save()

        # Update thread's last_message_at
        thread.last_message_at = timezone.now()
        thread.save()

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'author': message.author.username,
                'author_id': message.author.id,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'is_edited': message.is_edited,
                'attachment_url': message.attachment.url if message.attachment else None,
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


@login_required
@admin_permission_required('can_participate_dev_chat')
@require_POST
def edit_message(request, message_id):
    """Edit a chat message"""
    message = get_object_or_404(DeveloperMessage, pk=message_id)

    # Only message author can edit
    if message.author != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You can only edit your own messages.'
        }, status=403)

    content = request.POST.get('content')
    if content:
        message.content = content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'is_edited': message.is_edited,
                'edited_at': message.edited_at.isoformat() if message.edited_at else None,
            }
        })

    return JsonResponse({
        'success': False,
        'error': 'Content is required.'
    }, status=400)


@login_required
@admin_permission_required('can_participate_dev_chat')
@require_POST
def delete_message(request, message_id):
    """Delete a chat message"""
    message = get_object_or_404(DeveloperMessage, pk=message_id)

    # Only message author or superuser can delete
    if message.author != request.user and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'You can only delete your own messages.'
        }, status=403)

    message.delete()

    return JsonResponse({
        'success': True,
        'message_id': message_id
    })
