/* ==========================================
   CART JAVASCRIPT - Shopping Cart Operations
   ========================================== */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🛒 Cart JS loaded');
    
    // Initialize cart functionality
    initializeCart();
    
    // Update cart count on page load
    updateCartCount();
});

/* ==========================================
   INITIALIZATION
   ========================================== */

function initializeCart() {
    // Event delegation - attach listeners to document
    // This handles dynamically added elements too
    
    // Quantity buttons (increase/decrease)
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;
        
        const action = target.dataset.action;
        const itemId = target.dataset.itemId;
        
        if (action === 'increase') {
            handleQuantityChange(itemId, 'increase');
        } else if (action === 'decrease') {
            handleQuantityChange(itemId, 'decrease');
        } else if (action === 'remove') {
            handleRemoveItem(itemId);
        }
    });
    
    console.log('✅ Cart functionality initialized');
}

/* ==========================================
   QUANTITY CHANGE HANDLER
   ========================================== */

function handleQuantityChange(itemId, action) {
    console.log(`🔄 Changing quantity: Item ${itemId}, Action: ${action}`);
    
    // Get current quantity from input
    const cartItem = document.querySelector(`[data-item-id="${itemId}"]`);
    if (!cartItem) {
        console.error('❌ Cart item not found');
        return;
    }
    
    const quantityInput = cartItem.querySelector('.qty-input');
    let currentQuantity = parseInt(quantityInput.value);
    let newQuantity = action === 'increase' ? currentQuantity + 1 : currentQuantity - 1;
    
    // Validate quantity
    const minQty = parseInt(quantityInput.min) || 1;
    const maxQty = parseInt(quantityInput.max) || 999;
    
    if (newQuantity < minQty || newQuantity > maxQty) {
        console.warn('⚠️ Quantity out of range');
        return;
    }
    
    // Disable buttons during update
    const buttons = cartItem.querySelectorAll('.qty-btn');
    buttons.forEach(btn => btn.disabled = true);
    
    // Send AJAX request to update quantity
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Quantity updated:', data);
            
            // Update quantity input
            quantityInput.value = newQuantity;
            
            // Update item subtotal
            const itemSubtotal = cartItem.querySelector('.item-subtotal');
            if (itemSubtotal) {
                itemSubtotal.textContent = '$' + data.item_subtotal;
            }
            
            // Update cart totals
            updateCartTotals(data.cart_data);
            
            // Update cart count in navbar
            updateCartCount();
            
            // Update button states
            updateButtonStates(cartItem, newQuantity, maxQty);
            
            // Show success notification
            showNotification('success', 'Quantity updated');
        } else {
            console.error('❌ Update failed:', data.message);
            showNotification('error', data.message);
        }
        
        // Re-enable buttons
        buttons.forEach(btn => btn.disabled = false);
    })
    .catch(error => {
        console.error('❌ Error updating quantity:', error);
        showNotification('error', 'Failed to update quantity');
        buttons.forEach(btn => btn.disabled = false);
    });
}

/* ==========================================
   REMOVE ITEM HANDLER
   ========================================== */

function handleRemoveItem(itemId) {
    console.log(`🗑️ Removing item ${itemId}`);
    
    // Confirm removal
    if (!confirm('Remove this item from cart?')) {
        return;
    }
    
    const cartItem = document.querySelector(`[data-item-id="${itemId}"]`);
    if (!cartItem) return;
    
    // Send AJAX request to remove item
    fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Item removed:', data);
            
            // Fade out and remove element
            cartItem.style.opacity = '0';
            cartItem.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                cartItem.remove();
                
                // Update cart totals
                updateCartTotals(data.cart_data);
                
                // Update cart count
                updateCartCount();
                
                // If cart is empty, reload page to show empty cart message
                if (data.cart_data.count === 0) {
                    window.location.reload();
                }
            }, 300);
            
            showNotification('success', data.message);
        } else {
            console.error('❌ Remove failed:', data.message);
            showNotification('error', data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error removing item:', error);
        showNotification('error', 'Failed to remove item');
    });
}

