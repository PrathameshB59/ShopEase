"""
========================================
PRODUCTS FORMS - Form Validation
========================================
Django forms for product-related user input.

Security Features:
- CSRF protection (automatically added by Django)
- Input validation and sanitization
- Max length enforcement
- Rating range validation
"""

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Form for submitting product reviews.

    Security:
    - All fields validated by Django
    - XSS protection via template escaping
    - Length limits prevent DOS attacks

    Why ModelForm:
    - Automatically creates form from Review model
    - Less code duplication
    - Validation matches model constraints
    """

    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']

        # Custom labels for better UX
        labels = {
            'rating': 'Your Rating',
            'title': 'Review Title',
            'comment': 'Your Review'
        }

        # Help text for users
        help_texts = {
            'rating': 'Rate from 1 (Poor) to 5 (Excellent) stars',
            'title': 'Brief summary of your review',
            'comment': 'Share your experience with this product'
        }

        # Custom widgets for better styling
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (5, '5 Stars - Excellent'),
                (4, '4 Stars - Good'),
                (3, '3 Stars - Average'),
                (2, '2 Stars - Poor'),
                (1, '1 Star - Terrible')
            ]),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., "Great product, highly recommend!"',
                'maxlength': '100'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us what you liked or disliked about this product...',
                'rows': 5,
                'maxlength': '1000'
            })
        }

    def clean_rating(self):
        """
        Validate rating is between 1-5.

        Why: Extra validation layer (model also validates)
        Defense in depth: Multiple validation points
        """
        rating = self.cleaned_data.get('rating')

        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5 stars.')

        return rating

    def clean_comment(self):
        """
        Validate comment is not empty and has minimum length.

        Why: Ensure quality reviews, prevent spam
        """
        comment = self.cleaned_data.get('comment', '').strip()

        if len(comment) < 10:
            raise forms.ValidationError('Review must be at least 10 characters long.')

        if len(comment) > 1000:
            raise forms.ValidationError('Review cannot exceed 1000 characters.')

        return comment

    def clean_title(self):
        """Validate title is not empty"""
        title = self.cleaned_data.get('title', '').strip()

        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters long.')

        return title
