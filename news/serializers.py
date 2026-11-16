"""Define serializers for news application API data."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Article, Newsletter, Publisher


User = get_user_model()

class ArticleSerializer(serializers.ModelSerializer):
    """Serialize article data for API requests and responses."""
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )
    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
        """Define the article fields and read-only fields."""
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "publisher",
            "publisher_name",
            "status",
            "created_at",
            "updated_at",
            "approved_at",
            "approved_by",
        ]
        read_only_fields = [
            "id",
            "author",
            "status",
            "created_at",
            "updated_at",
            "approved_at",
            "approved_by",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletter data for API requests and responses."""
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )
    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
        """Define the newsletter fields and read-only fields."""
        model = Newsletter
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "publisher",
            "publisher_name",
            "articles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher data for API requests and responses."""
    class Meta:
        """Define the publisher fields and read-only fields."""
        model = Publisher
        fields = [
            "id",
            "name",
            "description",
            "journalists",
            "editors",
            "subscribers",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

class UserSerializer(serializers.ModelSerializer):
    """Serialize user information for API requests and responses."""
    class Meta:
        """Define the user fields and mark them as read-only."""
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = fields