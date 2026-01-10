"""
========================================
CART VIEWS - Shopping Cart Operations
========================================
Handles all cart functionality: view, add, update, remove items.

Security:
- CSRF protection on all POST requests
- User authentication checks
- Input validation
- SQL injection prevention via ORM
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json

from .models import Cart, CartItem
from apps.products.models import Product


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_or_create_cart(request):
    """
    Get or create cart for current user/session.
    
    Logic:
    - Logged in users: Get cart by user
    - Anonymous users: Get cart by session key
    - Creates new cart if doesn't exist
    
    Security:
    - Session key from Django (can't be forged)
    - User from Django auth (can't be forged)
    
    Returns: Cart object
    """
    if request.user.is_authenticated:
        # Logged in user - get cart by user
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Anonymous user - get cart by session
        # Ensure session exists (Django creates it)
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


def get_cart_data(cart):
    """
    Prepare cart data for JSON response.
    
    Used by AJAX endpoints to return cart info.
    
    Returns: Dictionary with cart stats
    """
    return {
        'count': cart.get_total_items(),
        'subtotal': str(cart.get_subtotal()),
        'tax': str(cart.get_tax()),
        'total': str(cart.get_total()),
    }


# ==========================================
# CART VIEW
# ==========================================

def cart_view(request):
    """
    Display shopping cart page.
    
    URL: /cart/
    Method: GET
    Template: cart/cart.html
    
    Context:
    - cart_items: QuerySet of CartItem objects
    - subtotal: Decimal
    - tax: Decimal  
    - total: Decimal
    """
    cart = get_or_create_cart(request)
    
    # Get all items in cart with product details
    # select_related('product'): Fetch product in same query (performance)
    cart_items = cart.items.select_related('product', 'product__category').all()
    
    context = {
        'cart_items': cart_items,
        'subtotal': cart.get_subtotal(),
        'tax': cart.get_tax(),
        'total': cart.get_total(),
        'cart_count': cart.get_total_items(),
    }
    
    return render(request, 'cart/cart.html', context)


# ==========================================
# ADD TO CART
# ==========================================

@require_POST
def add_to_cart(request):
    """
    Add product to cart.
    
    URL: /cart/add/
    Method: POST
    Content-Type: application/json
    
    Request Body:
    {
        "product_id": 123,
        "quantity": 1
    }
    
    Response:
    {
        "success": true,
        "message": "Product added to cart",
        "cart_count": 3,
        "cart_total": "149.97"
    }
    
    Security:
    - CSRF token required
    - Validates product exists
    - Validates quantity > 0
    - Validates quantity <= stock
    """
    try:
        # Parse JSON request body
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        # Validation: Check inputs
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID required'
            }, status=400)
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1'
            }, status=400)
        
        # Get product (404 if not found)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check stock availability
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Only {product.stock} items available'
            }, status=400)
        
        # Get or create cart
        cart = get_or_create_cart(request)
        
        # Check if product already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item exists - increase quantity
            new_quantity = cart_item.quantity + quantity
            
            # Check stock for new quantity
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot add more. Only {product.stock} available.'
                }, status=400)
            
            cart_item.quantity = new_quantity
            cart_item.save()
            message = f'Updated {product.name} quantity to {new_quantity}'
        else:
            # New item added
            message = f'{product.name} added to cart'
        
        # Return success with cart data
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_data': get_cart_data(cart)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ==========================================
# UPDATE CART ITEM QUANTITY
# ==========================================

@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity.
    
    URL: /cart/update/<item_id>/
    Method: POST
    Content-Type: application/json
    
    Request Body:
    {
        "quantity": 3
    }
    
    Response:
    {
        "success": true,
        "message": "Quantity updated",
        "item_subtotal": "59.97",
        "cart_data": {...}
    }
    
    Security:
    - CSRF token required
    - Validates item belongs to user's cart
    - Validates quantity > 0 and <= stock
    """
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        # Get cart for current user/session
        cart = get_or_create_cart(request)
        
        # Get cart item (must belong to user's cart)
        # Security: cart=cart ensures user can only update their items
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Validation: Quantity must be between 1 and stock
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1'
            }, status=400)
        
        if quantity > cart_item.product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Only {cart_item.product.stock} available'
            }, status=400)
        
        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Quantity updated',
            'item_subtotal': str(cart_item.get_subtotal()),
            'cart_data': get_cart_data(cart)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ==========================================
# REMOVE FROM CART
# ==========================================

@require_POST
def remove_from_cart(request, item_id):
    """
    Remove item from cart.
    
    URL: /cart/remove/<item_id>/
    Method: POST
    
    Response:
    {
        "success": true,
        "message": "Item removed from cart",
        "cart_data": {...}
    }
    
    Security:
    - CSRF token required
    - Validates item belongs to user's cart
    """
    try:
        # Get cart for current user/session
        cart = get_or_create_cart(request)
        
        # Get cart item (must belong to user's cart)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Store product name for message
        product_name = cart_item.product.name
        
        # Delete item
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart',
            'cart_data': get_cart_data(cart)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ==========================================
# GET CART DATA (AJAX)
# ==========================================

def cart_data(request):
    """
    Get cart data as JSON.
    
    URL: /cart/data/
    Method: GET
    
    Response:
    {
        "count": 3,
        "subtotal": "149.97",
        "tax": "14.99",
        "total": "164.96"
    }
    
    Used by JavaScript to update cart count badge.
    """
    cart = get_or_create_cart(request)
    return JsonResponse(get_cart_data(cart))


# ==========================================
# CLEAR CART
# ==========================================

@require_POST
def clear_cart(request):
    """
    Remove all items from cart.
    
    URL: /cart/clear/
    Method: POST
    
    Security: CSRF token required
    """
    cart = get_or_create_cart(request)
    cart.clear()
    
    messages.success(request, 'Cart cleared')
    return redirect('cart:cart_view')