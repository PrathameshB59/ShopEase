"""
========================================
REVIEW MODERATION VIEWS
========================================

Views for managing and moderating product reviews.

Includes:
- Review moderation queue (all reviews, pending only)
- Approve/reject individual reviews
- Bulk approval/rejection actions
- Review analytics and statistics
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta

from apps.admin_panel.decorators import admin_required, permission_required
from apps.products.models import Review, Product


@permission_required('can_moderate_reviews')
def review_list(request):
    """
    Display all reviews with filtering and moderation actions.

    Filters:
    - Approval status (all, pending, approved, rejected)
    - Rating (1-5 stars)
    - Search by product name or user
    - Date range
    """
    # Base queryset with related data
    reviews = Review.objects.select_related(
        'product', 'user'
    ).order_by('-created_at')

    # Approval status filter
    status = request.GET.get('status', 'all')
    if status == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif status == 'approved':
        reviews = reviews.filter(is_approved=True)

    # Rating filter
    rating = request.GET.get('rating', '')
    if rating and rating.isdigit():
        reviews = reviews.filter(rating=int(rating))

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(comment__icontains=search_query)
        )

    # Date filter
    days = request.GET.get('days', '')
    if days and days.isdigit():
        start_date = timezone.now() - timedelta(days=int(days))
        reviews = reviews.filter(created_at__gte=start_date)

    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_reviews = Review.objects.count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    approved_reviews = Review.objects.filter(is_approved=True).count()
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'page_obj': page_obj,
        'status': status,
        'rating': rating,
        'search_query': search_query,
        'days': days,
        'stats': {
            'total': total_reviews,
            'pending': pending_reviews,
            'approved': approved_reviews,
            'avg_rating': round(avg_rating, 2)
        }
    }

    return render(request, 'admin_panel/reviews/list.html', context)


@permission_required('can_moderate_reviews')
def review_pending(request):
    """
    Display only pending (unapproved) reviews for quick moderation.

    Optimized view for reviewing queue.
    """
    # Only pending reviews
    reviews = Review.objects.filter(
        is_approved=False
    ).select_related('product', 'user').order_by('-created_at')

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(title__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'pending_count': reviews.count()
    }

    return render(request, 'admin_panel/reviews/pending.html', context)


@permission_required('can_moderate_reviews')
def approve_review(request, review_id):
    """
    Approve a single review.

    Makes the review visible to customers.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review = get_object_or_404(Review, id=review_id)

    if not review.is_approved:
        review.is_approved = True
        review.save(update_fields=['is_approved', 'updated_at'])

        # Log admin activity
        from apps.admin_panel.models import AdminActivity
        AdminActivity.log_action(
            user=request.user,
            action='REVIEW_APPROVED',
            description=f'Approved review #{review.id} for {review.product.name}',
            related_object_id=str(review.id)
        )

        messages.success(request, f'Review for "{review.product.name}" has been approved.')
    else:
        messages.info(request, 'This review is already approved.')

    # Redirect back to referring page or list
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:review_list'))


@permission_required('can_moderate_reviews')
def reject_review(request, review_id):
    """
    Reject a review (mark as unapproved).

    Hides the review from customers.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review = get_object_or_404(Review, id=review_id)

    if review.is_approved:
        review.is_approved = False
        review.save(update_fields=['is_approved', 'updated_at'])

        # Log admin activity
        from apps.admin_panel.models import AdminActivity
        AdminActivity.log_action(
            user=request.user,
            action='REVIEW_REJECTED',
            description=f'Rejected review #{review.id} for {review.product.name}',
            related_object_id=str(review.id)
        )

        messages.success(request, f'Review for "{review.product.name}" has been rejected.')
    else:
        messages.info(request, 'This review is already rejected.')

    # Redirect back to referring page or list
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:review_list'))


@permission_required('can_moderate_reviews')
def delete_review(request, review_id):
    """
    Permanently delete a review.

    Use with caution - this action cannot be undone.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review = get_object_or_404(Review, id=review_id)
    product_name = review.product.name
    review_id_copy = review.id

    review.delete()

    # Log admin activity
    from apps.admin_panel.models import AdminActivity
    AdminActivity.log_action(
        user=request.user,
        action='REVIEW_DELETED',
        description=f'Deleted review #{review_id_copy} for {product_name}',
        related_object_id=str(review_id_copy)
    )

    messages.success(request, f'Review for "{product_name}" has been permanently deleted.')

    # Redirect back to referring page or list
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:review_list'))


