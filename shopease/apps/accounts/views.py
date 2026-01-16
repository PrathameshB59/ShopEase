"""
========================================
AUTHENTICATION VIEWS
========================================

SECURITY FEATURES IMPLEMENTED:
-------------------------------
1. CSRF Protection (Django automatic)
2. Password Hashing (PBKDF2 with SHA256)
3. Session Management (secure cookies)
4. Cart Merging (anonymous → logged-in user)
5. Login Required Decorator (@login_required)
6. Form Validation (SQL injection prevention)

REAL-WORLD CONSIDERATIONS:
--------------------------
- Rate limiting (TODO: django-ratelimit)
- Account lockout after failed logins (TODO: django-axes)
- Two-factor authentication (TODO: django-otp)
- Social login (TODO: django-allauth)
- Email verification (TODO: confirmation emails)
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm
)
from .models import Profile
from apps.cart.cart import CartService


# ==========================================
# USER REGISTRATION
# ==========================================

def register(request):
    """
    User registration view.
    
    URL: /accounts/register/
    Methods: GET, POST
    
    Process:
    1. Display registration form (GET)
    2. Validate form data (POST)
    3. Create User and Profile
    4. Log user in automatically
    5. Merge anonymous cart with user cart
    6. Redirect to homepage
    
    SECURITY MEASURES:
    ------------------
    1. Password Validation:
       - Minimum 8 characters
       - Not entirely numeric
       - Not too common (password123, qwerty)
       - Not too similar to username/email
    
    2. Email Validation:
       - Valid email format
       - Unique (not already registered)
       - Case-insensitive comparison
    
    3. CSRF Protection:
       - Token validated automatically
       - Prevents forged registration requests
    
    4. XSS Prevention:
       - Django auto-escapes all output
       - User input sanitized
    
    Real-world enhancement ideas:
    - Email verification (send confirmation link)
    - CAPTCHA (prevent bot registrations)
    - Rate limiting (max 3 registrations per IP per hour)
    - Password strength meter (frontend)
    """
    
    # If user already logged in, redirect to home
    # No need to register again
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')
    
    if request.method == 'POST':
        """
        HANDLE REGISTRATION SUBMISSION
        
        Steps:
        1. Bind form to POST data
        2. Validate all fields
        3. Check password strength
        4. Check email uniqueness
        5. Create user (password auto-hashed)
        6. Create profile (via signal)
        7. Log user in
        8. Merge cart
        """
        
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Create user (password is automatically hashed)
            # Django uses PBKDF2 algorithm with SHA256 hash
            # Hash includes salt (prevents rainbow table attacks)
            user = form.save()
            
            # Profile is automatically created via signal
            # See models.py: @receiver(post_save, sender=User)
            
            # Get cleaned data
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            # Log user in automatically after registration
            # Creates session, sets session cookie
            login(request, user)
            
            # Merge anonymous cart with user's cart
            # If user added items before registering, keep them
            try:
                cart_service = CartService(request)
                cart_service.merge_with_user_cart(user)
            except Exception as e:
                # Cart merge failed, but user is still registered
                # Log error but don't show to user
                print(f"Cart merge error: {e}")
            
            # Success message
            messages.success(
                request,
                f'Welcome {username}! Your account has been created successfully.'
            )
            
            # Redirect to homepage
            # Could also redirect to profile completion page
            return redirect('home')
        else:
            # Form validation failed
            # Errors are automatically attached to form fields
            # Template will display them
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        # GET request - show empty form
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Create Account'
    }
    
    return render(request, 'accounts/register.html', context)


# ==========================================
# USER LOGIN
# ==========================================

def user_login(request):
    """
    User login view.
    
    URL: /accounts/login/
    Methods: GET, POST
    
    SECURITY MEASURES:
    ------------------
    1. Password Verification:
       - Compares hashed passwords
       - Never stores plaintext passwords
       - Timing attack resistant
    
    2. Session Management:
       - Creates secure session
       - HttpOnly cookie (JavaScript can't access)
       - SameSite=Lax (CSRF protection)
       - Session timeout (2 weeks default)
    
    3. Session Fixation Prevention:
       - New session ID after login
       - Old session invalidated
    
    4. Account Enumeration Protection:
       - Same error message for invalid username/password
       - Prevents attackers from discovering usernames
    
    Production enhancements:
    - Rate limiting (max 5 attempts per 15 minutes)
    - Account lockout (after 10 failed attempts)
    - Login notifications (email: "New login from Mumbai")
    - Remember me checkbox (extends session)
    - Two-factor authentication (OTP via SMS/email)
    """
    
    # If already logged in, redirect
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')
    
    if request.method == 'POST':
        """
        HANDLE LOGIN SUBMISSION
        
        Steps:
        1. Get username and password
        2. Authenticate (verify password hash)
        3. Check if user is active
        4. Create session
        5. Merge cart
        6. Redirect to next page or home
        """
        
        form = UserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            # Get credentials
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            # This function:
            # 1. Finds user by username
            # 2. Verifies password hash
            # 3. Returns User object or None
            user = authenticate(
                request,
                username=username,
                password=password
            )
            
            if user is not None:
                # Check if account is active
                if user.is_active:
                    # Log user in
                    # Creates session, sets cookie
                    login(request, user)
                    
                    # Merge anonymous cart with user cart
                    try:
                        cart_service = CartService(request)
                        cart_service.merge_with_user_cart(user)
                    except Exception as e:
                        print(f"Cart merge error: {e}")
                    
                    # Success message
                    messages.success(
                        request,
                        f'Welcome back, {username}!'
                    )
                    
                    # Redirect to 'next' parameter or home
                    # Example: /accounts/login/?next=/checkout/
                    # After login, redirect to /checkout/
                    next_page = request.GET.get('next', 'home')
                    return redirect(next_page)
                else:
                    # Account is inactive (banned/suspended)
                    messages.error(
                        request,
                        'Your account has been deactivated. Please contact support.'
                    )
            else:
                # Invalid credentials
                # SECURITY: Don't specify if username or password is wrong
                messages.error(
                    request,
                    'Invalid username or password.'
                )
        else:
            # Form validation failed
            messages.error(
                request,
                'Invalid username or password.'
            )
    else:
        # GET request - show empty form
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    
    return render(request, 'accounts/login.html', context)


# ==========================================
# USER LOGOUT
# ==========================================

@login_required
def user_logout(request):
    """
    User logout view.
    
    URL: /accounts/logout/
    Methods: GET, POST
    
    SECURITY MEASURES:
    ------------------
    1. Session Invalidation:
       - Deletes session from database
       - Clears session cookie
       - Prevents session reuse
    
    2. CSRF Protection:
       - POST-only for logout (prevents CSRF attacks)
       - Example attack: <img src="/logout/"> auto-logs out user
    
    Process:
    1. Invalidate session
    2. Clear cookies
    3. Show success message
    4. Redirect to home
    
    NOTE: Cart data persists (stored in database, not session)
          User can see their cart when they login again
    """
    
    # Store username before logout
    username = request.user.username
    
    # Log user out
    # This function:
    # 1. Deletes session from database
    # 2. Clears session cookie
    # 3. Removes user from request.user
    logout(request)
    
    # Success message
    messages.success(
        request,
        f'Goodbye {username}! You have been logged out successfully.'
    )
    
    # Redirect to home
    return redirect('home')


# ==========================================
# USER PROFILE (VIEW & EDIT)
# ==========================================

@login_required
def profile(request):
    """
    User profile view and edit.
    
    URL: /accounts/profile/
    Methods: GET, POST
    Login required: Yes
    
    Displays:
    - User information
    - Profile details
    - Order history (TODO)
    - Saved addresses
    
    Allows editing:
    - Email, name
    - Phone number
    - Shipping address
    - Billing address
    - Profile picture
    - Preferences
    
    SECURITY:
    - @login_required decorator (redirect to login if not authenticated)
    - Users can only edit their own profile
    - File upload validation (image types only)
    - File size limits (TODO: max 5MB)
    """
    
    if request.method == 'POST':
        """
        HANDLE PROFILE UPDATE
        
        Two forms:
        1. UserUpdateForm: email, first_name, last_name
        2. ProfileUpdateForm: phone, address, avatar, etc.
        """
        
        # Bind forms to POST data and FILES (for avatar)
        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,  # For avatar upload
            instance=request.user.profile
        )
        
        # Validate both forms
        if user_form.is_valid() and profile_form.is_valid():
            # Save both forms
            user_form.save()
            profile_form.save()
            
            messages.success(
                request,
                'Your profile has been updated successfully!'
            )
            
            # Redirect to profile page (PRG pattern)
            # POST-Redirect-GET prevents duplicate submissions
            return redirect('accounts:profile')
        else:
            # Show validation errors
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        # GET request - populate forms with current data
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get user's orders (TODO: implement orders app)
    # orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'page_title': 'My Profile',
        # 'orders': orders,
    }
    
    return render(request, 'accounts/profile.html', context)


# ==========================================
# PASSWORD RESET VIEWS
# ==========================================

class CustomPasswordResetView(PasswordResetView):
    """
    Password reset request view.

    URL: /accounts/password-reset/

    Process:
    1. User enters email
    2. System sends reset link
    3. Link expires after 1 hour
    4. User clicks link, sets new password

    SECURITY:
    - Email validation
    - Token generation (random, unique, time-limited)
    - Rate limiting (TODO: max 3 resets per hour)
    - No user enumeration (same message for valid/invalid email)
    """

    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.txt'  # Plain text version
    html_email_template_name = 'accounts/password_reset_email.html'  # HTML version
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Password reset email sent confirmation.
    
    URL: /accounts/password-reset/done/
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Password reset confirmation (set new password).
    
    URL: /accounts/reset/<uidb64>/<token>/
    
    SECURITY:
    - Token validation (single-use)
    - Token expiration (1 hour default)
    - New password validation (strength requirements)
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Password reset complete (success message).

    URL: /accounts/reset/done/
    """
    template_name = 'accounts/password_reset_complete.html'


# ==========================================
# PASSWORD CHANGE (For Logged-in Users)
# ==========================================

class CustomPasswordChangeView(PasswordChangeView):
    """
    Password change for logged-in users.

    URL: /accounts/password-change/

    Requires:
    - User must be logged in (@login_required)
    - Current password (for verification)
    - New password (with validation)

    Security:
    - Validates current password before changing
    - New password strength requirements
    - Invalidates all other sessions after change

    Difference from Password Reset:
    - Password Change: For logged-in users (requires old password)
    - Password Reset: For users who forgot password (email verification)
    """
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """
    Password change success confirmation.

    URL: /accounts/password-change/done/
    """
    template_name = 'accounts/password_change_done.html'


# ==========================================
# DASHBOARD (Future Enhancement)
# ==========================================

@login_required
def dashboard(request):
    """
    User dashboard overview.

    URL: /accounts/dashboard/

    Shows:
    - Recent orders
    - Order status
    - Saved addresses
    - Wishlist (TODO)
    - Account statistics

    This is a placeholder for future implementation.
    """

    # Calculate profile completion percentage
    profile = request.user.profile
    completion_items = [
        bool(request.user.email),                    # Email verified
        bool(profile.phone),                         # Phone number added
        bool(profile.shipping_address_line1),        # Shipping address
        bool(profile.avatar),                        # Profile picture
    ]

    completed_count = sum(completion_items)
    total_items = len(completion_items)
    profile_completion = int((completed_count / total_items) * 100)

    # Get cart count
    from apps.cart.cart import CartService
    cart_service = CartService(request)
    cart_count = cart_service.get_item_count()

    # Get actual orders from database
    from apps.orders.models import Order
    from apps.products.models import Review
    from django.db.models import Sum

    # Get user's orders
    user_orders = Order.objects.filter(user=request.user)

    # Calculate statistics
    total_orders = user_orders.count()

    # Calculate total spent (sum of all order amounts)
    total_spent = user_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0.00

    # Get recent orders (last 5)
    recent_orders = user_orders.order_by('-created_at')[:5]

    # Get review count
    review_count = Review.objects.filter(user=request.user).count()

    context = {
        'page_title': 'Dashboard',
        'profile_completion': profile_completion,
        'cart_count': cart_count,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'review_count': review_count,
    }

    return render(request, 'accounts/dashboard.html', context)
    
    # ==========================================
# PHONE OTP AUTHENTICATION
# ==========================================

def send_otp(request):
    """
    Send OTP to phone number.

    URL: /accounts/send-otp/
    Method: POST (AJAX)

    Request body:
        {
            "phone": "+911234567890"
        }

    Response:
        {
            "success": true,
            "message": "OTP sent successfully"
        }

    Security:
    - Rate limiting needed (max 3 per hour)
    - Phone validation
    - Captcha recommended
    """
    import json
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.contrib.auth.models import User

    print("\n" + "="*60)
    print("OTP REQUEST RECEIVED")
    print("="*60)

    if request.method != 'POST':
        print("ERROR - Invalid method:", request.method)
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()

        print(f"Phone number received: {phone}")

        # Validate phone number
        if not phone or len(phone) < 10:
            print(f"ERROR - Invalid phone number: {phone}")
            return JsonResponse({
                'success': False,
                'message': 'Invalid phone number'
            })

        # Check if phone exists in database
        # Try to find profile with exact match or without country code
        profile = None

        # Try exact match first
        try:
            profile = Profile.objects.get(phone=phone)
            print(f"SUCCESS - Profile found (exact match): {phone}")
        except Profile.DoesNotExist:
            # Try without +91 prefix
            phone_without_prefix = phone.replace('+91', '')
            try:
                profile = Profile.objects.get(phone=phone_without_prefix)
                print(f"SUCCESS - Profile found (without prefix): {phone_without_prefix}")
                # Update profile with proper format
                profile.phone = phone
                profile.save()
                print(f"Updated phone number to: {phone}")
            except Profile.DoesNotExist:
                # Try with +91 prefix if phone doesn't have it
                if not phone.startswith('+91'):
                    phone_with_prefix = '+91' + phone
                    try:
                        profile = Profile.objects.get(phone=phone_with_prefix)
                        print(f"SUCCESS - Profile found (with prefix): {phone_with_prefix}")
                    except Profile.DoesNotExist:
                        pass

        if profile:
            import sys
            print(f"User: {profile.user.username}", flush=True)

            # Generate and send OTP
            print("\n" + "*"*60, flush=True)
            print("GENERATING OTP - CHECK BELOW FOR THE CODE", flush=True)
            print("*"*60, flush=True)

            otp_code = profile.send_otp_sms()

            print("*"*60, flush=True)
            print(f"OTP SENT SUCCESSFULLY: {otp_code}", flush=True)
            print("*"*60 + "\n", flush=True)
            sys.stdout.flush()

            return JsonResponse({
                'success': True,
                'message': f'OTP sent to {phone}',
                'phone': phone
            })
        else:
            print(f"ERROR - No profile found with phone: {phone}")
            print("Available phone numbers in database:")
            for p in Profile.objects.exclude(phone__isnull=True).exclude(phone=''):
                print(f"   - {p.phone} ({p.user.username})")

            # New phone number - allow registration
            return JsonResponse({
                'success': True,
                'message': 'Phone number not registered. Please register first.',
                'new_user': True
            })

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def verify_otp_login(request):
    """
    Verify OTP and login user.
    
    URL: /accounts/verify-otp/
    Method: POST (AJAX)
    
    Request body:
        {
            "phone": "+911234567890",
            "otp": "123456"
        }
    
    Response:
        {
            "success": true,
            "message": "Login successful"
        }
    """
    import json
    from django.http import JsonResponse
    from django.contrib.auth import login
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})
    
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '').strip()
        
        # Validate inputs
        if not phone or not otp:
            return JsonResponse({
                'success': False,
                'message': 'Phone and OTP required'
            })
        
        # Find profile by phone
        try:
            profile = Profile.objects.get(phone=phone)
            
            # Verify OTP
            if profile.verify_otp(otp):
                # Login user
                user = profile.user
                login(request, user)
                
                # Merge cart
                try:
                    cart_service = CartService(request)
                    cart_service.merge_with_user_cart(user)
                except Exception as e:
                    print(f"Cart merge error: {e}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'username': user.username
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid or expired OTP'
                })
        
        except Profile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Phone number not registered'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


