from django.contrib import admin
from .models import (
    DocCategory, Documentation, CodeExplanation, FAQ,
    DeveloperDiscussion, DeveloperMessage, AppVersion, DailyIssueHelp,
    HelpScreenshot, CodeLearningProgress
)


@admin.register(DocCategory)
class DocCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'audience', 'is_published', 'is_featured', 'author', 'views_count', 'created_at']
    list_filter = ['audience', 'is_published', 'is_featured', 'category']
    search_fields = ['title', 'content', 'keywords']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'audience')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'author', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views_count', 'helpful_count', 'not_helpful_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CodeExplanation)
class CodeExplanationAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'complexity', 'author', 'views_count', 'created_at']
    list_filter = ['module', 'complexity']
    search_fields = ['title', 'detailed_explanation', 'code_snippet']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    filter_horizontal = ['related_docs']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'audience', 'order', 'status', 'view_count']
    list_filter = ['audience', 'status', 'category']
    search_fields = ['question', 'answer']
    readonly_fields = ['view_count', 'helpful_count', 'not_helpful_count']
    ordering = ['order', '-created_at']


@admin.register(DeveloperDiscussion)
class DeveloperDiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'message_count', 'created_at', 'last_message_at']
    list_filter = ['status']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'last_message_at']


@admin.register(DeveloperMessage)
class DeveloperMessageAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at', 'edited_at']


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['version_number', 'version_type', 'release_date', 'is_current_version', 'created_by']
    list_filter = ['version_type', 'is_current_version']
    search_fields = ['version_number', 'release_notes']
    prepopulated_fields = {'slug': ('version_number',)}
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    fieldsets = (
        ('Version Information', {
            'fields': ('version_number', 'slug', 'version_type', 'release_date', 'is_current_version')
        }),
        ('Release Notes', {
            'fields': ('release_notes',)
        }),
        ('Detailed Changes', {
            'fields': ('new_features', 'bug_fixes', 'improvements', 'breaking_changes', 'migration_guide')
        }),
        ('Metadata', {
            'fields': ('created_by', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyIssueHelp)
class DailyIssueHelpAdmin(admin.ModelAdmin):
    list_display = ['title', 'issue_type', 'audience', 'status', 'views_count', 'created_at']
    list_filter = ['issue_type', 'audience', 'status']
    search_fields = ['title', 'problem_description', 'solution_steps']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']


@admin.register(HelpScreenshot)
class HelpScreenshotAdmin(admin.ModelAdmin):
    list_display = ['help_article', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'help_article__title']
    ordering = ['help_article', 'order']


@admin.register(CodeLearningProgress)
class CodeLearningProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'code_explanation', 'progress_percentage', 'completed', 'time_spent', 'last_accessed']
    list_filter = ['completed', 'last_accessed']
    search_fields = ['user__username', 'code_explanation__title']
    readonly_fields = ['started_at', 'last_accessed', 'completed_at', 'time_spent']
    ordering = ['-last_accessed']
