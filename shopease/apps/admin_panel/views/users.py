"""
========================================
USER & ROLE MANAGEMENT VIEWS
========================================

Views for managing users, roles, and admin activity logs.

Includes:
- User list with filtering
- User detail and editing
- Role assignment for staff users
- Activity log viewer
- Staff user creation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import timedelta

from apps.admin_panel.decorators import admin_required, permission_required, role_required
from apps.admin_panel.models import AdminRole, AdminActivity
from apps.accounts.models import Profile


@permission_required('can_view_users')
def user_list(request):
    """
    Display list of all users with filtering.

    Filters:
    - User type (all, staff, customers)
    - Role (for staff users)
    - Search by username, email, name
    - Date joined range
    """
    # Base queryset
    users = User.objects.select_related('profile').prefetch_related('admin_role').order_by('-date_joined')

    # User type filter
    user_type = request.GET.get('type', 'all')
    if user_type == 'staff':
        users = users.filter(is_staff=True)
    elif user_type == 'customers':
        users = users.filter(is_staff=False)

    # Role filter (for staff users)
    role = request.GET.get('role', '')
    if role:
        users = users.filter(admin_role__role=role)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Date filter
    days = request.GET.get('days', '')
    if days and days.isdigit():
        start_date = timezone.now() - timedelta(days=int(days))
        users = users.filter(date_joined__gte=start_date)

    # Status filter
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    customer_users = User.objects.filter(is_staff=False).count()
    active_users = User.objects.filter(is_active=True).count()

    # Role choices for filter
    role_choices = AdminRole.ROLE_CHOICES

    context = {
        'page_obj': page_obj,
        'user_type': user_type,
        'role': role,
        'search_query': search_query,
        'days': days,
        'status': status,
        'role_choices': role_choices,
        'stats': {
            'total': total_users,
            'staff': staff_users,
            'customers': customer_users,
            'active': active_users
        }
    }

    return render(request, 'admin_panel/users/list.html', context)


@permission_required('can_view_users')
def user_detail(request, user_id):
    """
    Display detailed information about a user.

    Shows:
    - User profile information
    - Role and permissions (if staff)
    - Order history
    - Review activity
    - Admin activity (if staff)
    """
    user = get_object_or_404(
        User.objects.select_related('profile').prefetch_related('admin_role'),
        id=user_id
    )

    # Get user's role if they have one
    try:
        admin_role = user.admin_role
    except AdminRole.DoesNotExist:
        admin_role = None

    # Get user's orders
    from apps.orders.models import Order
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    total_orders = Order.objects.filter(user=user).count()

    # Get user's reviews
    from apps.products.models import Review
    reviews = Review.objects.filter(user=user).select_related('product').order_by('-created_at')[:10]
    total_reviews = Review.objects.filter(user=user).count()

    # Get admin activity if staff
    activities = []
    if user.is_staff:
        activities = AdminActivity.objects.filter(user=user).order_by('-timestamp')[:20]

    context = {
        'user_obj': user,
        'admin_role': admin_role,
        'orders': orders,
        'total_orders': total_orders,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'activities': activities
    }

    return render(request, 'admin_panel/users/detail.html', context)


@permission_required('can_edit_users')
def assign_role(request, user_id):
    """
    Assign or update admin role for a user.

    Makes user staff and assigns role with permissions.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role = request.POST.get('role')

        if not role or role not in dict(AdminRole.ROLE_CHOICES):
            messages.error(request, 'Invalid role selected.')
            return redirect('admin_panel:user_detail', user_id=user_id)

        # Make user staff
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])

        # Create or update AdminRole
        admin_role, created = AdminRole.objects.update_or_create(
            user=user,
            defaults={'role': role}
        )

        # Log activity
        AdminActivity.log_action(
            user=request.user,
            action='ROLE_ASSIGNED',
            description=f'Assigned role {role} to {user.username}',
            related_object_id=str(user.id)
        )

        if created:
            messages.success(request, f'Successfully assigned {admin_role.get_role_display()} role to {user.username}.')
        else:
            messages.success(request, f'Successfully updated role for {user.username} to {admin_role.get_role_display()}.')

        return redirect('admin_panel:user_detail', user_id=user_id)

    # GET request - show form
    try:
        current_role = user.admin_role
    except AdminRole.DoesNotExist:
        current_role = None

    context = {
        'user_obj': user,
        'current_role': current_role,
        'role_choices': AdminRole.ROLE_CHOICES
    }

    return render(request, 'admin_panel/users/assign_role.html', context)


