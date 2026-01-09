"""
========================================
SHOPPING CART VIEWS
========================================

ARCHITECTURE: AJAX-based Cart Operations
-----------------------------------------
All cart operations (add, update, remove) use AJAX:
- No page reloads (better UX)
- Instant feedback
- Real-time cart updates

SECURITY:
- CSRF protection on all POST requests
- Stock validation before adding
- Price validation (fetch from DB, not frontend)
- Session management (cart tied to session/user)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .cart import CartService
from apps.products.models import Product
import json


# ==========================================
# CART PAGE VIEW
# ==========================================

def cart_view(request):
    """
    Display shopping cart page.
    
    URL: /cart/
    Method: GET
    
    Shows:
    - All items in cart
    - Quantities
    - Prices
    - Subtotal/total
    - Proceed to checkout button
    
    Performance:
    - Optimized queries with select_related
    - Minimal database hits
    """
    
    # Initialize cart service
    cart = CartService(request)
    
    # Get cart data
    cart_data = cart.get_cart_data()
    
    context = {
        'cart_items': cart_data['items'],
        'cart_count': cart_data['item_count'],
        'subtotal': cart_data['subtotal'],
        'total': cart_data['total'],
        'has_items': cart_data['has_items'],
        'page_title': 'Shopping Cart'
    }
    
    return render(request, 'cart/cart.html', context)


# ==========================================
# ADD TO CART (AJAX)
# ==========================================

@require_POST
def add_to_cart(request):
    """
    Add product to cart via AJAX.
    
    URL: /cart/add/
    Method: POST (AJAX)
    
    Request body (JSON):
        {
            "product_id": 5,
            "quantity": 2
        }
    
    Response (JSON):
        {
            "success": true,
            "message": "Added to cart",
            "cart_count": 3,
            "cart_total": "149.99"
        }
    
    SECURITY:
    - CSRF token required
    - Product validation (exists, active, in stock)
    - Quantity validation (positive integer, <= stock)
    - Price fetched from database (not frontend)
    """
    
    try:
        # Parse JSON request body
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Validate inputs
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID required'
            })
        
        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Quantity must be at least 1'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity'
            })
        
        # Add to cart via service layer
        cart = CartService(request)
        result = cart.add(product_id, quantity)
        
        # Return result
        return JsonResponse({
            'success': result['success'],
            'message': result['message'],
            'cart_count': result['cart_count'],
            'cart_total': str(result['cart_total'])
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        })
    
    except Exception as e:
        # Log error for debugging
        print(f"Cart add error: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


# ==========================================
# UPDATE CART ITEM (AJAX)
# ==========================================

@require_POST
def update_cart(request):
    """
    Update item quantity in cart via AJAX.
    
    URL: /cart/update/
    Method: POST (AJAX)
    
    Request body (JSON):
        {
            "product_id": 5,
            "quantity": 3
        }
    
    Response (JSON):
        {
            "success": true,
            "message": "Cart updated",
            "cart_count": 3,
            "cart_total": "179.97",
            "item_total": "59.99"
        }
    
    Special cases:
    - quantity = 0: Removes item
    - quantity > stock: Returns error
    """
    
    try:
        # Parse request
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        # Validate inputs
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID required'
            })
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid quantity'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity'
            })
        
        # Update cart
        cart = CartService(request)
        result = cart.update(product_id, quantity)
        
        # Calculate item total if item still exists
        item_total = None
        if result['success'] and quantity > 0:
            # Get updated item
            items = cart.get_items()
            for item in items:
                if item.product_id == int(product_id):
                    item_total = str(item.get_total_price())
                    break
        
        return JsonResponse({
            'success': result['success'],
            'message': result['message'],
            'cart_count': result['cart_count'],
            'cart_total': str(result['cart_total']),
            'item_total': item_total
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        })
    
    except Exception as e:
        print(f"Cart update error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


# ==========================================
# REMOVE FROM CART (AJAX)
# ==========================================

@require_POST
def remove_from_cart(request):
    """
    Remove item from cart via AJAX.
    
    URL: /cart/remove/
    Method: POST (AJAX)
    
    Request body (JSON):
        {
            "product_id": 5
        }
    
    Response (JSON):
        {
            "success": true,
            "message": "Item removed",
            "cart_count": 2,
            "cart_total": "99.98"
        }
    """
    
    try:
        # Parse request
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        # Validate input
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID required'
            })
        
        # Remove from cart
        cart = CartService(request)
        result = cart.remove(product_id)
        
        return JsonResponse({
            'success': result['success'],
            'message': result['message'],
            'cart_count': result['cart_count'],
            'cart_total': str(result['cart_total'])
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        })
    
    except Exception as e:
        print(f"Cart remove error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


# ==========================================
# CLEAR CART (AJAX)
# ==========================================

@require_POST
def clear_cart(request):
    """
    Remove all items from cart via AJAX.
    
    URL: /cart/clear/
    Method: POST (AJAX)
    
    Response (JSON):
        {
            "success": true,
            "message": "Cart cleared",
            "cart_count": 0,
            "cart_total": "0.00"
        }
    """
    
    try:
        # Clear cart
        cart = CartService(request)
        result = cart.clear()
        
        return JsonResponse(result)
    
    except Exception as e:
        print(f"Cart clear error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


# ==========================================
# GET CART DATA (AJAX)
# ==========================================

def get_cart_data(request):
    """
    Get current cart data via AJAX.
    
    URL: /cart/data/
    Method: GET (AJAX)
    
    Response (JSON):
        {
            "success": true,
            "cart_count": 3,
            "cart_total": "149.99",
            "items": [
                {
                    "product_id": 5,
                    "product_name": "Product Name",
                    "quantity": 2,
                    "price": "49.99",
                    "total": "99.98"
                }
            ]
        }
    
    Use case:
    - Update cart count in navbar without page reload
    - Refresh cart data after operations
    """
    
    try:
        cart = CartService(request)
        cart_data = cart.get_cart_data()
        
        # Format items for JSON
        items = []
        for item in cart_data['items']:
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_slug': item.product.slug,
                'product_image': item.product.image.url if item.product.image else None,
                'quantity': item.quantity,
                'price': str(item.price_snapshot),
                'total': str(item.get_total_price())
            })
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_data['item_count'],
            'cart_total': str(cart_data['total']),
            'items': items
        })
    
    except Exception as e:
        print(f"Get cart data error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })