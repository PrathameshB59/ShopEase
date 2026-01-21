"""
========================================
ADMIN PANEL FORMS
========================================

Forms for admin panel operations including product management
and role management.
"""

from django import forms
from apps.products.models import Product, Category
from apps.admin_panel.models import AdminRole
from django.contrib.auth.models import User


class ProductForm(forms.ModelForm):
    """Form for creating and editing products in admin panel."""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'short_description',
            'price', 'sale_price', 'stock', 'image', 'is_active', 'is_featured',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description for product cards (max 200 characters)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Optional sale price'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Available quantity'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_sale_price(self):
        """Validate sale price is less than regular price."""
        sale_price = self.cleaned_data.get('sale_price')
        price = self.cleaned_data.get('price')

        if sale_price and price and sale_price >= price:
            raise forms.ValidationError('Sale price must be less than regular price.')

        return sale_price

    def clean_image(self):
        """Validate image file size (max 5MB)."""
        image = self.cleaned_data.get('image')

        if image and hasattr(image, 'size'):
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be less than 5MB.')

        return image


class CustomRoleForm(forms.ModelForm):
    """Form for creating and editing custom roles."""

    class Meta:
        model = AdminRole
        fields = [
            'custom_role_name', 'role_description',
            'can_view_orders', 'can_edit_orders', 'can_process_refunds',
            'can_view_products', 'can_edit_products', 'can_manage_featured',
            'can_moderate_reviews', 'can_view_users', 'can_manage_roles',
            'can_view_analytics', 'can_export_data',
        ]
        widgets = {
            'custom_role_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter role name (e.g., Inventory Analyst)'
            }),
            'role_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe what this role can do'
            }),
            # Checkbox widgets for all permissions
            'can_view_orders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_edit_orders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_process_refunds': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_products': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_edit_products': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_moderate_reviews': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_roles': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_analytics': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_export_data': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_custom_role_name(self):
        """Ensure unique role name and prevent conflicts with predefined roles."""
        role_name = self.cleaned_data.get('custom_role_name')

        if not role_name:
            raise forms.ValidationError('Role name is required.')

        # Check for predefined role names
        predefined_roles = [
            'CUSTOMER_SERVICE', 'INVENTORY_MANAGER', 'MARKETING_MANAGER',
            'ORDER_MANAGER', 'SUPER_ADMIN'
        ]

        if role_name.upper().replace(' ', '_') in predefined_roles:
            raise forms.ValidationError(
                f'Cannot use "{role_name}" as it conflicts with a predefined role.'
            )

        # Check for uniqueness (if creating new role)
        if not self.instance.pk:
            if AdminRole.objects.filter(custom_role_name__iexact=role_name).exists():
                raise forms.ValidationError(
                    f'A role with the name "{role_name}" already exists.'
                )

        return role_name


class SuperuserCreationForm(forms.Form):
    """Form for creating a new superuser."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password'
        })
    )

    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)'
        })
    )

    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)'
        })
    )

    def clean_username(self):
        """Check if username already exists."""
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')

        return username

    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')

        return email

    def clean(self):
        """Validate that passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data
