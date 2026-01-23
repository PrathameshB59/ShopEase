from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class DocCategory(models.Model):
    """
    Categories for organizing documentation
    Examples: 'Getting Started', 'API Reference', 'Troubleshooting', 'User Guide'
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., 'bi-book')")
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documentation Category"
        verbose_name_plural = "Documentation Categories"
        ordering = ['order', 'name']
        db_table = 'documentation_category'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Documentation(models.Model):
    """
    Main documentation articles accessible based on audience targeting
    """
    AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('CUSTOMER', 'Customers Only'),
        ('ADMIN', 'Admins Only'),
        ('SUPERUSER', 'Superusers Only'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.ForeignKey(DocCategory, on_delete=models.CASCADE, related_name='documents')
    content = models.TextField(help_text="Main documentation content (supports Markdown and HTML)")
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')

    # Metadata
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_docs')
    is_published = models.BooleanField(default=False, help_text="Published docs are visible to users")
    is_featured = models.BooleanField(default=False, help_text="Show on documentation homepage")

    # Analytics
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)

    # SEO
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated keywords")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Documentation"
        verbose_name_plural = "Documentation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['audience', 'is_published']),
            models.Index(fields=['-created_at']),
        ]
        db_table = 'documentation_documentation'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def helpfulness_ratio(self):
        """Calculate helpful percentage"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100


