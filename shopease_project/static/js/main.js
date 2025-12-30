// ===========================================================================
// SHOPEASE MAIN JAVASCRIPT
// ===========================================================================
// File: static/js/main.js
// This file contains all JavaScript functionality for the website

// WAIT FOR DOM TO LOAD
// ====================
// This ensures all HTML elements are loaded before we try to access them
document.addEventListener('DOMContentLoaded', function() {
    console.log('ShopEase loaded successfully! 🛍️');
    
    // Initialize all functions
    initMobileMenu();
    initScrollToTop();
    initAlerts();
    initDropdowns();
    initCartBadge();
});

// ===========================================================================
// MOBILE MENU
// ===========================================================================
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            // Toggle 'active' class on nav menu
            navMenu.classList.toggle('active');
            
            // Change icon (hamburger ↔ close)
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
}

// ===========================================================================
// SCROLL TO TOP BUTTON
// ===========================================================================
function initScrollToTop() {
    const scrollBtn = document.getElementById('scrollToTop');
    
    if (scrollBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollBtn.classList.add('visible');
            } else {
                scrollBtn.classList.remove('visible');
            }
        });
        
        // Scroll to top when clicked
        scrollBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'  // Smooth scroll animation
            });
        });
    }
}

// ===========================================================================
// ALERT MESSAGES
// ===========================================================================
function initAlerts() {
    // Close alerts when X button clicked
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    
    alertCloseButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Fade out animation
            this.parentElement.style.opacity = '0';
            
            // Remove from DOM after animation
            setTimeout(function() {
                button.parentElement.remove();
            }, 300);
        });
    });
    
    // Auto-hide success alerts after 5 seconds
    const successAlerts = document.querySelectorAll('.alert-success');
    
    successAlerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

// ===========================================================================
// DROPDOWN MENUS
// ===========================================================================
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(function(dropdown) {
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        // Show dropdown on hover (desktop)
        dropdown.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768) {
                dropdownMenu.style.display = 'block';
            }
        });
        
        dropdown.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768) {
                dropdownMenu.style.display = 'none';
            }
        });
        
        // Toggle dropdown on click (mobile)
        dropdown.querySelector('.nav-link').addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const isVisible = dropdownMenu.style.display === 'block';
                dropdownMenu.style.display = isVisible ? 'none' : 'block';
            }
        });
    });
}

// ===========================================================================
// SHOPPING CART BADGE
// ===========================================================================
function initCartBadge() {
    // Get cart count from localStorage or session
    // We'll implement this fully when we add cart functionality
    updateCartBadge();
}

function updateCartBadge() {
    const cartBadge = document.querySelector('.cart-badge');
    
    if (cartBadge) {
        // For now, show 0
        // Later, we'll get this from the actual cart
        const cartCount = getCartCount();
        cartBadge.textContent = cartCount;
        
        // Hide badge if cart is empty
        if (cartCount === 0) {
            cartBadge.style.display = 'none';
        } else {
            cartBadge.style.display = 'block';
        }
    }
}

function getCartCount() {
    // Placeholder function
    // Will be replaced with actual cart logic
    return 0;
}

// ===========================================================================
// SEARCH FUNCTIONALITY
// ===========================================================================
function initSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Prevent submission if search is empty
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
                searchInput.classList.add('error-shake');
                
                setTimeout(function() {
                    searchInput.classList.remove('error-shake');
                }, 500);
            }
        });
    }
}

// ===========================================================================
// PRODUCT IMAGE GALLERY (for product detail page)
// ===========================================================================
function initProductGallery() {
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.product-main-image');
    
    if (thumbnails && mainImage) {
        thumbnails.forEach(function(thumbnail) {
            thumbnail.addEventListener('click', function() {
                // Remove active class from all thumbnails
                thumbnails.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
                
                // Change main image
                const newImageSrc = this.getAttribute('data-image');
                mainImage.src = newImageSrc;
                
                // Fade animation
                mainImage.style.opacity = '0';
                setTimeout(function() {
                    mainImage.style.opacity = '1';
                }, 100);
            });
        });
    }
}

