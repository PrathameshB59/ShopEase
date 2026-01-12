"""
========================================
AUTHENTICATION FORMS
========================================
Django forms for user registration, login, profile editing.

SECURITY FEATURES:
- Password validation (strength requirements)
- Email validation (format, uniqueness)
- CSRF protection (automatic in Django forms)
- XSS prevention (auto-escaping)
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class UserRegistrationForm(UserCreationForm):
    """
    User registration form with email validation.
    
    Extends Django's UserCreationForm to add:
    - Email field (required)
    - First/last name
    - Custom styling classes
    
    Security:
    - Password validation (min 8 chars, not common, not all numbers)
    - Email uniqueness check
    - Username validation (alphanumeric + @/./+/-/_)
    """
    
    # Email field (required)
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )
    
    # First name (optional but recommended)
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    # Last name (optional)
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Add CSS classes to password fields."""
        super().__init__(*args, **kwargs)
        
        # Add classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        """
        Validate email uniqueness.
        
        Security: Prevents duplicate accounts
        UX: Clear error message
        
        Returns: Cleaned email (lowercase)
        Raises: ValidationError if email exists
        """
        email = self.cleaned_data.get('email').lower()
        
        # Check if email already registered
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email is already registered. Please use another email or login.'
            )
        
        return email


class UserLoginForm(AuthenticationForm):
    """
    Custom login form with styled fields.

    Extends Django's AuthenticationForm.

    Features:
    - Accepts email OR username for login
    - Works with EmailOrUsernameBackend

    Security features (built-in):
    - Password hashing verification
    - Account lockout after failed attempts (add django-axes)
    - Session fixation prevention
    """

    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email or Username',
            'autofocus': True
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    
    Allows users to edit:
    - Contact information
    - Shipping address
    - Billing address
    - Profile picture
    - Preferences
    """
    
    class Meta:
        model = Profile
        fields = [
            'phone',
            'shipping_address_line1',
            'shipping_address_line2',
            'shipping_city',
            'shipping_state',
            'shipping_postal_code',
            'shipping_country',
            'billing_same_as_shipping',
            'billing_address_line1',
            'billing_address_line2',
            'billing_city',
            'billing_state',
            'billing_postal_code',
            'billing_country',
            'avatar',
            'newsletter_subscribed'
        ]
        
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 1234567890'
            }),
            'shipping_address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'shipping_address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, unit (optional)'
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'shipping_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'shipping_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'shipping_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'billing_address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'billing_address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, unit (optional)'
            }),
            'billing_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'billing_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'billing_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'billing_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating User model fields.
    
    Allows changing:
    - Email
    - First/last name
    
    Note: Username cannot be changed (security risk)
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }