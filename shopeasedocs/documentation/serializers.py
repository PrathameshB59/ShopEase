from rest_framework import serializers
from .models import (
    DocCategory, Documentation, FAQ, CodeExplanation,
    DailyIssueHelp, AppVersion, DeveloperDiscussion
)


class DocCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocCategory
        fields = ['id', 'name', 'slug', 'icon', 'description', 'order']


class DocumentationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Documentation
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'content', 'audience', 'is_published', 'is_featured',
            'views_count', 'helpful_count', 'not_helpful_count',
            'meta_description', 'created_at', 'updated_at',
        ]


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FAQ
        fields = [
            'id', 'category', 'category_name', 'question', 'answer',
            'audience', 'keywords', 'order', 'view_count',
            'helpful_count', 'not_helpful_count',
        ]


class CodeExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExplanation
        fields = [
            'id', 'title', 'slug', 'description', 'module', 'complexity',
            'file_path', 'line_numbers', 'code_snippet',
            'line_by_line_explanation', 'execution_flow', 'visual_diagram',
            'learning_objectives', 'prerequisites', 'common_mistakes',
            'practice_exercises', 'time_complexity', 'space_complexity',
            'estimated_learning_time', 'views_count',
        ]


class DailyIssueHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyIssueHelp
        fields = [
            'id', 'title', 'slug', 'issue_type', 'problem_description',
            'solution_steps', 'audience', 'views_count',
            'helpful_count', 'not_helpful_count',
        ]


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = [
            'id', 'version_number', 'slug', 'version_type',
            'release_date', 'release_notes', 'new_features',
            'bug_fixes', 'improvements', 'breaking_changes',
            'is_current_version', 'view_count',
        ]


class DeveloperDiscussionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DeveloperDiscussion
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_name',
            'status', 'tags', 'created_at', 'updated_at',
        ]
