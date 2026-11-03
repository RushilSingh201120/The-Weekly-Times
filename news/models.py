
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with reader, journalist, and editor roles."""

    class Role(models.TextChoices):
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
        return f"{self.username} ({self.get_role_display()})"


class Publisher(models.Model):
    """A publishing organisation with editors and journalists."""

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
        return self.name


class Article(models.Model):
    """An article written by a journalist and reviewed by an editor."""

    class Status(models.TextChoices):
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
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """A newsletter containing articles, created by a journalist or editor."""

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
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ApprovedArticleLog(models.Model):
    """Records attempts to send approved articles to the internal API."""

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
        ordering = ["-created_at"]
        permissions = [
            ("approve_article", "Can approve article"),
        ]

    def __str__(self):
        return (
            f"API log for {self.article.title} "
            f"({self.created_at:%Y-%m-%d %H:%M})"
        )
