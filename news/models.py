
"""Define the database models for The Weekly Times news application."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Represent a user with a reader, journalist, or editor role."""

    class Role(models.TextChoices):
        """Define the available roles for application users."""

        READER = "reader", "Reader"
        JOURNALIST = "journalist", "Journalist"
        EDITOR = "editor", "Editor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="journalist_subscribers",
        limit_choices_to={"role": "journalist"},
    )

    def __str__(self):
        """Return the username and displayed role of the user."""
        return f"{self.username} ({self.get_role_display()})"


class Publisher(models.Model):
    """Represent a publishing organisation with editors and journalists."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="publishers",
        limit_choices_to={"role": "journalist"},
    )

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="edited_publishers",
        limit_choices_to={"role": "editor"},
    )

    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="subscribed_publishers",
        limit_choices_to={"role": "reader"},
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the publisher's name."""
        return self.name


class Article(models.Model):
    """Represent an article written by a journalist and reviewed by an editor."""

    class Status(models.TextChoices):
        """Define the available approval statuses for articles."""

        PENDING = "pending", "Pending approval"
        APPROVED = "approved", "Approved"

    title = models.CharField(max_length=250)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        limit_choices_to={"role": "journalist"},
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_at = models.DateTimeField(null=True, blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles",
        limit_choices_to={"role": "editor"},
    )

    class Meta:
        """Configure the default ordering and metadata for articles."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return the article's title."""
        return self.title


class Newsletter(models.Model):
    """Represent a newsletter containing articles."""

    title = models.CharField(max_length=250)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to={"role__in": ["journalist", "editor"]},
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters",
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Configure the default ordering for newsletters."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return the newsletter's title."""
        return self.title


class ApprovedArticleLog(models.Model):
    """Record attempts to submit approved articles to the internal API."""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="api_logs",
    )

    response_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    response_body = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Configure log ordering and the article approval permission."""

        ordering = ["-created_at"]
        permissions = [
            ("approve_article", "Can approve article"),
        ]

    def __str__(self):
        """Return a description of the API log and its creation time."""
        return (
            f"API log for {self.article.title} "
            f"({self.created_at:%Y-%m-%d %H:%M})"
        )
