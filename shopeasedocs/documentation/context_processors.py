from documentation.models import CodeExplanation, CodeLearningProgress


def learning_progress(request):
    """Add learning progress data to template context for superusers."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return {}

    total = CodeExplanation.objects.count()
    if total == 0:
        return {'learning_total': 0, 'learning_completed': 0, 'learning_percentage': 0}

    completed = CodeLearningProgress.objects.filter(
        user=request.user, completed=True
    ).count()
    percentage = int((completed / total) * 100)

    return {
        'learning_total': total,
        'learning_completed': completed,
        'learning_percentage': percentage,
    }