// ===========================================================================
// QUANTITY SELECTOR (for cart and product pages)
// ===========================================================================
function initQuantitySelector() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(function(input) {
        const minusBtn = input.previousElementSibling;
        const plusBtn = input.nextElementSibling;
        
        // Decrease quantity
        if (minusBtn) {
            minusBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
        
        // Increase quantity
        if (plusBtn) {
            plusBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                const max = parseInt(input.getAttribute('max')) || 99;
                if (value < max) {
                    input.value = value + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
        
        // Validate input
        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || 99;
            
            if (isNaN(value) || value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
        });
    });
}

// ===========================================================================
// ADD TO CART ANIMATION
// ===========================================================================
function addToCartAnimation(button) {
    // Create flying cart icon
    const icon = document.createElement('i');
    icon.className = 'fas fa-shopping-cart flying-cart';
    icon.style.position = 'fixed';
    icon.style.fontSize = '2rem';
    icon.style.color = '#2563eb';
    icon.style.zIndex = '9999';
    icon.style.pointerEvents = 'none';
    
    // Position at button
    const rect = button.getBoundingClientRect();
    icon.style.left = rect.left + 'px';
    icon.style.top = rect.top + 'px';
    
    document.body.appendChild(icon);
    
    // Get cart position
    const cart = document.querySelector('.cart-link');
    const cartRect = cart.getBoundingClientRect();
    
    // Animate to cart
    setTimeout(function() {
        icon.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        icon.style.left = cartRect.left + 'px';
        icon.style.top = cartRect.top + 'px';
        icon.style.opacity = '0';
        icon.style.transform = 'scale(0.3)';
    }, 10);
    
    // Remove icon and update cart badge
    setTimeout(function() {
        icon.remove();
        updateCartBadge();
        
        // Shake cart icon
        cart.classList.add('cart-shake');
        setTimeout(function() {
            cart.classList.remove('cart-shake');
        }, 500);
    }, 800);
}

// ===========================================================================
// PRICE FILTER SLIDER (for product listing page)
// ===========================================================================
function initPriceFilter() {
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    const priceMinValue = document.getElementById('priceMinValue');
    const priceMaxValue = document.getElementById('priceMaxValue');
    
    if (priceMin && priceMax) {
        priceMin.addEventListener('input', function() {
            priceMinValue.textContent = '$' + this.value;
            
            // Ensure min doesn't exceed max
            if (parseInt(this.value) > parseInt(priceMax.value)) {
                this.value = priceMax.value;
            }
        });
        
        priceMax.addEventListener('input', function() {
            priceMaxValue.textContent = '$' + this.value;
            
            // Ensure max doesn't go below min
            if (parseInt(this.value) < parseInt(priceMin.value)) {
                this.value = priceMin.value;
            }
        });
    }
}

// ===========================================================================
// TOAST NOTIFICATIONS
// ===========================================================================
function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style toast
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 9999;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(function() {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

// ===========================================================================
// LAZY LOADING IMAGES
// ===========================================================================
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// ===========================================================================
// FORM VALIDATION
// ===========================================================================
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
            
            // Show error message
            const errorMsg = input.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.style.display = 'block';
            }
        } else {
            input.classList.remove('error');
            
            // Hide error message
            const errorMsg = input.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.style.display = 'none';
            }
        }
    });
    
    return isValid;
}

// ===========================================================================
// UTILITY FUNCTIONS
// ===========================================================================

// Format price with currency
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Debounce function (useful for search)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===========================================================================
// CSS ANIMATIONS (add these to your CSS file)
// ===========================================================================
/*
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

@keyframes error-shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    75% { transform: translateX(10px); }
}

.error-shake {
    animation: error-shake 0.3s ease;
}

.cart-shake {
    animation: error-shake 0.5s ease;
}
*/

// Console log for debugging
console.log('✅ ShopEase JavaScript initialized successfully!');