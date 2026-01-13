/**
 * ========================================
 * ADMIN PANEL JAVASCRIPT
 * ========================================
 *
 * Custom scripts for the admin panel.
 * Features will be added in later phases.
 */

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('ShopEase Admin Panel loaded');

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Tooltips initialization (if any)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Future features:
// - Chart.js integration (Phase 6)
// - Bulk actions (Phase 2-5)
// - Real-time notifications (Future enhancement)
// - Data tables with sorting/filtering