@permission_required('can_edit_users')
def remove_role(request, user_id):
    """
    Remove admin role from a user.

    Removes staff status and deletes AdminRole.
    """
    if request.method != 'POST':
        return redirect('admin_panel:user_detail', user_id=user_id)

    user = get_object_or_404(User, id=user_id)

    # Cannot remove superuser
    if user.is_superuser:
        messages.error(request, 'Cannot remove superuser privileges.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    # Cannot remove yourself
    if user == request.user:
        messages.error(request, 'Cannot remove your own admin role.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    try:
        admin_role = user.admin_role
        role_name = admin_role.get_role_display()
        admin_role.delete()

        # Remove staff status
        user.is_staff = False
        user.save(update_fields=['is_staff'])

        # Log activity
        AdminActivity.log_action(
            user=request.user,
            action='ROLE_REMOVED',
            description=f'Removed {role_name} role from {user.username}',
            related_object_id=str(user.id)
        )

        messages.success(request, f'Successfully removed admin role from {user.username}.')

    except AdminRole.DoesNotExist:
        messages.info(request, 'User does not have an admin role.')

    return redirect('admin_panel:user_detail', user_id=user_id)


@permission_required('can_edit_users')
def toggle_user_status(request, user_id):
    """
    Activate or deactivate a user account.
    """
    if request.method != 'POST':
        return redirect('admin_panel:user_detail', user_id=user_id)

    user = get_object_or_404(User, id=user_id)

    # Cannot deactivate superuser
    if user.is_superuser:
        messages.error(request, 'Cannot deactivate superuser account.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    # Cannot deactivate yourself
    if user == request.user:
        messages.error(request, 'Cannot deactivate your own account.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    # Toggle status
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    # Log activity
    action = 'USER_ACTIVATED' if user.is_active else 'USER_DEACTIVATED'
    AdminActivity.log_action(
        user=request.user,
        action=action,
        description=f'{"Activated" if user.is_active else "Deactivated"} user {user.username}',
        related_object_id=str(user.id)
    )

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'Successfully {status} {user.username}.')

    return redirect('admin_panel:user_detail', user_id=user_id)


@role_required('SUPER_ADMIN')
def create_staff_user(request):
    """
    Create a new staff user with admin role.

    Only accessible to super admins.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role')

        # Validation
        errors = []

        if not username or not email or not password:
            errors.append('Username, email, and password are required.')

        if password != password_confirm:
            errors.append('Passwords do not match.')

        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if User.objects.filter(email=email).exists():
            errors.append('Email already exists.')

        if not role or role not in dict(AdminRole.ROLE_CHOICES):
            errors.append('Valid role is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'admin_panel/users/create_staff.html', {
                'role_choices': AdminRole.ROLE_CHOICES,
                'form_data': request.POST
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_active=True
        )

        # Create admin role
        admin_role = AdminRole.objects.create(
            user=user,
            role=role
        )

        # Log activity
        AdminActivity.log_action(
            user=request.user,
            action='STAFF_USER_CREATED',
            description=f'Created staff user {username} with role {admin_role.get_role_display()}',
            related_object_id=str(user.id)
        )

        messages.success(request, f'Successfully created staff user {username} with role {admin_role.get_role_display()}.')

        return redirect('admin_panel:user_detail', user_id=user.id)

    # GET request - show form
    context = {
        'role_choices': AdminRole.ROLE_CHOICES
    }

    return render(request, 'admin_panel/users/create_staff.html', context)


@permission_required('can_view_activity')
def activity_log(request):
    """
    Display admin activity log with filtering.

    Shows all admin actions for audit purposes.
    """
    # Base queryset
    activities = AdminActivity.objects.select_related('user').order_by('-timestamp')

    # User filter
    user_id = request.GET.get('user', '')
    if user_id and user_id.isdigit():
        activities = activities.filter(user_id=user_id)

    # Action filter
    action = request.GET.get('action', '')
    if action:
        activities = activities.filter(action=action)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        activities = activities.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    # Date filter
    days = request.GET.get('days', '30')
    if days and days.isdigit():
        start_date = timezone.now() - timedelta(days=int(days))
        activities = activities.filter(timestamp__gte=start_date)

    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get all admin users for filter
    admin_users = User.objects.filter(is_staff=True).order_by('username')

    # Get unique actions for filter
    unique_actions = AdminActivity.objects.values_list('action', flat=True).distinct()

    # Statistics
    total_activities = AdminActivity.objects.count()
    period_activities = AdminActivity.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=int(days) if days.isdigit() else 30)
    ).count()

    # Activity by action (last 30 days)
    from django.db.models import Count
    activity_breakdown = AdminActivity.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).values('action').annotate(count=Count('id')).order_by('-count')[:10]

    context = {
        'page_obj': page_obj,
        'admin_users': admin_users,
        'unique_actions': sorted(unique_actions),
        'selected_user': user_id,
        'selected_action': action,
        'search_query': search_query,
        'days': days,
        'stats': {
            'total': total_activities,
            'period': period_activities
        },
        'activity_breakdown': activity_breakdown
    }

    return render(request, 'admin_panel/users/activity_log.html', context)


@permission_required('can_view_users')
def staff_list(request):
    """
    Display list of staff users only.

    Quick view for managing admin team.
    """
    staff_users = User.objects.filter(
        is_staff=True
    ).select_related('profile').prefetch_related('admin_role').order_by('-date_joined')

    # Role filter
    role = request.GET.get('role', '')
    if role:
        staff_users = staff_users.filter(admin_role__role=role)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        staff_users = staff_users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(staff_users, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'role': role,
        'search_query': search_query,
        'role_choices': AdminRole.ROLE_CHOICES
    }

    return render(request, 'admin_panel/users/staff_list.html', context)


@admin_required
def admin_profile(request):
    """
    Admin's own profile page.

    Shows:
    - User information
    - Admin role and permissions
    - Recent admin activity
    """
    # Get current user's admin role
    try:
        admin_role = request.user.admin_role
    except AdminRole.DoesNotExist:
        admin_role = None

    # Get recent admin activity
    activities = AdminActivity.objects.filter(user=request.user).order_by('-timestamp')[:10]

    context = {
        'admin_role': admin_role,
        'activities': activities,
    }

    return render(request, 'admin_panel/users/profile.html', context)


# ==========================================
# SUPERUSER MANAGEMENT
# ==========================================

@admin_required
@role_required('SUPER_ADMIN')
def superuser_list(request):
    """
    List all superusers with creation form.
    Only accessible to existing superusers.
    """
    from apps.admin_panel.forms import SuperuserCreationForm

    # Get all superusers
    superusers = User.objects.filter(is_superuser=True).order_by('username')

    # Handle superuser creation form
    form = SuperuserCreationForm()
    if request.method == 'POST':
        form = SuperuserCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_staff=True,
                is_superuser=True
            )

            # Create AdminRole with SUPER_ADMIN
            AdminRole.objects.create(
                user=user,
                role='SUPER_ADMIN',
                can_view_orders=True,
                can_edit_orders=True,
                can_process_refunds=True,
                can_view_products=True,
                can_edit_products=True,
                can_manage_featured=True,
                can_moderate_reviews=True,
                can_view_users=True,
                can_manage_roles=True,
                can_view_analytics=True,
                can_export_data=True
            )

            # Log activity
            AdminActivity.objects.create(
                user=request.user,
                action='SUPERUSER_CREATED',
                description=f'Created superuser account: {user.username}',
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )

            messages.success(request, f'Superuser "{user.username}" created successfully.')
            return redirect('admin_panel:superuser_list')

    context = {
        'superusers': superusers,
        'form': form,
        'superuser_count': superusers.count(),
    }

    return render(request, 'admin_panel/users/superuser_list.html', context)


@admin_required
@role_required('SUPER_ADMIN')
def remove_superuser(request, user_id):
    """
    Remove superuser privileges from a user.
    Cannot remove self or last superuser.
    """
    user = get_object_or_404(User, id=user_id, is_superuser=True)

    # Check: Cannot remove self
    if user == request.user:
        messages.error(request, 'You cannot remove your own superuser privileges.')
        return redirect('admin_panel:superuser_list')

    # Check: At least one superuser must remain
    superuser_count = User.objects.filter(is_superuser=True).count()
    if superuser_count <= 1:
        messages.error(request, 'Cannot remove the last superuser. At least one must remain.')
        return redirect('admin_panel:superuser_list')

    if request.method == 'POST':
        # Remove superuser status
        user.is_superuser = False
        user.save()

        # Update or remove AdminRole
        try:
            admin_role = user.admin_role
            # Option 1: Remove role entirely
            admin_role.delete()
            # Option 2: Change to different role (uncomment if preferred)
            # admin_role.role = 'CUSTOMER_SERVICE'
            # admin_role.save()
        except AdminRole.DoesNotExist:
            pass

        # Log activity
        AdminActivity.objects.create(
            user=request.user,
            action='SUPERUSER_REMOVED',
            description=f'Removed superuser privileges from: {user.username}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

        messages.success(request, f'Superuser privileges removed from "{user.username}".')
        return redirect('admin_panel:superuser_list')

    context = {'superuser': user}
    return render(request, 'admin_panel/users/remove_superuser_confirm.html', context)


# ==========================================
# ROLE MANAGEMENT
# ==========================================

@permission_required('can_manage_roles')
def role_list(request):
    """
    List all roles (predefined + custom) with user counts.
    """
    # Get all roles with user counts
    roles = AdminRole.objects.values('role', 'is_custom_role', 'custom_role_name').annotate(
        user_count=Count('id')
    ).order_by('is_custom_role', 'role')

    # Get predefined roles that haven't been used yet
    predefined_roles = [
        {'role': 'CUSTOMER_SERVICE', 'display': 'Customer Service'},
        {'role': 'INVENTORY_MANAGER', 'display': 'Inventory Manager'},
        {'role': 'MARKETING_MANAGER', 'display': 'Marketing Manager'},
        {'role': 'ORDER_MANAGER', 'display': 'Order Manager'},
        {'role': 'SUPER_ADMIN', 'display': 'Super Admin'},
    ]

    context = {
        'roles': roles,
        'predefined_roles': predefined_roles,
    }

    return render(request, 'admin_panel/users/role_list.html', context)


@permission_required('can_manage_roles')
def role_create(request):
    """
    Create a new custom role with granular permissions.
    """
    from apps.admin_panel.forms import CustomRoleForm

    if request.method == 'POST':
        form = CustomRoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.is_custom_role = True
            role.role = ''  # Custom roles don't use predefined role field
            role.save()

            # Log activity
            AdminActivity.objects.create(
                user=request.user,
                action='ROLE_CREATED',
                description=f'Created custom role: {role.custom_role_name}',
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )

            messages.success(request, f'Custom role "{role.custom_role_name}" created successfully.')
            return redirect('admin_panel:role_list')
    else:
        form = CustomRoleForm()

    context = {'form': form, 'action': 'Create'}
    return render(request, 'admin_panel/users/role_form.html', context)


@permission_required('can_manage_roles')
def role_edit(request, role_id):
    """
    Edit an existing custom role's permissions.
    Cannot edit predefined roles.
    """
    from apps.admin_panel.forms import CustomRoleForm

    role = get_object_or_404(AdminRole, id=role_id, is_custom_role=True)

    if request.method == 'POST':
        form = CustomRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()

            # Log activity
            AdminActivity.objects.create(
                user=request.user,
                action='ROLE_UPDATED',
                description=f'Updated custom role: {role.custom_role_name}',
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )

            messages.success(request, f'Role "{role.custom_role_name}" updated successfully.')
            return redirect('admin_panel:role_list')
    else:
        form = CustomRoleForm(instance=role)

    context = {'form': form, 'role': role, 'action': 'Edit'}
    return render(request, 'admin_panel/users/role_form.html', context)


@permission_required('can_manage_roles')
def role_delete(request, role_id):
    """
    Delete a custom role.
    Cannot delete if users are assigned to it.
    """
    role = get_object_or_404(AdminRole, id=role_id, is_custom_role=True)

    # Check if any users have this role
    if AdminRole.objects.filter(custom_role_name=role.custom_role_name).count() > 1:
        messages.error(request, f'Cannot delete role "{role.custom_role_name}" - users are still assigned to it.')
        return redirect('admin_panel:role_list')

    if request.method == 'POST':
        role_name = role.custom_role_name
        role.delete()

        # Log activity
        AdminActivity.objects.create(
            user=request.user,
            action='ROLE_DELETED',
            description=f'Deleted custom role: {role_name}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

        messages.success(request, f'Role "{role_name}" deleted successfully.')
        return redirect('admin_panel:role_list')

    context = {'role': role}
    return render(request, 'admin_panel/users/role_delete_confirm.html', context)
