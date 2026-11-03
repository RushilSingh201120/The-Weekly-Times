from django.db import models
import hmac

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

 
from .models import Article , Newsletter, Publisher


from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.exceptions import PermissionDenied

from .serializers import (
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
)
from .api_permissions import IsOwnerJournalistOrReadOnly



@api_view(["POST"])
@permission_classes([AllowAny])
def approved_article_api(request):
    """Receive approved articles from the internal application."""

    expected_key = getattr(settings, "INTERNAL_API_KEY", "")
    supplied_key = request.headers.get("X-API-Key", "")

    if not expected_key:
        return Response(
            {"error": "API authentication is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if not hmac.compare_digest(supplied_key, expected_key):
        return Response(
            {"error": "Invalid or missing API key."},
            status=status.HTTP_403_FORBIDDEN,
        )

    required_fields = ["id", "title", "content", "author", "status"]
    missing_fields = [
        field for field in required_fields
        if field not in request.data
    ]

    if missing_fields:
        return Response(
            {
                "error": "Missing required fields.",
                "missing_fields": missing_fields,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.data.get("status") != Article.Status.APPROVED:
        return Response(
            {"error": "Only approved articles can be submitted."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Approved article received successfully.",
            "article_id": request.data["id"],
            "title": request.data["title"],
        },
        status=status.HTTP_201_CREATED,
    )


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """List approved articles or create an article as a journalist."""

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Article.objects.select_related(
            "author", "publisher", "approved_by"
        ).filter(status=Article.Status.APPROVED)

    def perform_create(self, serializer):
        if self.request.user.role != "journalist":
            raise PermissionDenied(
                "Only journalists can create articles."
            )

        serializer.save(
            author=self.request.user,
            status=Article.Status.PENDING,
        )


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an article with role restrictions."""

    serializer_class = ArticleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerJournalistOrReadOnly,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == "editor" or user.is_superuser:
            return Article.objects.select_related(
                "author", "publisher", "approved_by"
            ).all()

        if user.role == "journalist":
            return Article.objects.select_related(
                "author", "publisher", "approved_by"
            ).filter(
                models.Q(author=user)
                | models.Q(status=Article.Status.APPROVED)
            )

        return Article.objects.select_related(
            "author", "publisher", "approved_by"
        ).filter(status=Article.Status.APPROVED)

    def perform_update(self, serializer):
        user = self.request.user

        if user.role == "editor" or user.is_superuser:
            serializer.save()
            return

        article = self.get_object()
        if article.author_id != user.id:
            raise PermissionDenied(
                "You can only update your own articles."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "editor" or user.is_superuser:
            instance.delete()
            return

        if user.role == "journalist" and instance.author_id == user.id:
            instance.delete()
            return

        raise PermissionDenied(
            "You can only delete your own articles, unless you are an editor."
        )


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    """List newsletters or create one as a journalist."""

    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Newsletter.objects.select_related(
            "author", "publisher"
        ).all()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ["journalist", "editor"] and not user.is_superuser:
            raise PermissionDenied(
                "Only journalists and editors can create newsletters."
            )

        serializer.save(author=user)


class NewsletterDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a newsletter with role restrictions."""

    serializer_class = NewsletterSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerJournalistOrReadOnly,
    ]

    def get_queryset(self):
        return Newsletter.objects.select_related(
            "author", "publisher"
        ).all()

    def perform_update(self, serializer):
        user = self.request.user

        if user.role == "editor" or user.is_superuser:
            serializer.save()
            return

        newsletter = self.get_object()
        if newsletter.author_id != user.id:
            raise PermissionDenied(
                "You can only update your own newsletters."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "editor" or user.is_superuser:
            instance.delete()
            return

        if user.role == "journalist" and instance.author_id == user.id:
            instance.delete()
            return

        raise PermissionDenied(
            "You can only delete your own newsletters, unless you are an editor."
        )


class PublisherListCreateAPIView(generics.ListCreateAPIView):
    """List publishers; restrict publisher creation to editors."""

    queryset = Publisher.objects.prefetch_related(
        "journalists", "subscribers"
    ).all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "editor" and not user.is_superuser:
            raise PermissionDenied(
                "Only editors can create publishers."
            )

        serializer.save()


class PublisherDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve publishers; restrict changes to editors."""

    queryset = Publisher.objects.prefetch_related(
        "journalists", "subscribers"
    ).all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        if user.role != "editor" and not user.is_superuser:
            raise PermissionDenied(
                "Only editors can update publishers."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != "editor" and not user.is_superuser:
            raise PermissionDenied(
                "Only editors can delete publishers."
            )

        instance.delete()

class SubscribedArticlesAPIView(generics.ListAPIView):
    """
    Return approved articles from publishers and journalists
    followed by the authenticated reader.
    """

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "reader":
            raise PermissionDenied(
                "Only readers can access subscribed articles."
            )

        return Article.objects.filter(
            status=Article.Status.APPROVED
        ).filter(
            models.Q(publisher__subscribers=user)
            | models.Q(author__journalist_subscribers=user)
        ).distinct()