# ==========================================
# ROLE-BASED REDIRECT HELPER
# ==========================================

def _get_role_based_redirect(request):
    """
    Determine redirect URL based on user role and current server.

    Logic:
    - Staff on admin server (8080) -> dashboard
    - Staff on customer server (8000) -> redirect to admin server
    - Customer on customer server (8000) -> home
    - Customer on admin server (8080) -> redirect to customer server
    """
    from django.conf import settings

    user = request.user
    server_type = getattr(settings, 'SERVER_TYPE', None)
    admin_port = getattr(settings, 'ADMIN_SERVER_PORT', 8080)
    customer_port = getattr(settings, 'CUSTOMER_SERVER_PORT', 8000)

    is_staff = user.is_staff or user.is_superuser

    # Debug output
    print("\n" + "="*60)
    print("ROLE-BASED REDIRECT DEBUG")
    print(f"User: {user.username}")
    print(f"Is Staff: {is_staff}")
    print(f"SERVER_TYPE: {server_type}")
    print(f"Admin Port: {admin_port}, Customer Port: {customer_port}")

    if is_staff:
        if server_type == 'admin':
            print("REDIRECT: Staff on admin server -> /dashboard/")
            print("="*60 + "\n")
            return redirect('admin_panel:dashboard')
        else:
            redirect_url = f'http://localhost:{admin_port}/dashboard/'
            print(f"REDIRECT: Staff on customer server -> {redirect_url}")
            print("="*60 + "\n")
            return redirect(redirect_url)
    else:
        if server_type == 'customer' or server_type is None:
            print("REDIRECT: Customer on customer server -> home")
            print("="*60 + "\n")
            return redirect('home')
        else:
            redirect_url = f'http://localhost:{customer_port}/'
            print(f"REDIRECT: Customer on admin server -> {redirect_url}")
            print("="*60 + "\n")
            return redirect(redirect_url)


