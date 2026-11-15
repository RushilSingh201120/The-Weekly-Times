"""Configure the Django news application."""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configure the news application and its startup behaviour."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        """Register role group creation and article notification signals."""
        from django.db.models.signals import post_migrate

        from .roles import create_role_groups
        from . import signals  # Register article notification signals

        post_migrate.connect(
            create_role_groups,
            sender=self,
            dispatch_uid="news.create_role_groups",
        )
