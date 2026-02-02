"""
========================================
CHECKOUT FORM - FAKE VERSION (Development)
========================================

Simplified checkout form without payment method selection.

Copy this to: apps/orders/forms.py
"""

from django import forms
from django.core.validators import RegexValidator
import re


# Phone number validator
# Ensures phone number is in correct format
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be in format: '+999999999'. Up to 15 digits allowed.",
    code='invalid_phone'
)


class CheckoutForm(forms.Form):
    """
    Checkout form for collecting shipping information.
    
    No payment method field - using fake payment for now.
    """
    
    # ==========================================
    # CONTACT INFORMATION
    # ==========================================
    
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
        }),
        label='Full Name',
        help_text='Your first and last name',
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email',
        }),
        label='Email Address',
        help_text='For order updates',
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91-9876543210',
            'autocomplete': 'tel',
        }),
        label='Phone Number',
        help_text='Include country code (e.g., +91 for India)',
    )
    
    # ==========================================
    # SHIPPING ADDRESS
    # ==========================================
    
    address_line1 = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address, P.O. box, company name',
            'autocomplete': 'address-line1',
        }),
        label='Address Line 1',
    )
    
    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartment, suite, unit, building (optional)',
            'autocomplete': 'address-line2',
        }),
        label='Address Line 2',
    )
    
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
            'autocomplete': 'address-level2',
        }),
        label='City',
    )
    
    state = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State or Province',
            'autocomplete': 'address-level1',
        }),
        label='State / Province',
    )
    
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP or Postal Code',
            'autocomplete': 'postal-code',
        }),
        label='Postal Code',
    )
    
    country = forms.CharField(
        max_length=100,
        initial='India',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country',
            'autocomplete': 'country-name',
        }),
        label='Country',
    )
    
    # ==========================================
    # ORDER NOTES (OPTIONAL)
    # ==========================================
    
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special delivery instructions? (optional)',
        }),
        label='Order Notes',
        help_text='Optional - any special instructions',
    )
    
    # ==========================================
    # CUSTOM VALIDATION
    # ==========================================
    
    def clean_phone(self):
        """
        Clean and standardize phone number.
        
        Removes spaces, dashes, parentheses.
        Adds country code if missing.
        """
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            return phone
        
        # Remove all non-digit characters except +
        phone = re.sub(r'[^+\d]', '', phone)
        
        # Add country code if missing
        if not phone.startswith('+'):
            phone = '+91' + phone  # Default to India
        
        return phone
    
    def clean_postal_code(self):
        """
        Clean postal code.
        
        Removes extra spaces.
        Converts to uppercase.
        """
        postal_code = self.cleaned_data.get('postal_code')
        
        if not postal_code:
            return postal_code
        
        # Remove spaces and convert to uppercase
        postal_code = postal_code.strip().upper()
        
        return postal_code
    
    def clean_email(self):
        """
        Normalize email address.
        
        Converts to lowercase.
        Removes spaces.
        """
        email = self.cleaned_data.get('email')
        
        if not email:
            return email
        
        # Convert to lowercase and trim
        email = email.lower().strip()
        
        return email