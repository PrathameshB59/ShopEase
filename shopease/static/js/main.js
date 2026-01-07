/* ==========================================
   SHOPEASE - MAIN JAVASCRIPT
   Core Interactivity & Features
   ========================================== */

(function() {
    'use strict';  // Enables strict mode (catches common coding errors)

    /* ==========================================
       MOBILE MENU TOGGLE
       ========================================== */
    
    // Get mobile menu elements
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbarNav = document.querySelector('#navbar-nav');
    
    if (mobileMenuToggle && navbarNav) {
        // Toggle menu on button click
        mobileMenuToggle.addEventListener('click', function() {
            // Toggle aria-expanded for accessibility
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            
            // Toggle menu visibility
            navbarNav.classList.toggle('mobile-menu-open');
            
            // Toggle hamburger animation
            this.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            document.body.classList.toggle('menu-open');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenuToggle.contains(e.target) && !navbarNav.contains(e.target)) {
                navbarNav.classList.remove('mobile-menu-open');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('menu-open');
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navbarNav.classList.contains('mobile-menu-open')) {
                navbarNav.classList.remove('mobile-menu-open');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('menu-open');
            }
        });
    }

    /* ==========================================
       DROPDOWN MENUS
       ========================================== */
    
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            // Toggle dropdown on click (mobile)
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                
                // Close all other dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(m => {
                    if (m !== menu) {
                        m.classList.remove('show');
                    }
                });
                
                // Toggle this dropdown
                this.setAttribute('aria-expanded', !isExpanded);
                menu.classList.toggle('show');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    /* ==========================================
       SMOOTH SCROLL TO ANCHORS
       ========================================== */
    
    // Add smooth scrolling to all links with hash
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Ignore empty hashes or just "#"
            if (href === '#' || href === '') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                // Get navbar height for offset
                const navbar = document.querySelector('.navbar');
                const offset = navbar ? navbar.offsetHeight : 0;
                
                // Calculate scroll position
                const targetPosition = target.offsetTop - offset - 20;
                
                // Smooth scroll
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without triggering navigation
                history.pushState(null, null, href);
            }
        });
    });

    /* ==========================================
       LAZY LOADING IMAGES
       ========================================== */
    
    // Use Intersection Observer for performance
    // Only load images when they're about to enter viewport
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Replace src with data-src
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    
                    // Replace srcset with data-srcset
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                        img.removeAttribute('data-srcset');
                    }
                    
                    // Remove loading class
                    img.classList.remove('lazy');
                    
                    // Stop observing this image
                    observer.unobserve(img);
                }
            });
        }, {
            // Start loading images 200px before they enter viewport
            rootMargin: '200px'
        });
        
        // Observe all images with lazy class
        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        document.querySelectorAll('img.lazy').forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
            if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
            }
        });
    }

    /* ==========================================
       ADD TO CART FUNCTIONALITY
       ========================================== */
    
    // Handle add to cart button clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-cart-btn')) {
            e.preventDefault();
            const button = e.target.closest('.add-to-cart-btn');
            
            // Get product data from button attributes
            const productId = button.dataset.productId;
            const productName = button.dataset.productName;
            const productPrice = button.dataset.productPrice;
            
            // Disable button to prevent double-clicks
            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = 'Adding...';
            
            // Send AJAX request to add item to cart
            // csrfPost is defined in csrf.js
            csrfPost('/cart/add/', {
                product_id: productId,
                quantity: 1
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count in navbar
                    updateCartCount(data.cart_count);
                    
                    // Show success message
                    showNotification('success', `${productName} added to cart!`);
                    
                    // Change button text temporarily
                    button.textContent = '✓ Added';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);
                } else {
                    // Show error message
                    showNotification('error', data.message || 'Failed to add to cart');
                    button.textContent = originalText;
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('error', 'Something went wrong. Please try again.');
                button.textContent = originalText;
                button.disabled = false;
            });
        }
    });

    /* ==========================================
       WISHLIST FUNCTIONALITY
       ========================================== */
    
    // Handle wishlist button clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.wishlist-btn')) {
            e.preventDefault();
            const button = e.target.closest('.wishlist-btn');
            const productId = button.dataset.productId;
            
            // Toggle wishlist status
            csrfPost('/wishlist/toggle/', {
                product_id: productId
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle active state
                    button.classList.toggle('active');
                    
                    // Update wishlist count
                    updateWishlistCount(data.wishlist_count);
                    
                    // Show appropriate message
                    const message = data.added ? 
                        'Added to wishlist' : 
                        'Removed from wishlist';
                    showNotification('success', message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('error', 'Please login to use wishlist');
            });
        }
    });

    /* ==========================================
       HELPER FUNCTIONS
       ========================================== */
    
    /**
     * Update cart count badge in navbar
     * @param {number} count - New cart count
     */
    function updateCartCount(count) {
        const cartBadge = document.querySelector('.action-link[href*="cart"] .badge');
        if (cartBadge) {
            cartBadge.textContent = count;
            
            // Animate badge
            cartBadge.classList.add('pulse');
            setTimeout(() => {
                cartBadge.classList.remove('pulse');
            }, 500);
        }
    }
    
    /**
     * Update wishlist count badge in navbar
     * @param {number} count - New wishlist count
     */
    function updateWishlistCount(count) {
        const wishlistBadge = document.querySelector('.action-link[href*="wishlist"] .badge');
        if (wishlistBadge) {
            wishlistBadge.textContent = count;
        }
    }
    
    /**
     * Show notification toast
     * @param {string} type - Type of notification (success, error, warning, info)
     * @param {string} message - Message to display
     */
    function showNotification(type, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible`;
        notification.setAttribute('data-alert', '');
        notification.setAttribute('role', 'alert');
        
        // Set notification HTML
        notification.innerHTML = `
            <span class="alert-icon">
                ${getNotificationIcon(type)}
            </span>
            <div class="alert-content">
                <p class="alert-message">${message}</p>
            </div>
            <button type="button" class="alert-close" data-dismiss="alert" aria-label="Close">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;
        
        // Add to messages container (create if doesn't exist)
        let container = document.querySelector('.messages-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'messages-container';
            container.setAttribute('role', 'alert');
            container.setAttribute('aria-live', 'polite');
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.add('dismissing');
            setTimeout(() => notification.remove(), 200);
        }, 5000);
    }
    
    /**
     * Get icon SVG for notification type
     * @param {string} type - Notification type
     * @returns {string} - SVG icon HTML
     */
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
       FORM VALIDATION
       ========================================== */
    
    // Add real-time validation to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Check if form is valid
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Show which fields are invalid
                form.querySelectorAll(':invalid').forEach(field => {
                    field.classList.add('is-invalid');
                });
            }
            
            form.classList.add('was-validated');
        });
        
        // Remove error styling when user starts typing
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    });

    /* ==========================================
       PERFORMANCE MONITORING (Development Only)
       ========================================== */
    
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Log page load time
        window.addEventListener('load', function() {
            const loadTime = performance.now();
            console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        });
    }

})();  // End of IIFE (Immediately Invoked Function Expression)