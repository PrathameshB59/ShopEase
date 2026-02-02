from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    DocCategory, Documentation, FAQ, CodeExplanation,
    DailyIssueHelp, AppVersion, DeveloperDiscussion
)
from .serializers import (
    DocCategorySerializer, DocumentationSerializer, FAQSerializer,
    CodeExplanationSerializer, DailyIssueHelpSerializer,
    AppVersionSerializer, DeveloperDiscussionSerializer
)


class DocCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocCategory.objects.filter(is_active=True).order_by('order')
    serializer_class = DocCategorySerializer


class DocumentationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Documentation.objects.filter(
        is_published=True
    ).select_related('category').order_by('-updated_at')
    serializer_class = DocumentationSerializer
    lookup_field = 'slug'


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(
        status='published'
    ).select_related('category').order_by('order')
    serializer_class = FAQSerializer


class CodeExplanationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CodeExplanation.objects.all().order_by('module', 'title')
    serializer_class = CodeExplanationSerializer
    lookup_field = 'slug'


class DailyIssueHelpViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyIssueHelp.objects.filter(
        status='published'
    ).order_by('-created_at')
    serializer_class = DailyIssueHelpSerializer


class AppVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AppVersion.objects.all().order_by('-release_date')
    serializer_class = AppVersionSerializer


class DeveloperDiscussionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeveloperDiscussion.objects.all().select_related(
        'created_by'
    ).order_by('-last_message_at')
    serializer_class = DeveloperDiscussionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
