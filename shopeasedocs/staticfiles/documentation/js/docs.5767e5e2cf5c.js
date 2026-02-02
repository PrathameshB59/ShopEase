/**
 * ShopEase Documentation - Main JavaScript
 * Handles interactive features for public documentation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize helpful buttons
    initHelpfulButtons();

    // Initialize copy code buttons
    initCopyCodeButtons();

    // Initialize smooth scrolling
    initSmoothScroll();

    // Initialize tooltips
    initTooltips();

    // Initialize search autocomplete
    initSearchAutocomplete();
});

/**
 * Handle "Was this helpful?" buttons
 */
function initHelpfulButtons() {
    const helpfulButtons = document.querySelectorAll('.helpful-btn');

    helpfulButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const modelType = this.dataset.type;
            const objectId = this.dataset.id;
            const isHelpful = this.dataset.helpful === 'true';

            try {
                const response = await fetch('/ajax/mark-helpful/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: new URLSearchParams({
                        'model_type': modelType,
                        'object_id': objectId,
                        'is_helpful': isHelpful
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Update button counts
                    const buttons = document.querySelectorAll(
                        `.helpful-btn[data-type="${modelType}"][data-id="${objectId}"]`
                    );
                    buttons.forEach(btn => {
                        if (btn.dataset.helpful === 'true') {
                            btn.innerHTML = `<i class="bi bi-hand-thumbs-up"></i> Yes (${data.helpful_count})`;
                        } else {
                            btn.innerHTML = `<i class="bi bi-hand-thumbs-down"></i> No (${data.not_helpful_count})`;
                        }
                        btn.disabled = true;
                    });

                    // Show success message
                    showToast('Thank you for your feedback!', 'success');
                } else {
                    showToast('Failed to submit feedback. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'error');
            }
        });
    });
}

/**
 * Initialize copy code buttons for code blocks
 */
function initCopyCodeButtons() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach(codeBlock => {
        const pre = codeBlock.parentElement;
        pre.style.position = 'relative';

        const button = document.createElement('button');
        button.className = 'btn btn-sm btn-outline-secondary copy-code-btn';
        button.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        button.style.position = 'absolute';
        button.style.top = '0.5rem';
        button.style.right = '0.5rem';

        button.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                button.classList.remove('btn-outline-secondary');
                button.classList.add('btn-success');

                setTimeout(() => {
                    button.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-outline-secondary');
                }, 2000);
            } catch (error) {
                console.error('Copy failed:', error);
                showToast('Failed to copy code', 'error');
            }
        });

        pre.appendChild(button);
    });
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update URL without scrolling
                history.pushState(null, null, href);
            }
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize search autocomplete (basic implementation)
 */
function initSearchAutocomplete() {
    const searchInputs = document.querySelectorAll('input[name="query"]');

    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            // This is a placeholder for autocomplete functionality
            // You can implement AJAX-based autocomplete here
            const query = this.value;
            if (query.length >= 3) {
                // TODO: Fetch suggestions via AJAX
                console.log('Search query:', query);
            }
        }, 300));
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Show toast
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * Get CSRF token from cookies
 */
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

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format timestamp to relative time (e.g., "5 minutes ago")
 */
function timeAgo(timestamp) {
    const now = new Date();
    const past = new Date(timestamp);
    const diffInSeconds = Math.floor((now - past) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(diffInSeconds / secondsInUnit);
        if (interval >= 1) {
            return interval === 1
                ? `1 ${unit} ago`
                : `${interval} ${unit}s ago`;
        }
    }

    return 'just now';
}

/**
 * Highlight search terms in text
 */
function highlightSearchTerms(text, searchTerm) {
    if (!searchTerm) return text;

    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

/**
 * Initialize image zoom on click
 */
function initImageZoom() {
    const images = document.querySelectorAll('.doc-content img, .screenshot-gallery img');

    images.forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            // Create modal for zoomed image
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.alt || 'Image'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${this.src}" class="img-fluid" alt="${this.alt || ''}">
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();

                modal.addEventListener('hidden.bs.modal', function() {
                    modal.remove();
                });
            }
        });
    });
}

/**
 * Print documentation
 */
function printDocumentation() {
    window.print();
}

/**
 * Export as PDF (requires additional library)
 */
function exportAsPDF() {
    // This would require a library like jsPDF
    showToast('PDF export functionality coming soon!', 'info');
}

// Expose functions globally
window.DocUtils = {
    showToast,
    timeAgo,
    highlightSearchTerms,
    printDocumentation,
    exportAsPDF
};
