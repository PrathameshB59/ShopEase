from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_panel'
    verbose_name = 'Admin Panel'

    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.admin_panel.signals
        except ImportError:
            pass
