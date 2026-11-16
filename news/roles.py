"""Create role groups and assign users to groups based on their roles."""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Article, Newsletter


def create_role_groups(sender, **kwargs):
    """Create the Reader, Journalist, and Editor groups with permissions."""

    reader_group, _ = Group.objects.get_or_create(name="Reader")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    editor_group, _ = Group.objects.get_or_create(name="Editor")

    article_type = ContentType.objects.get_for_model(Article)
    newsletter_type = ContentType.objects.get_for_model(Newsletter)

    # Readers can view articles and newsletters.
    reader_permissions = Permission.objects.filter(
        content_type__in=[article_type, newsletter_type],
        codename__in=["view_article", "view_newsletter"],
    )
    reader_group.permissions.set(reader_permissions)

    # Journalists can add, view, change, and delete articles and newsletters.
    journalist_permissions = Permission.objects.filter(
        content_type__in=[article_type, newsletter_type],
        codename__in=[
            "add_article",
            "view_article",
            "change_article",
            "delete_article",
            "add_newsletter",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
    )
    journalist_group.permissions.set(journalist_permissions)

    # Editors can review and manage articles and newsletters.
    editor_permissions = Permission.objects.filter(
        content_type__in=[article_type, newsletter_type],
        codename__in=[
            "view_article",
            "change_article",
            "delete_article",
            "approve_article",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
    )
    editor_group.permissions.set(editor_permissions)


from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_user_role_group(sender, instance, **kwargs):
    """Keep a user's group membership aligned with their role."""

    if not instance.pk:
        return

    role_to_group = {
        CustomUser.Role.READER: "Reader",
        CustomUser.Role.JOURNALIST: "Journalist",
        CustomUser.Role.EDITOR: "Editor",
    }

    group_name = role_to_group.get(instance.role)

    if not group_name:
        return

    from django.contrib.auth.models import Group

    group = Group.objects.filter(name=group_name).first()

    if group:
        instance.groups.set([group])
