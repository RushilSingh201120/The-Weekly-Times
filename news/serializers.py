from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Article, Newsletter, Publisher


User = get_user_model()

class ArticleSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )
    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
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
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )
    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
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
    class Meta:
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
    class Meta:
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