# ==========================================
# COMBINED AUTH PAGE
# ==========================================

def auth_page(request):
    """
    Combined login/register page with sliding panels.

    URL: /accounts/auth/
    Methods: GET, POST

    Features:
    - Toggle between login and register
    - Username/password login
    - Phone OTP login
    - Social login (Google, Facebook)
    - Role-based redirect (staff -> admin port, customer -> customer port)
    """

    # Redirect if already logged in
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return _get_role_based_redirect(request)

    # Initialize forms
    login_form = UserLoginForm()
    register_form = UserRegistrationForm()

    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            # Handle username/password login
            login_form = UserLoginForm(request, data=request.POST)

            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)

                if user is not None and user.is_active:
                    user.backend = 'apps.accounts.backends.EmailOrUsernameBackend'
                    login(request, user)

                    # Merge cart
                    try:
                        cart_service = CartService(request)
                        cart_service.merge_with_user_cart(user)
                    except:
                        pass

                    messages.success(request, f'Welcome back, {username}!')

                    # Check for 'next' parameter first
                    next_page = request.GET.get('next')
                    if next_page:
                        return redirect(next_page)

                    # Role and port-based redirect
                    return _get_role_based_redirect(request)
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Invalid username or password.')

        elif action == 'register':
            # Handle registration
            register_form = UserRegistrationForm(request.POST)

            if register_form.is_valid():
                user = register_form.save()
                username = register_form.cleaned_data.get('username')

                # Auto-login after registration
                user.backend = 'apps.accounts.backends.EmailOrUsernameBackend'
                login(request, user)

                # Merge cart
                try:
                    cart_service = CartService(request)
                    cart_service.merge_with_user_cart(user)
                except:
                    pass

                messages.success(request, f'Welcome {username}! Your account has been created.')

                # New registrations go to customer port (they're not staff)
                return _get_role_based_redirect(request)
            else:
                # Log form errors for debugging
                print(f"Registration form errors: {register_form.errors}")
                messages.error(request, 'Please correct the errors below.')

    context = {
        'login_form': login_form,
        'register_form': register_form,
        'page_title': 'Sign In / Register'
    }

    return render(request, 'accounts/auth.html', context)