/* ==========================================
   CSRF TOKEN HANDLING FOR AJAX REQUESTS
   Critical Security Component
   ========================================== */

/* WHY THIS MATTERS:
 * Django's CSRF protection prevents attackers from forging requests
 * Example attack without CSRF: Malicious site tricks user's browser into
 * making unauthorized requests to our site (like purchasing products)
 * 
 * How CSRF protection works:
 * 1. Django generates unique token for each user session
 * 2. Token must be included in every POST/PUT/DELETE request
 * 3. Django verifies token matches before processing request
 * 4. Without valid token, request is rejected (403 Forbidden)
 */

// Get CSRF token from cookie
// Django stores the token in a cookie named 'csrftoken'
function getCookie(name) {
    let cookieValue = null;
    
    // document.cookie contains all cookies as one string
    // Format: "name1=value1; name2=value2; name3=value3"
    if (document.cookie && document.cookie !== '') {
        // Split into array of individual cookies
        const cookies = document.cookie.split(';');
        
        // Loop through cookies to find the one we want
        for (let i = 0; i < cookies.length; i++) {
            // Trim whitespace from cookie string
            const cookie = cookies[i].trim();
            
            // Check if this cookie starts with the name we're looking for
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // Extract the value part (everything after 'name=')
                // decodeURIComponent handles URL-encoded special characters
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get the CSRF token from cookie
const csrftoken = getCookie('csrftoken');

/* ==========================================
   CONFIGURE FETCH API TO INCLUDE CSRF TOKEN
   ========================================== */

// Save original fetch function
const originalFetch = window.fetch;

// Override fetch to automatically include CSRF token
window.fetch = function(url, options = {}) {
    // Only add CSRF token for requests that modify data
    // GET and HEAD requests don't need CSRF protection
    const method = options.method ? options.method.toUpperCase() : 'GET';
    const needsCsrf = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
    
    // Only add CSRF for same-origin requests
    // External API calls don't use Django's CSRF protection
    const isRelativeUrl = !url.startsWith('http://') && !url.startsWith('https://');
    const isSameOrigin = url.startsWith(window.location.origin);
    
    if (needsCsrf && (isRelativeUrl || isSameOrigin)) {
        // Initialize headers if not present
        options.headers = options.headers || {};
        
        // Add CSRF token to request headers
        // Django looks for this header in incoming requests
        options.headers['X-CSRFToken'] = csrftoken;
        
        // Also set credentials to 'same-origin' to include cookies
        // This ensures session cookie is sent with request
        options.credentials = options.credentials || 'same-origin';
    }
    
    // Call original fetch with modified options
    return originalFetch(url, options);
};

/* ==========================================
   CONFIGURE XMLHTTPREQUEST TO INCLUDE CSRF TOKEN
   ========================================== */

// For libraries that use XMLHttpRequest (jQuery, Axios, etc.)
// We need to set up automatic CSRF token inclusion

// Save original XMLHttpRequest open method
const originalOpen = XMLHttpRequest.prototype.open;

// Override open method to add CSRF header
XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    // Store method and URL for use in send()
    this._method = method;
    this._url = url;
    
    // Call original open method
    return originalOpen.call(this, method, url, ...rest);
};

// Save original XMLHttpRequest send method
const originalSend = XMLHttpRequest.prototype.send;

// Override send method to add CSRF token
XMLHttpRequest.prototype.send = function(...args) {
    // Check if this request needs CSRF token
    const method = this._method ? this._method.toUpperCase() : 'GET';
    const needsCsrf = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
    
    // Check if URL is same-origin
    const url = this._url;
    const isRelativeUrl = !url.startsWith('http://') && !url.startsWith('https://');
    const isSameOrigin = url.startsWith(window.location.origin);
    
    if (needsCsrf && (isRelativeUrl || isSameOrigin)) {
        // Set CSRF token header
        this.setRequestHeader('X-CSRFToken', csrftoken);
    }
    
    // Call original send method
    return originalSend.apply(this, args);
};

/* ==========================================
   HELPER FUNCTION FOR MANUAL AJAX REQUESTS
   ========================================== */

/**
 * Make a POST request with CSRF token
 * @param {string} url - The URL to send request to
 * @param {Object} data - Data to send in request body
 * @returns {Promise} - Fetch promise
 */
function csrfPost(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data),
        credentials: 'same-origin'
    });
}

/**
 * Make a PUT request with CSRF token
 * @param {string} url - The URL to send request to
 * @param {Object} data - Data to send in request body
 * @returns {Promise} - Fetch promise
 */
function csrfPut(url, data) {
    return fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data),
        credentials: 'same-origin'
    });
}

/**
 * Make a DELETE request with CSRF token
 * @param {string} url - The URL to send request to
 * @returns {Promise} - Fetch promise
 */
function csrfDelete(url) {
    return fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    });
}

// Export functions for use in other scripts
window.csrfPost = csrfPost;
window.csrfPut = csrfPut;
window.csrfDelete = csrfDelete;

/* ==========================================
   USAGE EXAMPLES
   ========================================== */

/*
// Example 1: Using enhanced fetch (automatic CSRF)
fetch('/api/cart/add/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ product_id: 123, quantity: 1 })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));

// Example 2: Using helper function
csrfPost('/api/cart/add/', { product_id: 123, quantity: 1 })
    .then(response => response.json())
    .then(data => console.log('Success:', data))
    .catch(error => console.error('Error:', error));

// Example 3: Using XMLHttpRequest (automatic CSRF)
const xhr = new XMLHttpRequest();
xhr.open('POST', '/api/cart/add/');
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.onload = function() {
    if (xhr.status === 200) {
        console.log('Success:', JSON.parse(xhr.responseText));
    }
};
xhr.send(JSON.stringify({ product_id: 123, quantity: 1 }));
*/

/* ==========================================
   DEBUGGING
   ========================================== */

// Log CSRF token for debugging (remove in production!)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('CSRF Token:', csrftoken);
    if (!csrftoken) {
        console.warn('CSRF token not found! Make sure {% csrf_token %} is in your template.');
    }
}

/* ==========================================
   SECURITY NOTES
   ========================================== */

/*
 * NEVER disable CSRF protection in production
 * NEVER send CSRF token to external domains
 * NEVER log CSRF token in production (remove debug code)
 * ALWAYS use HTTPS in production (cookies with Secure flag)
 * ALWAYS set SameSite=Strict on CSRF cookie
 * 
 * Common CSRF errors and fixes:
 * 
 * 1. "CSRF token missing or incorrect"
 *    - Check {% csrf_token %} is in your template
 *    - Verify cookie is being set (check browser DevTools)
 *    - Ensure domain in settings.py matches your domain
 * 
 * 2. "CSRF verification failed. Request aborted."
 *    - Cookie might be blocked (check SameSite settings)
 *    - Token might be expired (clear cookies and reload)
 *    - Mixed HTTP/HTTPS causing cookie issues
 * 
 * 3. Token not included in AJAX request
 *    - Check this script loads before your AJAX code
 *    - Verify fetch/XMLHttpRequest is being used
 *    - Some libraries need manual configuration
 */