
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Article,
    ApprovedArticleLog,
    CustomUser,
    Newsletter,
    Publisher,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for users and their roles."""

    fieldsets = UserAdmin.fieldsets + (
        (
            "News Application Role",
            {"fields": ("role", "subscribed_journalists")},
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("News Application Role", {"fields": ("role",)}),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "publisher",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("title", "content", "author__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "created_at")
    search_fields = ("title", "author__username")


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "success",
        "response_status",
        "created_at",
    )
    list_filter = ("success", "created_at")
    readonly_fields = (
        "article",
        "response_status",
        "response_body",
        "success",
        "error_message",
        "created_at",
    )
