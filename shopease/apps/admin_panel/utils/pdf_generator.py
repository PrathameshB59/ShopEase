"""
========================================
PDF INVOICE GENERATOR
========================================

Generates PDF invoices for orders using WeasyPrint.

WeasyPrint converts HTML/CSS to PDF with excellent support for:
- Modern CSS layouts
- Web fonts
- Images
- Page breaks

Installation:
    pip install weasyprint

Note: WeasyPrint requires additional system dependencies.
See: https://weasyprint.readthedocs.io/en/stable/install.html
"""

from django.template.loader import render_to_string
from django.conf import settings
import os


def generate_invoice_pdf(order):
    """
    Generate PDF invoice for an order.

    Args:
        order: Order instance

    Returns:
        Tuple of (filename, pdf_bytes)

    Raises:
        ImportError: If WeasyPrint is not installed
        Exception: If PDF generation fails
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise ImportError(
            'WeasyPrint is not installed. '
            'Install it with: pip install weasyprint'
        )

    # Company information (can be moved to settings later)
    company_info = {
        'name': 'ShopEase',
        'address': '123 Business Street',
        'city': 'Mumbai, Maharashtra 400001',
        'country': 'India',
        'phone': '+91-1234567890',
        'email': 'support@shopease.com',
        'website': 'www.shopease.com',
        'gstin': 'GST123456789',  # GST number for India
    }

    # Prepare context for template
    context = {
        'order': order,
        'company': company_info,
        'items': order.items.all(),
        'subtotal': order.total_amount,  # Can calculate excluding tax if needed
        'tax_amount': 0,  # Calculate if applicable
        'total': order.total_amount,
    }

    # Render HTML template
    html_content = render_to_string('admin_panel/orders/invoice_pdf.html', context)

    # Optional: Add custom CSS for invoice styling
    css_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'admin_panel/css/invoice.css')

    # Generate PDF
    try:
        if os.path.exists(css_path):
            pdf_file = HTML(string=html_content).write_pdf(
                stylesheets=[CSS(css_path)]
            )
        else:
            # Generate without custom CSS if file doesn't exist
            pdf_file = HTML(string=html_content).write_pdf()
    except Exception as e:
        raise Exception(f'Failed to generate PDF: {str(e)}')

    # Generate filename
    filename = f'invoice_{str(order.order_id)[:8]}.pdf'

    return filename, pdf_file


def save_invoice_to_media(order, pdf_bytes):
    """
    Save generated invoice to media directory.

    Args:
        order: Order instance
        pdf_bytes: PDF file bytes

    Returns:
        Path to saved file relative to MEDIA_ROOT
    """
    # Create invoices directory if it doesn't exist
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)

    # Generate filename
    filename = f'invoice_{str(order.order_id)}.pdf'
    filepath = os.path.join(invoices_dir, filename)

    # Save PDF
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)

    # Return relative path
    return os.path.join('invoices', filename)
