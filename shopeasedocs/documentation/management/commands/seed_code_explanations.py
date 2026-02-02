"""
Management command to seed CodeExplanation entries with deep,
educational line-by-line explanations of the ShopEase codebase.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documentation.models import CodeExplanation


EXPLANATIONS = [
    # ===== 1. USER REGISTRATION FLOW =====
    {
        'title': 'User Registration Flow - Complete Authentication',
        'slug': 'user-registration-flow',
        'description': 'Deep dive into how ShopEase registers new users, hashes passwords, creates profiles via signals, auto-logs in, and merges anonymous cart items.',
        'module': 'ACCOUNTS',
        'file_path': 'shopease/apps/accounts/views.py',
        'line_numbers': '52-155',
        'complexity': 'intermediate',
        'code_snippet': '''def register(request):
    # If user already logged in, redirect to home
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            # Create user (password is automatically hashed)
            # Django uses PBKDF2 algorithm with SHA256 hash
            user = form.save()

            # Profile is automatically created via signal
            # See models.py: @receiver(post_save, sender=User)

            username = form.cleaned_data.get('username')

            # Log user in automatically after registration
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # Merge anonymous cart with user's cart
            try:
                cart_service = CartService(request)
                cart_service.merge_carts()
            except Exception:
                pass

            messages.success(request, f'Welcome {username}! Account created.')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/auth.html', {'form': form})''',
        'detailed_explanation': '''This view handles the complete user registration flow in ShopEase. It demonstrates several key Django patterns:

**1. Authentication Check (Guard Clause)**
The first thing the view does is check if the user is already logged in using `request.user.is_authenticated`. This is a guard clause pattern - it prevents unnecessary processing and provides immediate feedback.

**2. GET vs POST Pattern**
Django views commonly handle both GET (display form) and POST (process form) in the same function. GET renders the empty form, POST validates and processes it.

**3. Password Security**
When `form.save()` is called, Django automatically hashes the password using PBKDF2 with SHA256. The hash includes a random salt, making rainbow table attacks impossible. The raw password is NEVER stored.

**4. Signal-Based Profile Creation**
The Profile model is created automatically by a Django signal (`post_save` on User). This is the Observer pattern - the registration view doesn't need to know about Profile creation.

**5. Explicit Backend Assignment**
`user.backend = 'django.contrib.auth.backends.ModelBackend'` is required because Django supports multiple authentication backends. Without this, `login()` wouldn't know which backend authenticated the user.

**6. Cart Merging**
Anonymous users can add items to cart (stored by session). After registration, `merge_carts()` transfers those items to the user's permanent cart. The try/except ensures registration succeeds even if cart merge fails.''',
        'why_it_matters': 'Registration is the entry point for user accounts. Understanding this flow teaches you about Django forms, password security, signals, session management, and the GET/POST pattern that appears in almost every Django view.',
        'line_by_line_explanation': {
            "1": "Define the register view function. Takes `request` - an HttpRequest object containing all HTTP data (headers, body, user, session).",
            "2": "Guard clause: Check if user is already authenticated. `request.user` is set by AuthenticationMiddleware from the session cookie.",
            "3": "Show info message using Django's messages framework. Messages are stored in session and displayed once on next page load.",
            "4": "Redirect to home page. `redirect('home')` uses the URL name from urls.py to generate the URL.",
            "6": "Check HTTP method. GET = show empty form, POST = process submitted form data.",
            "7": "Bind POST data to the form. This populates form fields with submitted values for validation.",
            "9": "Validate ALL form fields: username uniqueness, email format, password strength, password confirmation match.",
            "11": "Save the form which creates a User object. Django automatically hashes the password using PBKDF2+SHA256 with a random salt.",
            "14": "Profile creation happens automatically here via Django's post_save signal on the User model.",
            "16": "Extract the cleaned (validated & sanitized) username from the form data.",
            "19": "Set the authentication backend explicitly. Required because Django supports multiple auth backends.",
            "20": "Log the user in: creates a session record in the database, sets the session cookie on the response.",
            "23": "Initialize CartService which finds or creates a cart for this request (now authenticated user).",
            "24": "Merge anonymous session cart items into the user's permanent cart. Items added before registration are preserved.",
            "29": "Show success message and redirect to homepage. The PRG pattern (Post-Redirect-Get) prevents duplicate form submissions.",
            "31": "GET request: create an empty, unbound form for display.",
            "33": "Render the template with the form context. Works for both empty forms (GET) and forms with errors (invalid POST)."
        },
        'execution_flow': [
            {"step": 1, "description": "Browser sends GET request to /accounts/register/"},
            {"step": 2, "description": "Django middleware checks session cookie, sets request.user (AnonymousUser)"},
            {"step": 3, "description": "View creates empty UserRegistrationForm, renders auth.html template"},
            {"step": 4, "description": "User fills form, clicks Submit → POST request with CSRF token"},
            {"step": 5, "description": "Django CSRF middleware validates token (prevents cross-site attacks)"},
            {"step": 6, "description": "Form validates: username unique, email valid, password strong enough"},
            {"step": 7, "description": "form.save() → INSERT INTO auth_user (password stored as hash, never plaintext)"},
            {"step": 8, "description": "Django post_save signal fires → Profile object auto-created"},
            {"step": 9, "description": "login() → creates session in DB, sets sessionid cookie"},
            {"step": 10, "description": "CartService merges anonymous cart items → user's cart"},
            {"step": 11, "description": "302 Redirect to homepage → browser makes GET request (PRG pattern)"}
        ],
        'visual_diagram': '''graph TD
    A[GET /register/] --> B{User authenticated?}
    B -->|Yes| C[Redirect to Home]
    B -->|No| D[Show Registration Form]
    D --> E[User submits POST]
    E --> F{Form valid?}
    F -->|No| G[Show form with errors]
    F -->|Yes| H[form.save - Create User]
    H --> I[Signal: Create Profile]
    I --> J[login - Create Session]
    J --> K[Merge Anonymous Cart]
    K --> L[Redirect to Home]
    style H fill:#28a745,color:#fff
    style J fill:#667eea,color:#fff
    style K fill:#ffc107,color:#000''',
        'learning_objectives': '1. Understand Django view GET/POST pattern\n2. Learn how password hashing works (PBKDF2+SHA256)\n3. Understand Django signals (post_save)\n4. Learn session-based authentication\n5. Understand cart merging for anonymous users',
        'prerequisites': 'Basic Python, HTTP methods (GET/POST), HTML forms',
        'related_concepts': 'Django Forms, CSRF Protection, Session Management, Password Hashing, Signals',
        'common_mistakes': '1. Forgetting to set user.backend before login() - causes ValueError\n2. Storing raw passwords instead of hashing - CRITICAL security flaw\n3. Not handling cart merge failures - could break registration\n4. Missing CSRF token in template - causes 403 Forbidden',
        'practice_exercises': '1. Add email verification: send confirmation link before activating account\n2. Add rate limiting: max 3 registrations per IP per hour\n3. Add password strength meter on the frontend\n4. Add social login (Google OAuth)',
        'time_complexity': 'O(1)',
        'space_complexity': 'O(1)',
        'estimated_learning_time': 25,
    },

    # ===== 2. CART SYSTEM =====
    {
        'title': 'Shopping Cart - get_or_create Pattern',
        'slug': 'cart-get-or-create-pattern',
        'description': 'How ShopEase handles shopping carts for both authenticated users and anonymous visitors using Django sessions and the get_or_create pattern.',
        'module': 'CART',
        'file_path': 'shopease/apps/cart/views.py',
        'line_numbers': '33-45',
        'complexity': 'beginner',
        'code_snippet': '''def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()

        # IMPORTANT: Force the session to persist
        request.session.modified = True

        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart''',
        'detailed_explanation': '''This function is the foundation of ShopEase's cart system. It solves a critical e-commerce problem: how do you maintain a shopping cart for users who haven't logged in yet?

**The Two-Path Strategy:**

**Path 1 - Authenticated Users:**
For logged-in users, the cart is linked to their User object via a ForeignKey. `get_or_create()` either finds their existing cart or creates a new one. This cart persists across sessions and devices.

**Path 2 - Anonymous Users:**
For visitors who haven't logged in, the cart is linked to their session key. Django sessions use a cookie (`sessionid`) to identify the browser. The session key is a random string like `abc123def456`.

**Why `request.session.create()`?**
Django uses lazy session creation - it doesn't create a session until you write to it. Without `session.create()`, anonymous users would have no session key, and we couldn't store their cart.

**Why `request.session.modified = True`?**
This forces Django to save the session to the database. Without it, the session might not persist, and the cart would be lost on the next page load.

**The get_or_create() Pattern:**
This is an atomic Django ORM method that either:
- Gets the existing record matching the lookup fields, OR
- Creates a new record if none exists
It returns a tuple: (object, created_boolean). This prevents race conditions where two requests might try to create duplicate carts.''',
        'why_it_matters': 'Every e-commerce site needs to handle shopping carts for both logged-in and anonymous users. This pattern appears in many real-world Django projects.',
        'line_by_line_explanation': {
            "1": "Define helper function that takes the Django request object.",
            "2": "Check if user is logged in. `is_authenticated` is a property on User model (True) or AnonymousUser (False).",
            "3": "For logged-in users: get existing cart or create new one, linked to user via ForeignKey. Returns (cart, created_bool).",
            "4": "Else branch: handle anonymous visitors (not logged in).",
            "5": "Check if session exists. Django uses lazy sessions - no session until data is written.",
            "6": "Force create a session. Generates a random session_key and saves to django_session table.",
            "8": "Force Django to save session changes. Without this, the session cookie might not be set.",
            "10": "Get the session key string (e.g., 'abc123def456'). This identifies the browser.",
            "11": "For anonymous users: get/create cart linked to session_key instead of user.",
            "12": "Return the cart object (either found or newly created)."
        },
        'execution_flow': [
            {"step": 1, "description": "Request arrives at any cart endpoint (add, view, update)"},
            {"step": 2, "description": "get_or_create_cart() called to find/create the user's cart"},
            {"step": 3, "description": "Check request.user.is_authenticated (set by AuthenticationMiddleware)"},
            {"step": 4, "description": "IF authenticated: SELECT * FROM cart WHERE user_id=X (or INSERT)"},
            {"step": 5, "description": "IF anonymous: ensure session exists, then SELECT/INSERT by session_key"},
            {"step": 6, "description": "Return Cart object for use in the calling view"}
        ],
        'visual_diagram': '''graph TD
    A[Request arrives] --> B{User authenticated?}
    B -->|Yes| C[get_or_create by user_id]
    B -->|No| D{Session exists?}
    D -->|No| E[Create session]
    E --> F[Set session.modified = True]
    D -->|Yes| F
    F --> G[get_or_create by session_key]
    C --> H[Return Cart]
    G --> H
    style C fill:#28a745,color:#fff
    style G fill:#ffc107,color:#000''',
        'learning_objectives': '1. Understand get_or_create() pattern\n2. Learn Django session management\n3. Understand authenticated vs anonymous user handling\n4. Learn lazy session creation',
        'prerequisites': 'Django ORM basics, HTTP sessions and cookies',
        'related_concepts': 'Django Sessions, ORM get_or_create, Anonymous Users, Cookies',
        'common_mistakes': '1. Forgetting session.create() - anonymous cart disappears\n2. Forgetting session.modified = True - session not persisted\n3. Not handling the created boolean from get_or_create\n4. Using session_key before creating the session',
        'practice_exercises': '1. Add a "cart count" badge to the navbar using this function\n2. Implement cart expiry (delete carts older than 30 days)\n3. Add cart merging when anonymous user logs in',
        'time_complexity': 'O(1)',
        'space_complexity': 'O(1)',
        'estimated_learning_time': 15,
    },

    # ===== 3. ADMIN ROLE-BASED ACCESS CONTROL =====
    {
        'title': 'Role-Based Access Control (RBAC) - Permission Decorator',
        'slug': 'rbac-permission-decorator',
        'description': 'How ShopEase implements role-based access control using custom decorators to protect admin views based on AdminRole permissions.',
        'module': 'ADMIN_PANEL',
        'file_path': 'shopease/apps/admin_panel/decorators.py',
        'line_numbers': '1-50',
        'complexity': 'advanced',
        'code_snippet': '''from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access admin panel.')
            return redirect('accounts:auth_page')
        if not request.user.is_staff:
            messages.error(request, 'Admin access required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_required(*permissions):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            try:
                admin_role = request.user.admin_role
                for perm in permissions:
                    if not getattr(admin_role, perm, False):
                        raise PermissionDenied
            except Exception:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator''',
        'detailed_explanation': '''This code implements Role-Based Access Control (RBAC) - a fundamental security pattern used in every enterprise application.

**Decorator Pattern in Python:**
Decorators are functions that wrap other functions to add behavior. When you write `@admin_required` above a view, Python calls `admin_required(view_func)` and replaces the view with the returned wrapper.

**@wraps Preserves Function Metadata:**
`@wraps(view_func)` copies the original function's name, docstring, and attributes to the wrapper. Without it, debugging becomes difficult because every decorated function would appear as "wrapper".

**Two-Layer Security:**

**Layer 1 - `admin_required`:**
Basic staff check. Uses `is_staff` (a boolean field on Django's User model). Non-staff users are redirected with a friendly message.

**Layer 2 - `permission_required`:**
Granular permission check. This is a decorator FACTORY - it takes permission names as arguments and RETURNS a decorator. The inner function checks each permission on the user's AdminRole model.

**Superuser Bypass:**
`request.user.is_superuser` gets full access without permission checks. This follows the principle that superusers are omnipotent.

**getattr() for Dynamic Permission Checking:**
`getattr(admin_role, perm, False)` dynamically accesses the permission field by name. If the AdminRole has `can_view_orders = True`, then `getattr(admin_role, 'can_view_orders', False)` returns `True`. The third argument `False` is the default if the attribute doesn't exist.''',
        'why_it_matters': 'RBAC is used in every business application. Understanding decorators and permission systems is essential for building secure Django applications.',
        'line_by_line_explanation': {
            "1": "Import wraps from functools - preserves the wrapped function's metadata (name, docstring).",
            "5": "Define admin_required decorator. Takes the view function as argument.",
            "6": "@wraps copies view_func's __name__, __doc__ to wrapper. Critical for debugging.",
            "7": "wrapper receives all the same arguments as the original view (request, *args, **kwargs).",
            "8": "First check: is the user logged in? request.user is AnonymousUser if not.",
            "10": "Second check: is the user staff? is_staff is a boolean field on Django's User model.",
            "12": "All checks passed - call the original view function with all arguments.",
            "13": "Return the wrapper function. Python will replace the view with this wrapper.",
            "15": "Decorator FACTORY: takes permission names as *args (variable arguments).",
            "16": "Inner decorator: receives the view function.",
            "18": "The actual wrapper function that runs on each request.",
            "19": "Superuser bypass: superusers always have ALL permissions.",
            "20": "Call original view immediately for superusers - no further checks needed.",
            "22": "Access the user's AdminRole object (OneToOne relationship with User).",
            "23": "Loop through required permissions (e.g., 'can_view_orders', 'can_edit_orders').",
            "24": "getattr dynamically gets the permission boolean. False = permission denied.",
            "25": "Raise PermissionDenied - Django returns a 403 Forbidden response.",
            "27": "If no AdminRole exists (AttributeError), deny access.",
            "29": "All permission checks passed - call original view."
        },
        'execution_flow': [
            {"step": 1, "description": "Request hits view decorated with @admin_required @permission_required('can_view_orders')"},
            {"step": 2, "description": "admin_required runs first: checks is_authenticated and is_staff"},
            {"step": 3, "description": "permission_required runs: checks if superuser (bypass all)"},
            {"step": 4, "description": "If not superuser: loads AdminRole from user.admin_role"},
            {"step": 5, "description": "Loops through each required permission, checks getattr()"},
            {"step": 6, "description": "All checks pass → original view executes"}
        ],
        'visual_diagram': '''graph TD
    A[Request] --> B{Authenticated?}
    B -->|No| C[Redirect to Login]
    B -->|Yes| D{is_staff?}
    D -->|No| E[Redirect to Home]
    D -->|Yes| F{is_superuser?}
    F -->|Yes| G[Execute View - Full Access]
    F -->|No| H{Has AdminRole?}
    H -->|No| I[403 Forbidden]
    H -->|Yes| J{All permissions granted?}
    J -->|No| I
    J -->|Yes| G
    style G fill:#28a745,color:#fff
    style I fill:#dc3545,color:#fff
    style C fill:#ffc107,color:#000''',
        'learning_objectives': '1. Understand Python decorators and decorator factories\n2. Learn @wraps and why it matters\n3. Understand RBAC (Role-Based Access Control)\n4. Learn Django permission patterns\n5. Understand getattr() for dynamic attribute access',
        'prerequisites': 'Python functions, closures, Django authentication',
        'related_concepts': 'Decorators, Closures, RBAC, Django Auth, PermissionDenied',
        'common_mistakes': '1. Forgetting @wraps - breaks debugging and Django URL resolution\n2. Not checking is_authenticated before is_staff - causes AttributeError\n3. Wrong decorator order - @admin_required should come before @permission_required\n4. Hardcoding permissions instead of using getattr',
        'practice_exercises': '1. Create a @role_required decorator that checks role names\n2. Add logging to track permission denials\n3. Create a permission cache to avoid repeated DB queries\n4. Add a "reason" parameter to show custom denial messages',
        'time_complexity': 'O(p) where p = number of permissions to check',
        'space_complexity': 'O(1)',
        'estimated_learning_time': 30,
    },

    # ===== 4. DJANGO SIGNALS - AUTO PROFILE CREATION =====
    {
        'title': 'Django Signals - Auto Profile Creation on User Registration',
        'slug': 'django-signals-profile-creation',
        'description': 'How ShopEase uses Django post_save signal to automatically create a Profile whenever a new User is registered. The Observer pattern in Django.',
        'module': 'ACCOUNTS',
        'file_path': 'shopease/apps/accounts/models.py',
        'line_numbers': '1-40',
        'complexity': 'intermediate',
        'code_snippet': '''from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)''',
        'detailed_explanation': '''This demonstrates the Observer Pattern implemented via Django Signals. Signals allow decoupled applications to notify each other when certain actions occur.

**What is `post_save`?**
Django sends the `post_save` signal after a model's `save()` method is called. The signal includes: the sender (model class), instance (the object saved), and `created` (True if new, False if updated).

**@receiver Decorator:**
Connects a function to a signal. `@receiver(post_save, sender=User)` means "call this function every time a User object is saved."

**Two Signal Handlers - Why?**

**Handler 1 - `create_user_profile`:**
Only runs when a NEW user is created (`if created:`). Creates the Profile object linked to the User via OneToOneField.

**Handler 2 - `save_user_profile`:**
Runs on EVERY User save (create and update). Ensures the Profile stays in sync. The try/except handles edge cases where Profile might not exist.

**OneToOneField:**
`user = models.OneToOneField(User, on_delete=models.CASCADE)` creates a 1:1 relationship. Each User has exactly one Profile, and deleting a User cascades to delete their Profile.

**Why Signals Instead of Direct Creation?**
Signals decouple the code. The registration view doesn't need to know about Profile creation. If you add more models (e.g., UserPreferences), you just add another signal handler - no changes to the registration view.''',
        'why_it_matters': 'Signals are the backbone of Django event handling. They enable loose coupling between apps - a fundamental software engineering principle.',
        'line_by_line_explanation': {
            "1": "Import models module for defining database models.",
            "2": "Import Django's built-in User model (username, email, password, is_staff, etc.).",
            "3": "Import post_save signal - fired after any model's save() method completes.",
            "4": "Import @receiver decorator - connects functions to signals.",
            "6": "Define Profile model extending the User with additional fields.",
            "7": "OneToOneField: each User has exactly ONE Profile. CASCADE = delete Profile when User is deleted.",
            "8": "Phone field: optional (blank=True). max_length=15 covers international formats (+1-555-555-5555).",
            "9": "Boolean flag for phone verification. Default False - not verified until OTP confirmed.",
            "10": "OTP code storage. null=True allows NULL in DB (no OTP generated yet).",
            "11": "Avatar image upload. Files stored in MEDIA_ROOT/avatars/ directory.",
            "13": "String representation for admin panel and debugging.",
            "16": "@receiver connects this function to post_save signal for User model only.",
            "17": "Signal handler parameters: sender=User class, instance=the saved user, created=True if new record.",
            "18": "Only create Profile for NEW users, not when existing users update their data.",
            "19": "Create Profile row in DB linked to the new User via OneToOneField.",
            "21": "Second signal handler: runs on every User save (create AND update).",
            "23": "Try to save the existing profile (keeps it in sync with User changes).",
            "25": "If Profile doesn't exist (edge case), create one. Defensive programming."
        },
        'execution_flow': [
            {"step": 1, "description": "User.objects.create_user() or form.save() is called"},
            {"step": 2, "description": "Django's Model.save() method executes INSERT INTO auth_user"},
            {"step": 3, "description": "Django sends post_save signal with created=True"},
            {"step": 4, "description": "create_user_profile() receives signal, checks created=True"},
            {"step": 5, "description": "Profile.objects.create(user=instance) → INSERT INTO accounts_profile"},
            {"step": 6, "description": "save_user_profile() receives signal, calls instance.profile.save()"},
            {"step": 7, "description": "Both User and Profile now exist in the database"}
        ],
        'visual_diagram': '''graph TD
    A[User.save called] --> B[INSERT INTO auth_user]
    B --> C[Django sends post_save signal]
    C --> D[create_user_profile]
    C --> E[save_user_profile]
    D --> F{created=True?}
    F -->|Yes| G[Create Profile]
    F -->|No| H[Skip]
    E --> I[Save existing Profile]
    style G fill:#28a745,color:#fff
    style C fill:#667eea,color:#fff''',
        'learning_objectives': '1. Understand Django signals (post_save)\n2. Learn the Observer pattern\n3. Understand OneToOneField relationships\n4. Learn signal handler best practices',
        'prerequisites': 'Django models, database relationships',
        'related_concepts': 'Observer Pattern, Django Signals, OneToOneField, CASCADE',
        'common_mistakes': '1. Creating Profile in registration view AND signal = duplicate\n2. Forgetting created check = Profile recreated on every save\n3. Circular signal handlers = infinite loop\n4. Not handling DoesNotExist in save handler',
        'practice_exercises': '1. Add a post_save signal that sends a welcome email\n2. Add a pre_save signal that validates phone format\n3. Create a signal that logs user activity to MongoDB',
        'time_complexity': 'O(1)',
        'space_complexity': 'O(1)',
        'estimated_learning_time': 20,
    },

    # ===== 5. ORDER PROCESSING FLOW =====
    {
        'title': 'Order Processing - From Cart to Confirmed Order',
        'slug': 'order-processing-flow',
        'description': 'The complete order processing flow: validating cart items, creating the order, reducing stock, clearing the cart, and sending confirmation.',
        'module': 'ORDERS',
        'file_path': 'shopease/apps/orders/views.py',
        'line_numbers': '1-80',
        'complexity': 'advanced',
        'code_snippet': '''@login_required
def place_order(request):
    cart_service = CartService(request)
    cart_data = cart_service.get_cart_data()

    if not cart_data['items']:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_view')

    if request.method == 'POST':
        # Create the order
        order = Order.objects.create(
            user=request.user,
            subtotal=cart_data['subtotal'],
            tax=cart_data['tax'],
            total=cart_data['total'],
            status='PENDING',
        )

        # Create order items and reduce stock
        for item in cart_data['items']:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price,
            )
            # Reduce product stock
            product = item['product']
            product.stock -= item['quantity']
            product.save()

        # Clear the cart
        cart_service.clear()

        messages.success(request, f'Order #{order.id} placed!')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart_data': cart_data
    })''',
        'detailed_explanation': '''This view demonstrates a complete e-commerce transaction flow. It involves multiple database operations that must all succeed together.

**@login_required Decorator:**
Ensures only authenticated users can place orders. Anonymous users are redirected to the login page with a `?next=` parameter so they return here after logging in.

**Cart Validation:**
Before processing, we verify the cart isn't empty. This prevents empty orders and handles edge cases (user opens checkout in two tabs, places order in one, tries again in the other).

**Order Creation:**
`Order.objects.create()` performs an INSERT with all order details. The status starts as PENDING - it will change to CONFIRMED after payment processing.

**Order Items Loop:**
Each cart item becomes an OrderItem record. We store the price at time of purchase (not a reference to the current price) because product prices can change.

**Stock Reduction:**
`product.stock -= item['quantity']` reduces inventory. In production, this should use `F()` expressions for atomicity: `Product.objects.filter(pk=product.pk).update(stock=F('stock') - quantity)`.

**Cart Clearing:**
After successful order creation, the cart is emptied. This prevents double-ordering.

**Note:** In production, this entire process should be wrapped in `@transaction.atomic` to ensure all-or-nothing execution.''',
        'why_it_matters': 'Order processing is the core business logic of any e-commerce platform. It teaches database transactions, stock management, and multi-step business workflows.',
        'line_by_line_explanation': {
            "1": "@login_required ensures only logged-in users can access. Redirects to login with ?next= URL.",
            "3": "Initialize CartService to access the user's cart data.",
            "4": "Get all cart items with calculated subtotal, tax, and total.",
            "6": "Guard clause: prevent placing an order with an empty cart.",
            "10": "POST means user clicked 'Place Order' button.",
            "12": "Create Order record in database. Status starts as PENDING.",
            "21": "Loop through each cart item to create OrderItem records.",
            "22": "Create OrderItem linking this order to a product with quantity and price snapshot.",
            "28": "Reduce product stock. WARNING: not atomic - should use F() in production.",
            "29": "Save the updated product stock to database.",
            "32": "Clear all items from the cart after successful order.",
            "34": "Success message and redirect to order detail page (PRG pattern).",
            "37": "GET request: show checkout page with cart summary."
        },
        'execution_flow': [
            {"step": 1, "description": "User clicks 'Place Order' → POST to /orders/place/"},
            {"step": 2, "description": "@login_required verifies user is authenticated"},
            {"step": 3, "description": "CartService loads cart items from database"},
            {"step": 4, "description": "Validate cart is not empty"},
            {"step": 5, "description": "INSERT INTO orders (user, subtotal, tax, total, status=PENDING)"},
            {"step": 6, "description": "FOR each cart item: INSERT INTO order_items + UPDATE product stock"},
            {"step": 7, "description": "DELETE all cart items (cart.clear())"},
            {"step": 8, "description": "Redirect to order confirmation page"}
        ],
        'visual_diagram': '''graph TD
    A[POST /orders/place/] --> B{User logged in?}
    B -->|No| C[Redirect to Login]
    B -->|Yes| D{Cart empty?}
    D -->|Yes| E[Error: Cart empty]
    D -->|No| F[Create Order record]
    F --> G[Loop: Create OrderItems]
    G --> H[Reduce product stock]
    H --> I[Clear cart]
    I --> J[Redirect to Order Detail]
    style F fill:#28a745,color:#fff
    style H fill:#ffc107,color:#000
    style I fill:#dc3545,color:#fff''',
        'learning_objectives': '1. Understand multi-step database operations\n2. Learn stock management patterns\n3. Understand the importance of database transactions\n4. Learn the checkout flow architecture',
        'prerequisites': 'Django ORM, HTTP POST, login_required decorator',
        'related_concepts': 'Database Transactions, Atomic Operations, F() Expressions, PRG Pattern',
        'common_mistakes': '1. Not wrapping in transaction.atomic - partial orders on failure\n2. Using product.price from model instead of snapshot - price changes break history\n3. Not checking stock before reducing - negative stock\n4. Forgetting to clear cart - duplicate orders',
        'practice_exercises': '1. Wrap the entire flow in @transaction.atomic\n2. Add stock validation before order (check sufficient quantity)\n3. Use F() expression for atomic stock reduction\n4. Add Celery task for sending order confirmation email',
        'time_complexity': 'O(n) where n = number of cart items',
        'space_complexity': 'O(n)',
        'estimated_learning_time': 30,
    },
]


class Command(BaseCommand):
    help = 'Seed CodeExplanation entries with deep educational content about ShopEase'

    def handle(self, *args, **options):
        # Get or create a superuser as author
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            self.stdout.write(self.style.ERROR('No superuser found. Create one first: python manage.py createsuperuser'))
            return

        created_count = 0
        updated_count = 0

        for data in EXPLANATIONS:
            obj, created = CodeExplanation.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'module': data['module'],
                    'file_path': data['file_path'],
                    'line_numbers': data.get('line_numbers', ''),
                    'complexity': data['complexity'],
                    'code_snippet': data['code_snippet'],
                    'detailed_explanation': data['detailed_explanation'],
                    'why_it_matters': data.get('why_it_matters', ''),
                    'line_by_line_explanation': data.get('line_by_line_explanation', {}),
                    'execution_flow': data.get('execution_flow', []),
                    'visual_diagram': data.get('visual_diagram', ''),
                    'learning_objectives': data.get('learning_objectives', ''),
                    'prerequisites': data.get('prerequisites', ''),
                    'related_concepts': data.get('related_concepts', ''),
                    'common_mistakes': data.get('common_mistakes', ''),
                    'practice_exercises': data.get('practice_exercises', ''),
                    'time_complexity': data.get('time_complexity', ''),
                    'space_complexity': data.get('space_complexity', ''),
                    'estimated_learning_time': data.get('estimated_learning_time', 15),
                    'author': superuser,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {data["title"]}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  Updated: {data["title"]}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created: {created_count}, Updated: {updated_count}, Total: {len(EXPLANATIONS)}'
        ))
