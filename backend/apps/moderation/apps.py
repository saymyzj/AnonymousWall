from django.apps import AppConfig

class ModerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.moderation'
    verbose_name = '内容审核'

    def ready(self):
        from .services import DFAFilter
        DFAFilter.instance = None  # Will be initialized on first use
