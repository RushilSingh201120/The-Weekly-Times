"""Handle article status changes, subscriber notifications, and API submissions."""
import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Article, ApprovedArticleLog


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Article)
def remember_previous_article_status(sender, instance, **kwargs):
    """Remember an existing article's status before it is saved."""
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        Article.objects.filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )


@receiver(post_save, sender=Article)
def handle_approved_article(sender, instance, created, **kwargs):
    """Notify subscribers only when an article becomes approved."""

    previous_status = getattr(instance, "_previous_status", None)

    if created or previous_status != Article.Status.PENDING:
        return

    if instance.status != Article.Status.APPROVED:
        return

    article = instance

    # Gather readers subscribed to this journalist.
    journalist_subscribers = (
        article.author.journalist_subscribers
        .filter(is_active=True)
        .exclude(email="")
    )

    recipient_emails = set(
        journalist_subscribers.values_list("email", flat=True)
    )

    # Include readers subscribed to the publisher.
    if article.publisher:
        publisher_subscribers = (
            article.publisher.subscribers
            .filter(is_active=True)
            .exclude(email="")
        )

        recipient_emails.update(
            publisher_subscribers.values_list("email", flat=True)
        )

    # Send one email to each unique subscriber.
    if recipient_emails:
        try:
            send_mail(
                subject=f"New approved article: {article.title}",
                message=(
                    "A new article has been approved on The Weekly Times.\n\n"
                    f"Title: {article.title}\n"
                    f"Journalist: {article.author.username}\n\n"
                    f"{article.content}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=sorted(recipient_emails),
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Email notification failed for article %s",
                article.pk,
            )

    # Submit the approved article to the internal API.
    api_url = getattr(settings, "APPROVED_ARTICLE_API_URL", None)
    api_key = getattr(settings, "INTERNAL_API_KEY", None)

    if not api_url:
        logger.warning(
            "APPROVED_ARTICLE_API_URL is not configured."
        )
        return

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    payload = {
        "id": article.pk,
        "title": article.title,
        "content": article.content,
        "author": article.author.username,
        "publisher": article.publisher.name if article.publisher else None,
        "status": article.status,
        "approved_at": (
            article.approved_at.isoformat()
            if article.approved_at
            else None
        ),
    }

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        ApprovedArticleLog.objects.create(
            article=article,
            response_status=response.status_code,
            response_body=response.text[:5000],
            success=True,
        )

    except requests.RequestException as exc:
        ApprovedArticleLog.objects.create(
            article=article,
            error_message=str(exc)[:5000],
            success=False,
        )

        logger.exception(
            "Internal API submission failed for article %s",
            article.pk,
        )
