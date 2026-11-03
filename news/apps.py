
from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        from django.db.models.signals import post_migrate

        from .roles import create_role_groups
        from . import signals  # Register article notification signals

        post_migrate.connect(
            create_role_groups,
            sender=self,
            dispatch_uid="news.create_role_groups",
        )
