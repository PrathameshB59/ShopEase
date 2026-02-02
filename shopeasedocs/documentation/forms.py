from django import forms
from django.contrib.auth.models import User
from .models import (
    DocCategory, Documentation, CodeExplanation, FAQ,
    DeveloperDiscussion, DeveloperMessage, AppVersion, DailyIssueHelp,
    HelpScreenshot, CodeLearningProgress
)


class DocCategoryForm(forms.ModelForm):
    """Form for creating and editing documentation categories"""

    class Meta:
        model = DocCategory
        fields = ['name', 'slug', 'icon', 'description', 'parent', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-slug'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bi-book (Bootstrap icon class)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this category'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from name',
            'icon': 'Bootstrap icon class (e.g., bi-book, bi-gear)',
            'order': 'Lower numbers appear first'
        }


class DocumentationForm(forms.ModelForm):
    """Form for creating and editing documentation articles"""

    editor_type = forms.ChoiceField(
        choices=[('markdown', 'Markdown'), ('richtext', 'Rich Text Editor')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='markdown',
        required=False,
        label='Editor Type'
    )

    class Meta:
        model = Documentation
        fields = [
            'title', 'slug', 'category', 'content', 'audience',
            'is_published', 'is_featured', 'author', 'published_at',
            'meta_description', 'keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter documentation title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-slug'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control doc-editor',
                'rows': 15,
                'placeholder': 'Write your documentation content here...'
            }),
            'audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'author': forms.Select(attrs={
                'class': 'form-select'
            }),
            'published_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'maxlength': '160',
                'placeholder': 'SEO meta description (max 160 chars)'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'keyword1, keyword2, keyword3'
            })
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title',
            'content': 'Supports Markdown and HTML',
            'keywords': 'Comma-separated keywords for SEO'
        }


class CodeExplanationForm(forms.ModelForm):
    """Form for creating and editing code explanations (superuser-only)"""

    class Meta:
        model = CodeExplanation
        fields = [
            'title', 'slug', 'description', 'module', 'file_path', 'line_numbers',
            'code_snippet', 'detailed_explanation', 'why_it_matters', 'complexity',
            'line_by_line_explanation', 'execution_flow', 'visual_diagram',
            'interactive_demo_url', 'learning_objectives', 'prerequisites',
            'related_concepts', 'common_mistakes', 'practice_exercises',
            'time_complexity', 'space_complexity', 'estimated_learning_time',
            'related_docs', 'author'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter code explanation title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of what this code does'
            }),
            'module': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'shopease/apps/accounts/views.py'
            }),
            'line_numbers': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '145-178'
            }),
            'code_snippet': forms.Textarea(attrs={
                'class': 'form-control code-editor',
                'rows': 10,
                'placeholder': 'Paste the code snippet here...',
                'style': 'font-family: monospace;'
            }),
            'detailed_explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Detailed overview explanation of the code...'
            }),
            'why_it_matters': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Why this code pattern is important...'
            }),
            'complexity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'line_by_line_explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '{"1": "Line 1 explanation", "2": "Line 2 explanation"}'
            }),
            'execution_flow': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '[{"step": 1, "line": 1, "description": "..."}, ...]'
            }),
            'visual_diagram': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Mermaid.js syntax for flowchart'
            }),
            'interactive_demo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://codepen.io/...'
            }),
            'learning_objectives': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What learners will understand...'
            }),
            'prerequisites': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Required knowledge before studying this...'
            }),
            'related_concepts': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Related programming concepts...'
            }),
            'common_mistakes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Common mistakes to avoid...'
            }),
            'practice_exercises': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Exercises to practice this concept...'
            }),
            'time_complexity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'O(n) or O(log n)'
            }),
            'space_complexity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'O(1) or O(n)'
            }),
            'estimated_learning_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '15'
            }),
            'related_docs': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'author': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title',
            'file_path': 'Relative path from project root',
            'line_numbers': 'e.g., 145-178 or just 145',
            'estimated_learning_time': 'Estimated time in minutes'
        }


class FAQForm(forms.ModelForm):
    """Form for creating and editing FAQ entries"""

    class Meta:
        model = FAQ
        fields = ['category', 'question', 'answer', 'audience', 'keywords', 'order', 'status']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the question'
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter the answer...'
            }),
            'audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'keyword1, keyword2, keyword3'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'order': 'Lower numbers appear first within category',
            'audience': 'Who can see this FAQ',
            'keywords': 'Comma-separated keywords for search'
        }


class DeveloperDiscussionForm(forms.ModelForm):
    """Form for creating and editing developer discussion threads"""

    class Meta:
        model = DeveloperDiscussion
        fields = ['title', 'description', 'status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discussion title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the topic or initial question...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bug, authentication, urgent'
            })
        }
        help_texts = {
            'tags': 'Comma-separated tags for categorization'
        }


class DeveloperMessageForm(forms.ModelForm):
    """Form for posting messages in developer discussions"""

    class Meta:
        model = DeveloperMessage
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx,.zip'
            })
        }
        help_texts = {
            'attachment': 'Optional file attachment (images, PDFs, docs)'
        }


class AppVersionForm(forms.ModelForm):
    """Form for creating and editing app versions"""

    class Meta:
        model = AppVersion
        fields = [
            'version_number', 'slug', 'version_type', 'release_date', 'release_notes',
            'new_features', 'bug_fixes', 'improvements', 'breaking_changes',
            'migration_guide', 'is_current_version', 'created_by'
        ]
        widgets = {
            'version_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.2.3'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'v-1-2-3'
            }),
            'version_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'release_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'release_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Overall release notes (supports Markdown)...'
            }),
            'new_features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- New feature 1\n- New feature 2'
            }),
            'bug_fixes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- Fixed bug 1\n- Fixed bug 2'
            }),
            'improvements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- Improvement 1\n- Improvement 2'
            }),
            'breaking_changes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- Breaking change 1\n- Breaking change 2'
            }),
            'migration_guide': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Migration instructions from previous versions...'
            }),
            'is_current_version': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'created_by': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'version_number': 'Semantic versioning (e.g., 1.2.3)',
            'slug': 'Leave blank to auto-generate from version number',
            'is_current_version': 'Only one version should be marked as current'
        }


class DailyIssueHelpForm(forms.ModelForm):
    """Form for creating and editing daily issue help articles"""

    class Meta:
        model = DailyIssueHelp
        fields = [
            'title', 'slug', 'issue_type', 'problem_description', 'solution_steps',
            'keywords', 'audience', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter issue title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-slug'
            }),
            'issue_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'problem_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the problem...'
            }),
            'solution_steps': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Step-by-step solution:\n1. First step\n2. Second step\n3. ...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'keyword1, keyword2, keyword3'
            }),
            'audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title',
            'keywords': 'Comma-separated keywords for search'
        }


class SearchForm(forms.Form):
    """Form for searching documentation"""

    query = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documentation...',
            'autocomplete': 'off'
        }),
        label=''
    )

    category = forms.ModelChoiceField(
        queryset=DocCategory.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Filter by Category',
        empty_label='All Categories'
    )

    audience = forms.ChoiceField(
        choices=[('', 'All Audiences')] + Documentation.AUDIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Filter by Audience'
    )