@permission_required('can_moderate_reviews')
def bulk_approve_reviews(request):
    """
    Bulk approve multiple reviews at once.

    Accepts list of review IDs via POST.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review_ids = request.POST.getlist('review_ids')

    if not review_ids:
        messages.warning(request, 'No reviews selected.')
        return redirect('admin_panel:review_list')

    # Approve all selected reviews
    updated_count = Review.objects.filter(
        id__in=review_ids,
        is_approved=False
    ).update(is_approved=True)

    # Log admin activity
    if updated_count > 0:
        from apps.admin_panel.models import AdminActivity
        AdminActivity.log_action(
            user=request.user,
            action='REVIEWS_BULK_APPROVED',
            description=f'Bulk approved {updated_count} reviews',
            related_object_id=','.join(review_ids)
        )

    messages.success(request, f'Successfully approved {updated_count} review(s).')

    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:review_list'))


@permission_required('can_moderate_reviews')
def bulk_reject_reviews(request):
    """
    Bulk reject multiple reviews at once.

    Accepts list of review IDs via POST.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review_ids = request.POST.getlist('review_ids')

    if not review_ids:
        messages.warning(request, 'No reviews selected.')
        return redirect('admin_panel:review_list')

    # Reject all selected reviews
    updated_count = Review.objects.filter(
        id__in=review_ids,
        is_approved=True
    ).update(is_approved=False)

    # Log admin activity
    if updated_count > 0:
        from apps.admin_panel.models import AdminActivity
        AdminActivity.log_action(
            user=request.user,
            action='REVIEWS_BULK_REJECTED',
            description=f'Bulk rejected {updated_count} reviews',
            related_object_id=','.join(review_ids)
        )

    messages.success(request, f'Successfully rejected {updated_count} review(s).')

    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:review_list'))


@permission_required('can_moderate_reviews')
def bulk_delete_reviews(request):
    """
    Bulk delete multiple reviews at once.

    Use with caution - this action cannot be undone.
    """
    if request.method != 'POST':
        return redirect('admin_panel:review_list')

    review_ids = request.POST.getlist('review_ids')

    if not review_ids:
        messages.warning(request, 'No reviews selected.')
        return redirect('admin_panel:review_list')

    # Delete all selected reviews
    deleted_count, _ = Review.objects.filter(id__in=review_ids).delete()

    # Log admin activity
    if deleted_count > 0:
        from apps.admin_panel.models import AdminActivity
        AdminActivity.log_action(
            user=request.user,
            action='REVIEWS_BULK_DELETED',
            description=f'Bulk deleted {deleted_count} reviews',
            related_object_id=','.join(review_ids)
        )

    messages.success(request, f'Successfully deleted {deleted_count} review(s).')

    return redirect('admin_panel:review_list')


@permission_required('can_view_analytics')
def review_analytics(request):
    """
    Analytics dashboard for reviews.

    Shows:
    - Review statistics (total, pending, average rating)
    - Reviews over time
    - Rating distribution
    - Top reviewed products
    - Recent reviews
    """
    # Time period filter
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # Overall statistics
    total_reviews = Review.objects.count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    approved_reviews = Review.objects.filter(is_approved=True).count()
    avg_rating = Review.objects.filter(is_approved=True).aggregate(
        Avg('rating')
    )['rating__avg'] or 0

    # Reviews in selected period
    period_reviews = Review.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    period_count = period_reviews.count()
    period_avg_rating = period_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Rating distribution
    rating_distribution = []
    for rating in range(1, 6):
        count = Review.objects.filter(rating=rating, is_approved=True).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_distribution.append({
            'rating': rating,
            'count': count,
            'percentage': round(percentage, 1)
        })

    # Top reviewed products (most reviews)
    top_reviewed = Product.objects.annotate(
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).filter(review_count__gt=0).order_by('-review_count')[:10]

    # Top rated products (highest average rating, min 3 reviews)
    top_rated = Product.objects.annotate(
        review_count=Count('reviews', filter=Q(reviews__is_approved=True)),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).filter(review_count__gte=3).order_by('-avg_rating')[:10]

    # Recent reviews (last 10)
    recent_reviews = Review.objects.select_related(
        'product', 'user'
    ).order_by('-created_at')[:10]

    # Reviews by day (last 30 days for chart)
    from django.db.models.functions import TruncDate
    reviews_by_day = Review.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Format for Chart.js
    chart_data = {
        'dates': [item['day'].isoformat() for item in reviews_by_day],
        'counts': [item['count'] for item in reviews_by_day]
    }

    context = {
        'stats': {
            'total': total_reviews,
            'pending': pending_reviews,
            'approved': approved_reviews,
            'avg_rating': round(avg_rating, 2),
            'period_count': period_count,
            'period_avg_rating': round(period_avg_rating, 2)
        },
        'rating_distribution': rating_distribution,
        'top_reviewed': top_reviewed,
        'top_rated': top_rated,
        'recent_reviews': recent_reviews,
        'chart_data': chart_data,
        'days': days,
        'start_date': start_date.date(),
        'end_date': end_date.date()
    }

    return render(request, 'admin_panel/reviews/analytics.html', context)


@permission_required('can_moderate_reviews')
def review_detail(request, review_id):
    """
    Detailed view of a single review with moderation actions.

    Shows:
    - Full review content
    - User information
    - Product information
    - Moderation history (if available)
    """
    review = get_object_or_404(
        Review.objects.select_related('product', 'user'),
        id=review_id
    )

    # Get other reviews by same user
    user_reviews = Review.objects.filter(
        user=review.user
    ).exclude(id=review.id).select_related('product')[:5]

    # Get other reviews for same product
    product_reviews = Review.objects.filter(
        product=review.product,
        is_approved=True
    ).exclude(id=review.id).select_related('user')[:5]

    context = {
        'review': review,
        'user_reviews': user_reviews,
        'product_reviews': product_reviews
    }

    return render(request, 'admin_panel/reviews/detail.html', context)