/* ==========================================
   UPDATE CART TOTALS
   ========================================== */

function updateCartTotals(cartData) {
    console.log('💰 Updating cart totals:', cartData);
    
    // Update subtotal
    const subtotal = document.querySelector('.cart-subtotal');
    if (subtotal) {
        subtotal.textContent = '$' + cartData.subtotal;
    }
    
    // Update tax
    const tax = document.querySelector('.cart-tax');
    if (tax) {
        tax.textContent = '$' + cartData.tax;
    }
    
    // Update total
    const total = document.querySelector('.cart-total');
    if (total) {
        total.textContent = '$' + cartData.total;
        
        // Pulse animation
        total.classList.add('pulse');
        setTimeout(() => total.classList.remove('pulse'), 500);
    }
}

/* ==========================================
   UPDATE CART COUNT (NAVBAR BADGE)
   ========================================== */

function updateCartCount() {
    console.log('🔄 Updating cart count...');
    
    fetch('/cart/data/')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Cart data:', data);
            
            // Update cart count badge in navbar
            const badge = document.getElementById('cartCount');
            if (badge) {
                badge.textContent = data.count;
                
                // Pulse animation
                badge.classList.add('pulse');
                setTimeout(() => badge.classList.remove('pulse'), 500);
            }
        })
        .catch(error => {
            console.error('❌ Error fetching cart data:', error);
        });
}

/* ==========================================
   UPDATE BUTTON STATES
   ========================================== */

function updateButtonStates(cartItem, quantity, maxQty) {
    // Update decrease button state (disabled at quantity 1)
    const decreaseBtn = cartItem.querySelector('[data-action="decrease"]');
    if (decreaseBtn) {
        decreaseBtn.disabled = (quantity <= 1);
    }
    
    // Update increase button state (disabled at max stock)
    const increaseBtn = cartItem.querySelector('[data-action="increase"]');
    if (increaseBtn) {
        increaseBtn.disabled = (quantity >= maxQty);
    }
}

/* ==========================================
   NOTIFICATIONS
   ========================================== */

function showNotification(type, message) {
    console.log(`📢 Notification: ${type} - ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            ${getNotificationIcon(type)}
        </div>
        <div class="notification-message">${message}</div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    return icons[type] || icons.info;
}

/* ==========================================
   UTILITY FUNCTIONS
   ========================================== */

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* ==========================================
   ADD TO CART (FOR PRODUCT PAGES)
   ========================================== */

// Global function for adding to cart from product pages
// Accept either (productId, quantity) or (productId, productName)
window.addToCart = function(productId, qtyOrName = 1) {
    // Determine quantity: if second arg is numeric use it, otherwise default to 1
    let quantity = 1;
    let productName = null;

    if (typeof qtyOrName === 'number' && Number.isInteger(qtyOrName) && qtyOrName > 0) {
        quantity = qtyOrName;
    } else if (typeof qtyOrName === 'string') {
        // If it's numeric string, parse it
        if (/^\d+$/.test(qtyOrName)) {
            quantity = parseInt(qtyOrName, 10);
        } else {
            productName = qtyOrName; // treat as name for friendly notification
        }
    }

    console.log(`🛒 Adding to cart: Product ${productId}, Qty ${quantity}`);

    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Added to cart:', data);

            // Update cart count
            updateCartCount();

            // Show success notification (use server message or fallback)
            const msg = data.message || (productName ? `${productName} added to cart` : 'Added to cart');
            showNotification('success', msg);
        } else {
            console.error('❌ Add to cart failed:', data.message);
            showNotification('error', data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error adding to cart:', error);
        showNotification('error', 'Failed to add to cart');
    });
};

console.log('✅ Cart JS ready');