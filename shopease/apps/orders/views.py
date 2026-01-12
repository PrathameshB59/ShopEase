"""
========================================
CHECKOUT VIEWS - FAKE VERSION (Development)
========================================

Simplified checkout without payment processing.
Orders are created immediately as COMPLETED.

Copy this to: apps/orders/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import Order, OrderItem
from .forms import CheckoutForm
from apps.cart.models import Cart


@login_required
def checkout(request):
    """
    Display checkout page and process orders.
    
    For now:
    - No payment processing
    - Orders created immediately as COMPLETED
    - Stock decreased right away
    - Cart cleared
    
    Later:
    - Add real payment processing
    - Orders start as PENDING
    - Stock decreased after payment
    """
    
    # ==========================================
    # STEP 1: GET USER'S CART
    # ==========================================
    try:
        # Get cart with all items and products
        # This prevents N+1 query problem
        cart = Cart.objects.select_related('user').prefetch_related(
            'items__product'
        ).get(user=request.user)
    except Cart.DoesNotExist:
        # User has no cart
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('cart:view_cart')
    
    # Get cart items
    cart_items = cart.items.all()
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('cart:view_cart')
    
    # ==========================================
    # STEP 2: VALIDATE STOCK
    # ==========================================
    # Check if we have enough stock for each item
    out_of_stock_items = []
    
    for item in cart_items:
        if item.quantity > item.product.stock:
            # Not enough stock!
            out_of_stock_items.append({
                'name': item.product.name,
                'requested': item.quantity,
                'available': item.product.stock
            })
    
    # If any items are out of stock, show error
    if out_of_stock_items:
        from django.utils.safestring import mark_safe
        error_msg = "Sorry, we don't have enough stock:<br><br>"
        for item in out_of_stock_items:
            error_msg += f"<strong>{item['name']}</strong>: "
            error_msg += f"You want {item['requested']}, "
            error_msg += f"we have {item['available']}<br>"
        
        messages.error(request, mark_safe(error_msg))
        return redirect('cart:view_cart')
    
    # ==========================================
    # STEP 3: CALCULATE TOTALS
    # ==========================================
    # Calculate order totals
    # Using Decimal for exact precision (important for money!)
    
    # Subtotal = sum of all items
    subtotal = sum(
        item.product.price * item.quantity 
        for item in cart_items
    )
    
    # Tax = 18% GST (change for your country)
    tax_rate = Decimal('0.18')  # 18%
    tax = subtotal * tax_rate
    
    # Shipping
    # Free shipping over ₹1000, otherwise ₹50
    shipping = Decimal('0.00') if subtotal >= Decimal('1000.00') else Decimal('50.00')
    
    # Total
    total = subtotal + tax + shipping
    
    # ==========================================
    # STEP 4: HANDLE FORM SUBMISSION
    # ==========================================
    if request.method == 'POST':
        # User submitted the form
        form = CheckoutForm(request.POST)
        
        # Validate form
        if form.is_valid():
            # Form is valid! Get the cleaned data
            data = form.cleaned_data
            
            try:
                # Use transaction to ensure all-or-nothing
                # If any step fails, everything rolls back
                with transaction.atomic():
                    
                    # ======================================
                    # CREATE ORDER
                    # ======================================
                    order = Order.objects.create(
                        # User
                        user=request.user,
                        
                        # Shipping information
                        shipping_full_name=data['full_name'],
                        shipping_email=data['email'],
                        shipping_phone=data['phone'],
                        shipping_address_line1=data['address_line1'],
                        shipping_address_line2=data['address_line2'],
                        shipping_city=data['city'],
                        shipping_state=data['state'],
                        shipping_postal_code=data['postal_code'],
                        shipping_country=data['country'],
                        
                        # Payment information
                        total_amount=total,
                        payment_method='FAKE',  # Fake payment for now
                        
                        # Order notes
                        order_notes=data.get('order_notes', ''),
                        
                        # Status (COMPLETED immediately for fake checkout)
                        status='COMPLETED',
                    )
                    
                    # ======================================
                    # CREATE ORDER ITEMS
                    # ======================================
                    # For each item in cart, create an OrderItem
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            # price, product_name, product_sku auto-filled by save()
                        )
                    
                    # ======================================
                    # UPDATE STOCK
                    # ======================================
                    # Decrease product stock
                    # (In real version, this happens after payment)
                    for cart_item in cart_items:
                        product = cart_item.product
                        product.stock -= cart_item.quantity
                        product.save(update_fields=['stock'])
                    
                    # ======================================
                    # CLEAR CART
                    # ======================================
                    # Order is placed, clear the cart
                    cart.items.all().delete()
                    
                    # ======================================
                    # SUCCESS MESSAGE
                    # ======================================
                    # Show success message to user
                    messages.success(
                        request,
                        f'🎉 Order placed successfully! '
                        f'Order number: #{str(order.order_id)[:8]}'
                    )
                    
                    # Redirect to order detail page
                    return redirect('orders:order_detail', order_id=order.order_id)
            
            except Exception as e:
                # Something went wrong!
                # Log the error (for debugging)
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Order creation failed: {str(e)}")
                
                # Show user-friendly error message
                messages.error(
                    request,
                    'Oops! Something went wrong. Please try again.'
                )
        
        else:
            # Form has errors
            # Show form again with error messages
            messages.error(request, 'Please correct the errors below.')
        
        # Render form with errors
        return render(request, 'checkout/checkout.html', {
            'form': form,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total,
        })
    
    # ==========================================
    # STEP 5: DISPLAY FORM (GET REQUEST)
    # ==========================================
    else:
        # GET request - show empty form
        
        # Pre-fill form with user data if available
        initial_data = {}
        
        # If user has first/last name, pre-fill
        if request.user.first_name or request.user.last_name:
            initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        
        # Pre-fill email
        if request.user.email:
            initial_data['email'] = request.user.email
        
        # Create form with initial data
        form = CheckoutForm(initial=initial_data)
    
    # Render checkout page
    return render(request, 'checkout/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    })


@login_required
def order_detail(request, order_id):
    """
    Display order details.
    
    Shows:
    - Order number
    - Order status
    - Shipping address
    - Order items
    - Total amount
    """
    
    # Get order
    # 404 if not found or doesn't belong to user
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_id=order_id,
        user=request.user  # Security: user can only see their own orders
    )
    
    return render(request, 'checkout/order_detail.html', {
        'order': order,
    })


@login_required
def order_list(request):
    """
    Display user's order history.
    
    Shows all orders, newest first.
    """
    
    # Get all user's orders
    orders = Order.objects.filter(
        user=request.user
    ).select_related('user').order_by('-created_at')
    
    return render(request, 'checkout/order_list.html', {
        'orders': orders,
    })


@login_required
@require_POST
def cancel_order(request, order_id):
    """
    Cancel an order.
    
    What happens:
    1. Check if order can be cancelled
    2. Restore product stock
    3. Update status to CANCELLED
    4. Log the reason
    """
    
    # Get order (404 if not found or not user's order)
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )
    
    # Check if order can be cancelled
    if not order.can_be_cancelled():
        messages.error(
            request,
            f"Sorry, this order cannot be cancelled. "
            f"Current status: {order.get_status_display()}"
        )
        return redirect('orders:order_detail', order_id=order_id)
    
    # Get cancellation reason (optional)
    reason = request.POST.get('reason', '')
    
    # Cancel the order
    try:
        order.cancel_order(reason=reason)
        
        messages.success(
            request,
            f'Order #{str(order.order_id)[:8]} has been cancelled successfully. '
            f'Product stock has been restored.'
        )
    except Exception as e:
        messages.error(request, f'Failed to cancel order: {str(e)}')
    
    return redirect('orders:order_detail', order_id=order_id)