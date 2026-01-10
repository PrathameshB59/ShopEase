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

from .cart import CartService

from .models import Cart, CartItem
from apps.products.models import Product
    # 

# ==========================================
# HELPER FUNCTIONS
# ==========================================

# views.py - inside get_or_create_cart
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        
        # IMPORTANT: Force the session to persist
        request.session.modified = True 
        
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
    cart_service = CartService(request)
    cart_data = cart_service.get_cart_data()
    
    return render(request, 'cart/cart.html', {
        'cart': cart_service.cart,
        'cart_items': cart_data['items'],
        'subtotal': cart_data['subtotal'],
        'tax': cart_data['tax'],
        'total': cart_data['total']
    })

# ==========================================
# ADD TO CART
# ==========================================

@require_POST
def add_to_cart(request):
    cart_service = CartService(request)

    # Support both form-encoded POST (from forms) and JSON (from fetch)
    product_id = None
    quantity = 1

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))  # Convert to int
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid JSON, product_id or quantity'}, status=400)
    else:
        product_id = request.POST.get('product_id')
        try:
            product_id = int(product_id)  # Convert to int
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid product_id or quantity'}, status=400)

    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product id is required'}, status=400)

    print(f'DEBUG: Adding product {product_id}, qty {quantity} to cart')
    print(f'DEBUG: Session key: {request.session.session_key}')
    print(f'DEBUG: Cart ID: {cart_service.cart.id}')
    
    # The service handles session creation and DB saving internally
    result = cart_service.add(product_id=product_id, quantity=quantity)
    
    print(f'DEBUG: Result: {result}')
    print(f'DEBUG: Cart items after add: {cart_service.cart.items.count()}')

    if result['success']:
        return JsonResponse(result)
    else:
        return JsonResponse(result, status=400)


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