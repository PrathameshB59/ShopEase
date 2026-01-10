"""
========================================
CART SERVICE - Business Logic Layer
========================================

This is a SERVICE LAYER that sits between views and models.

Why a separate service class?
- Separates business logic from views (cleaner code)
- Reusable across views, APIs, CLI commands
- Easier to test (mock service, not views)
- Follows Single Responsibility Principle

Architecture Pattern: Service Layer
View → Service → Model → Database

Real-world examples:
- Stripe: StripePaymentService
- AWS: S3StorageService  
- SendGrid: EmailService
"""

from decimal import Decimal
from django.conf import settings
from .models import Cart, CartItem
from apps.products.models import Product


class CartService:
    """
    Shopping cart service for session-based carts.
    
    Usage:
        cart = CartService(request)
        cart.add(product_id=5, quantity=2)
        total = cart.get_total()
    
    Security Features:
    - Price validation (fetches from DB, not frontend)
    - Stock validation (prevents overselling)
    - Session management (secure, HttpOnly cookies)
    """
    
    def __init__(self, request):
        """
        Initialize cart service for current request.
        
        Args:
            request: Django HttpRequest object
        
        How it works:
        1. Get or create session (Django handles this)
        2. Get or create cart (from session_key or user)
        3. Load cart items into memory (for fast access)
        
        Session lifecycle:
        - First visit: Django creates session, saves to DB
        - Returns: Session key stored in cookie
        - Future visits: Cookie sent, session loaded
        """
        self.request = request
        self.session = request.session
        
        # Ensure session exists (creates if needed)
        # session.session_key is None until session is saved
        if not self.session.session_key:
            self.session.create()
        
        # Get or create cart
        self.cart = self._get_or_create_cart()
    
    def _get_or_create_cart(self):
        """
        Get existing cart or create new one.
        
        Logic:
        1. If logged in → Use user's cart
        2. If anonymous → Use session's cart
        3. If none exists → Create new cart
        
        Returns: Cart instance
        """
        session_key = self.session.session_key

        if self.request.user.is_authenticated:
            # Logged-in user: Get or create cart by user
            cart, created = Cart.objects.get_or_create(
                user=self.request.user,
                defaults={'session_key': session_key}
            )
        else:
            # Anonymous user: Get or create cart by session key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key
            )

        return cart
    
    # ==========================================
    # ADD TO CART
    # ==========================================
    
    def add(self, product_id, quantity=1):
        """
        Add product to cart.
        
        Args:
            product_id: Integer (product ID)
            quantity: Integer (how many to add)
        
        Returns:
            dict: {
                'success': Boolean,
                'message': String,
                'cart_total': Decimal,
                'cart_count': Integer,
                'item': CartItem or None
            }
        
        Security checks:
        1. Product exists and is active
        2. Product has enough stock
        3. Quantity is positive integer
        4. Price fetched from database (not frontend)
        
        Business rules:
        - If item exists: Update quantity
        - If new item: Create new CartItem
        - If quantity exceeds stock: Return error
        """
        try:
            # SECURITY: Fetch product from database
            # NEVER trust product data from frontend
            product = Product.objects.select_related('category').get(
                id=product_id,
                is_active=True  # Only active products
            )
        except Product.DoesNotExist:
            return {
                'success': False,
                'message': 'Product not found or unavailable',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # SECURITY: Validate quantity
        if quantity < 1:
            return {
                'success': False,
                'message': 'Quantity must be at least 1',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # Check stock availability
        existing_quantity = self.cart.get_item_count_by_product(product_id)
        new_total_quantity = existing_quantity + quantity
        
        if new_total_quantity > product.stock:
            return {
                'success': False,
                'message': f'Only {product.stock} items available. You have {existing_quantity} in cart.',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price_snapshot': product.get_display_price()  # Current price
            }
        )
        
        # If item already exists, update quantity
        if not created:
            cart_item.quantity = new_total_quantity
            cart_item.save()
            message = f'Updated {product.name} quantity to {new_total_quantity}'
        else:
            message = f'Added {product.name} to cart'
        
        return {
            'success': True,
            'message': message,
            'cart_total': self.get_total(),
            'cart_count': self.get_item_count(),
            'item': cart_item
        }
    
    # ==========================================
    # UPDATE CART
    # ==========================================
    
    def update(self, product_id, quantity):
        """
        Update quantity of item in cart.
        
        Args:
            product_id: Integer
            quantity: Integer (new quantity, not increment)
        
        Returns: dict (same structure as add())
        
        Special cases:
        - quantity = 0: Remove item
        - quantity > stock: Return error
        """
        try:
            cart_item = CartItem.objects.select_related('product').get(
                cart=self.cart,
                product_id=product_id
            )
        except CartItem.DoesNotExist:
            return {
                'success': False,
                'message': 'Item not in cart',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # Remove item if quantity is 0
        if quantity <= 0:
            product_name = cart_item.product.name
            cart_item.delete()
            return {
                'success': True,
                'message': f'Removed {product_name} from cart',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # Check stock
        if quantity > cart_item.product.stock:
            return {
                'success': False,
                'message': f'Only {cart_item.product.stock} items available',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        
        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        return {
            'success': True,
            'message': f'Updated {cart_item.product.name} quantity',
            'cart_total': self.get_total(),
            'cart_count': self.get_item_count(),
            'item': cart_item
        }
    
    # ==========================================
    # REMOVE FROM CART
    # ==========================================
    
    def remove(self, product_id):
        """
        Remove item from cart completely.
        
        Args:
            product_id: Integer
        
        Returns: dict
        """
        try:
            cart_item = CartItem.objects.get(
                cart=self.cart,
                product_id=product_id
            )
            product_name = cart_item.product.name
            cart_item.delete()
            
            return {
                'success': True,
                'message': f'Removed {product_name} from cart',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
        except CartItem.DoesNotExist:
            return {
                'success': False,
                'message': 'Item not in cart',
                'cart_total': self.get_total(),
                'cart_count': self.get_item_count()
            }
    
    # ==========================================
    # CLEAR CART
    # ==========================================
    
    def clear(self):
        """Remove all items from cart."""
        self.cart.clear()
        return {
            'success': True,
            'message': 'Cart cleared',
            'cart_total': Decimal('0.00'),
            'cart_count': 0
        }
    
    # ==========================================
    # GET CART DATA
    # ==========================================
    
    def get_items(self):
        """
        Get all items in cart with related data.
        
        Returns: QuerySet of CartItem
        
        Performance: Uses select_related to prevent N+1 queries
        """
        return self.cart.items.select_related(
            'product',
            'product__category'
        ).all()
    
    def get_item_count(self):
        """Total number of items (sum of quantities)."""
        return self.cart.get_total_items()
    
    def get_total(self):
        """Cart subtotal (before tax/shipping)."""
        return self.cart.get_subtotal()
    
    def get_cart_data(self):
        """
        Get complete cart data for template/API.
        
        Returns: dict with all cart information
        """
        items = self.get_items()
        
        return {
            'items': items,
            'item_count': self.get_item_count(),
            'subtotal': self.get_total(),
            'tax': self.cart.get_tax(),
            'total': self.cart.get_total(),
            'has_items': items.exists()
        }
    
    # ==========================================
    # CART MERGING (For Login)
    # ==========================================
    
    def merge_with_user_cart(self, user):
        """
        Merge anonymous cart with user's cart on login.
        
        Args:
            user: User instance
        
        Logic:
        1. Get user's existing cart (if any)
        2. Move items from session cart to user cart
        3. If item exists in both: Use max quantity
        4. Delete session cart
        
        Use case: User adds items while not logged in,
                 then logs in. Don't lose their cart!
        """
        # Get or create user's cart
        user_cart, created = Cart.objects.get_or_create(
            user=user,
            is_active=True
        )
        
        # If session cart has items, merge them
        session_cart_items = self.cart.items.all()
        
        for session_item in session_cart_items:
            # Check if user cart already has this product
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=session_item.product,
                defaults={
                    'quantity': session_item.quantity,
                    'price_snapshot': session_item.price_snapshot
                }
            )
            
            # If user already had this item, use higher quantity
            if not created:
                user_item.quantity = max(user_item.quantity, session_item.quantity)
                # Check stock limit
                if user_item.quantity > session_item.product.stock:
                    user_item.quantity = session_item.product.stock
                user_item.save()
        
        # Delete session cart
        self.cart.delete()
        
        # Update service to use user's cart
        self.cart = user_cart