class CodeExplanation(models.Model):
    """
    Detailed code-level explanations visible ONLY to superusers for learning
    Enhanced with interactive visual learning features
    """
    MODULE_CHOICES = [
        ('ACCOUNTS', 'Accounts App'),
        ('PRODUCTS', 'Products App'),
        ('ORDERS', 'Orders App'),
        ('CART', 'Cart App'),
        ('ADMIN_PANEL', 'Admin Panel'),
        ('CORE', 'Core App'),
        ('DOCUMENTATION', 'Documentation App'),
    ]

    COMPLEXITY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(help_text="Brief description of what this code does")
    module = models.CharField(max_length=20, choices=MODULE_CHOICES)
    file_path = models.CharField(max_length=500, help_text="Relative path to file (e.g., 'shopease/apps/accounts/views.py')")
    line_numbers = models.CharField(max_length=50, blank=True, help_text="Line range (e.g., '145-178')")

    # Code details
    code_snippet = models.TextField(help_text="The actual code being explained")
    detailed_explanation = models.TextField(help_text="Detailed overview explanation")
    why_it_matters = models.TextField(blank=True, help_text="Why this code pattern is important")
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='intermediate')

    # Enhanced visual learning fields
    line_by_line_explanation = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object with line numbers as keys and detailed explanations as values"
    )
    execution_flow = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array describing execution order and flow"
    )
    visual_diagram = models.TextField(
        blank=True,
        help_text="Mermaid.js syntax for flowchart/diagram"
    )
    interactive_demo_url = models.URLField(
        blank=True,
        help_text="URL to interactive demo (e.g., CodePen, JSFiddle)"
    )

    # Learning content
    learning_objectives = models.TextField(
        blank=True,
        help_text="What learners will understand after studying this code"
    )
    prerequisites = models.TextField(
        blank=True,
        help_text="Concepts/topics learners should know before studying this"
    )
    related_concepts = models.TextField(
        blank=True,
        help_text="Related programming concepts and patterns"
    )
    common_mistakes = models.TextField(
        blank=True,
        help_text="Common mistakes developers make with this pattern"
    )
    practice_exercises = models.TextField(
        blank=True,
        help_text="Exercises to practice and reinforce learning"
    )

    # Complexity analysis
    time_complexity = models.CharField(
        max_length=50,
        blank=True,
        help_text="Big O notation for time complexity (e.g., 'O(n)')"
    )
    space_complexity = models.CharField(
        max_length=50,
        blank=True,
        help_text="Big O notation for space complexity (e.g., 'O(1)')"
    )
    estimated_learning_time = models.PositiveIntegerField(
        default=15,
        help_text="Estimated time to learn this code (in minutes)"
    )

    # Related content
    related_docs = models.ManyToManyField(Documentation, blank=True, related_name='related_code_examples')

    # Metadata
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Code Explanation"
        verbose_name_plural = "Code Explanations"
        ordering = ['module', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['module']),
            models.Index(fields=['complexity']),
        ]
        db_table = 'documentation_codeexplanation'

    def __str__(self):
        return f"{self.title} ({self.get_module_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class FAQ(models.Model):
    """
    Frequently Asked Questions accessible to all users or targeted audiences
    """
    category = models.ForeignKey(DocCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()

    # Audience control
    AUDIENCE_CHOICES = Documentation.AUDIENCE_CHOICES
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')

    # SEO
    keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated keywords for search")

    # Display
    order = models.PositiveIntegerField(default=0, help_text="Display order within category")
    status = models.CharField(
        max_length=20,
        choices=[('published', 'Published'), ('draft', 'Draft')],
        default='published'
    )

    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', '-created_at']
        db_table = 'documentation_faq'

    def __str__(self):
        return self.question


class DeveloperDiscussion(models.Model):
    """
    Discussion threads for developers (WhatsApp-like chat feature)
    """
    THREAD_STATUS = [
        ('OPEN', 'Open'),
        ('RESOLVED', 'Resolved'),
        ('ARCHIVED', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Thread description or initial question")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_threads')
    status = models.CharField(max_length=20, choices=THREAD_STATUS, default='OPEN')

    # Categorization
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags (e.g., 'bug, authentication, urgent')")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Developer Discussion"
        verbose_name_plural = "Developer Discussions"
        ordering = ['-last_message_at']
        db_table = 'documentation_developerdiscussion'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def message_count(self):
        """Get total message count for this thread"""
        return self.messages.count()


class DeveloperMessage(models.Model):
    """
    Individual messages within developer discussion threads
    """
    thread = models.ForeignKey(DeveloperDiscussion, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    # Message metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    # Attachments
    attachment = models.FileField(upload_to='developer_chat/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Developer Message"
        verbose_name_plural = "Developer Messages"
        ordering = ['created_at']
        db_table = 'documentation_developermessage'

    def __str__(self):
        return f"{self.author.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AppVersion(models.Model):
    """
    Track application versions and release notes
    """
    VERSION_TYPE = [
        ('major', 'Major Release'),
        ('minor', 'Minor Release'),
        ('patch', 'Patch/Hotfix'),
    ]

    version_number = models.CharField(max_length=20, unique=True, help_text="Semantic versioning (e.g., '1.2.3')")
    slug = models.SlugField(unique=True, max_length=50)
    version_type = models.CharField(max_length=10, choices=VERSION_TYPE)

    # Release information
    release_date = models.DateField()
    release_notes = models.TextField(help_text="Overall release notes (supports Markdown)")

    # Detailed changes
    new_features = models.TextField(blank=True, help_text="List of new features (one per line or Markdown list)")
    bug_fixes = models.TextField(blank=True, help_text="List of bug fixes")
    improvements = models.TextField(blank=True, help_text="List of improvements")
    breaking_changes = models.TextField(blank=True, help_text="Breaking changes that require action")
    migration_guide = models.TextField(blank=True, help_text="Instructions for migrating from previous versions")

    # Metadata
    is_current_version = models.BooleanField(default=False, help_text="Mark as current version (only one should be current)")
    view_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Version"
        verbose_name_plural = "App Versions"
        ordering = ['-release_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-release_date']),
        ]
        db_table = 'documentation_appversion'

    def __str__(self):
        return f"v{self.version_number} ({self.get_version_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"v-{self.version_number}")
        # If this version is marked as current, unmark all others
        if self.is_current_version:
            AppVersion.objects.filter(is_current_version=True).update(is_current_version=False)
        super().save(*args, **kwargs)


class DailyIssueHelp(models.Model):
    """
    Common day-to-day issues and their solutions - accessible to all users
    """
    ISSUE_TYPE = [
        ('ACCOUNT', 'Account Issues'),
        ('ORDER', 'Order Issues'),
        ('PAYMENT', 'Payment Issues'),
        ('PRODUCT', 'Product Issues'),
        ('TECHNICAL', 'Technical Issues'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE)

    # Problem and solution
    problem_description = models.TextField(help_text="Describe the problem")
    solution_steps = models.TextField(help_text="Step-by-step solution")

    # SEO
    keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated keywords for search")

    # Audience targeting
    AUDIENCE_CHOICES = Documentation.AUDIENCE_CHOICES
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')

    # Analytics
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[('published', 'Published'), ('draft', 'Draft')],
        default='published'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Daily Issue Help"
        verbose_name_plural = "Daily Issue Help"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['issue_type']),
            models.Index(fields=['audience', 'status']),
        ]
        db_table = 'documentation_dailyissuehelp'

    def __str__(self):
        return f"{self.title} ({self.get_issue_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def helpfulness_ratio(self):
        """Calculate helpful percentage"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100


class HelpScreenshot(models.Model):
    """
    Screenshots for help articles - supports multiple images per article
    """
    help_article = models.ForeignKey(
        DailyIssueHelp,
        on_delete=models.CASCADE,
        related_name='screenshots'
    )
    image = models.ImageField(
        upload_to='help_screenshots/%Y/%m/',
        help_text="Screenshot showing the issue or solution step"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Description of what this screenshot shows"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for this screenshot"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Help Screenshot"
        verbose_name_plural = "Help Screenshots"
        ordering = ['order', 'uploaded_at']
        db_table = 'documentation_helpscreenshot'

    def __str__(self):
        return f"Screenshot for {self.help_article.title}"


class CodeLearningProgress(models.Model):
    """
    Track user progress through code explanations for personalized learning
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_learning_progress')
    code_explanation = models.ForeignKey(CodeExplanation, on_delete=models.CASCADE, related_name='user_progress')

    # Progress tracking
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(
        default=0,
        help_text="Total time spent in seconds"
    )

    # Detailed progress
    lines_explored = models.JSONField(
        default=list,
        blank=True,
        help_text="List of line numbers the user has explored"
    )
    completed = models.BooleanField(default=False)
    progress_percentage = models.PositiveIntegerField(default=0)

    # Learning notes
    user_notes = models.TextField(
        blank=True,
        help_text="Personal notes from the learner"
    )

    class Meta:
        verbose_name = "Code Learning Progress"
        verbose_name_plural = "Code Learning Progress"
        unique_together = [['user', 'code_explanation']]
        ordering = ['-last_accessed']
        db_table = 'documentation_codelearningprogress'

    def __str__(self):
        status = "Completed" if self.completed else f"{self.progress_percentage}%"
        return f"{self.user.username} - {self.code_explanation.title} ({status})"

    def mark_complete(self):
        """Mark this code explanation as completed"""
        from django.utils import timezone
        self.completed = True
        self.progress_percentage = 100
        self.completed_at = timezone.now()
        self.save()
