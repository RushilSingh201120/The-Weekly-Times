"""Define custom permissions for the news application's REST API."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsJournalistOrReadOnly(BasePermission):
    """Allow safe reads, and restrict writes to journalists."""

    def has_permission(self, request, view):
        """Check whether the user may read or create content."""
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "journalist"
        )


class IsOwnerJournalistOrReadOnly(BasePermission):
    """Allow reads, and restrict changes to owners or editors."""

    def has_permission(self, request, view):
        """Check whether the user may access or modify API content."""
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return (
            getattr(request.user, "role", None) in ["journalist", "editor"]
            or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        """Check whether the user may modify the specific object."""
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if getattr(request.user, "role", None) == "editor":
            return True

        return (
            getattr(request.user, "role", None) == "journalist"
            and getattr(obj, "author_id", None) == request.user.id
        )


class IsEditorOrReadOnly(BasePermission):
    """Allow safe reads and restrict writes to editors."""

    def has_permission(self, request, view):
        """Check whether the user may read content or perform editor actions."""
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return (
            getattr(request.user, "role", None) == "editor"
            or request.user.is_superuser
        )
