"""
========================================
ORDER MANAGEMENT VIEWS
========================================

Views for managing orders in the admin panel:
- Order list with filters
- Order detail view
- Update order status
- Process refunds
- Generate invoices (PDF)

Access controlled by permissions decorators.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from apps.admin_panel.decorators import permission_required, log_admin_activity
from apps.admin_panel.models import Refund, AdminActivity
from apps.orders.models import Order, OrderItem
from decimal import Decimal


@permission_required('can_view_orders')
def order_list(request):
    """
    Display list of all orders with filtering options.

    Filters:
    - Status (PENDING, COMPLETED, SHIPPED, etc.)
    - Date range
    - Search by order ID, customer name, email

    Access: Requires can_view_orders permission
    """
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Apply status filter
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Apply search filter
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(shipping_full_name__icontains=search_query) |
            Q(shipping_email__icontains=search_query) |
            Q(shipping_phone__icontains=search_query)
        )

    # Apply date range filters
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    # Pagination (50 per page)
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics for display
    total_orders = orders.count()
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'admin_panel/orders/list.html', context)


@permission_required('can_view_orders')
def order_detail(request, order_id):
    """
    Display detailed information about a specific order.

    Shows:
    - Order items
    - Shipping information
    - Payment details
    - Order history/notes
    - Refunds (if any)

    Access: Requires can_view_orders permission
    """
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product', 'refunds'),
        order_id=order_id
    )

    # Get refunds for this order
    refunds = order.refunds.all().order_by('-created_at')

    # Get admin activities for this order
    activities = AdminActivity.objects.filter(
        order_id=order_id
    ).select_related('user').order_by('-timestamp')[:10]

    context = {
        'order': order,
        'refunds': refunds,
        'activities': activities,
    }

    return render(request, 'admin_panel/orders/detail.html', context)


@permission_required('can_edit_orders')
@log_admin_activity('ORDER_STATUS_CHANGE')
def update_order_status(request, order_id):
    """
    Update the status of an order.

    POST parameters:
    - status: New status value
    - admin_notes: Optional admin notes

    Access: Requires can_edit_orders permission
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel:order_detail', order_id=order_id)

    order = get_object_or_404(Order, order_id=order_id)
    new_status = request.POST.get('status')
    admin_notes = request.POST.get('admin_notes', '')

    # Validate status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status selected.')
        return redirect('admin_panel:order_detail', order_id=order_id)

    # Store old status for logging
    old_status = order.status

    # Update order
    order.status = new_status
    if admin_notes:
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        note = f"[{timestamp}] Status changed from {order.get_status_display()} to {dict(Order.STATUS_CHOICES)[new_status]} by {request.user.username}"
        if admin_notes:
            note += f"\nNotes: {admin_notes}"
        order.admin_notes += f"\n{note}" if order.admin_notes else note

    order.save()

    # Log activity
    AdminActivity.objects.create(
        user=request.user,
        action='ORDER_STATUS_CHANGE',
        description=f"Changed order #{str(order_id)[:8]} status from {old_status} to {new_status}",
        order_id=order_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(
        request,
        f'Order status updated to {dict(Order.STATUS_CHOICES)[new_status]} successfully.'
    )

    return redirect('admin_panel:order_detail', order_id=order_id)


@permission_required('can_process_refunds')
def refund_detail(request, refund_id):
    """
    Display refund details and processing options.

    Access: Requires can_process_refunds permission
    """
    refund = get_object_or_404(
        Refund.objects.select_related('order', 'processed_by'),
        refund_id=refund_id
    )

    context = {
        'refund': refund,
    }

    return render(request, 'admin_panel/orders/refund_detail.html', context)


@permission_required('can_process_refunds')
@log_admin_activity('REFUND_PROCESSED')
def process_refund(request, refund_id):
    """
    Process a refund request (approve, reject, or complete).

    POST parameters:
    - action: 'approve', 'reject', or 'complete'
    - admin_notes: Optional notes
    - rejection_reason: Required if action is 'reject'

    Access: Requires can_process_refunds permission
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel:order_detail', order_id=request.GET.get('order_id'))

    refund = get_object_or_404(Refund, refund_id=refund_id)
    action = request.POST.get('action')
    admin_notes = request.POST.get('admin_notes', '')

    if action == 'approve':
        refund.approve(request.user)
        if admin_notes:
            refund.admin_notes += f"\n{admin_notes}"
            refund.save(update_fields=['admin_notes'])
        messages.success(request, 'Refund approved successfully.')

    elif action == 'reject':
        rejection_reason = request.POST.get('rejection_reason', '')
        refund.reject(request.user, rejection_reason)
        messages.success(request, 'Refund rejected.')

    elif action == 'complete':
        # Mark return as received if checkbox is checked
        if request.POST.get('return_received'):
            refund.return_received = True
            refund.save(update_fields=['return_received'])

        refund.complete(request.user)
        if admin_notes:
            refund.admin_notes += f"\n{admin_notes}"
            refund.save(update_fields=['admin_notes'])
        messages.success(request, 'Refund completed successfully. Stock has been restored.')

    else:
        messages.error(request, 'Invalid action.')
        return redirect('admin_panel:refund_detail', refund_id=refund_id)

    # Log activity
    AdminActivity.objects.create(
        user=request.user,
        action='REFUND_PROCESSED',
        description=f"Processed refund #{str(refund_id)[:8]} - Action: {action}",
        order_id=refund.order.order_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return redirect('admin_panel:order_detail', order_id=refund.order.order_id)


@permission_required('can_view_orders')
def generate_invoice(request, order_id):
    """
    Generate PDF invoice for an order.

    Uses WeasyPrint to convert HTML template to PDF.

    Access: Requires can_view_orders permission
    """
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        order_id=order_id
    )

    try:
        from apps.admin_panel.utils.pdf_generator import generate_invoice_pdf

        filename, pdf_bytes = generate_invoice_pdf(order)

        # Log activity
        AdminActivity.objects.create(
            user=request.user,
            action='INVOICE_GENERATED',
            description=f"Generated invoice for order #{str(order_id)[:8]}",
            order_id=order_id,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        # Return PDF as download
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except ImportError:
        messages.error(
            request,
            'PDF generation is not available. Please install WeasyPrint: pip install weasyprint'
        )
        return redirect('admin_panel:order_detail', order_id=order_id)
    except Exception as e:
        messages.error(request, f'Error generating invoice: {str(e)}')
        return redirect('admin_panel:order_detail', order_id=order_id)


@permission_required('can_edit_orders')
def bulk_update_status(request):
    """
    Update status for multiple orders at once.

    POST parameters:
    - order_ids[]: List of order IDs
    - status: New status to apply

    Access: Requires can_edit_orders permission
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel:order_list')

    order_ids = request.POST.getlist('order_ids[]')
    new_status = request.POST.get('status')

    if not order_ids:
        messages.error(request, 'No orders selected.')
        return redirect('admin_panel:order_list')

    # Validate status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status selected.')
        return redirect('admin_panel:order_list')

    # Update orders
    updated_count = Order.objects.filter(order_id__in=order_ids).update(status=new_status)

    # Log activity
    AdminActivity.objects.create(
        user=request.user,
        action='BULK_ACTION',
        description=f"Bulk updated {updated_count} orders to status: {new_status}",
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f'Successfully updated {updated_count} orders to {dict(Order.STATUS_CHOICES)[new_status]}.')

    return redirect('admin_panel:order_list')
