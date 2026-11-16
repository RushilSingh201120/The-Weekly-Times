"""Define the views for The Weekly Times news application."""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ArticleForm, RegistrationForm, NewsletterForm
from .models import Article, Publisher, Newsletter
from django.contrib.auth import get_user_model

from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods

from django.contrib.auth.views import LoginView
from django.urls import reverse



def article_list(request):
    """Display approved articles and available newsletters."""

    articles = Article.objects.filter(
        status=Article.Status.APPROVED
    ).select_related("author", "publisher")

    newsletters = Newsletter.objects.select_related(
        "author",
        "publisher",
    ).prefetch_related(
        "articles",
    ).order_by("-created_at")

    return render(
        request,
        "news/article_list.html",
        {
            "articles": articles,
            "newsletters": newsletters,
        },
    )


def article_detail(request, article_id):
    """Display an approved article, or allow its author/editor to view it."""

    article = get_object_or_404(Article, pk=article_id)

    if article.status != Article.Status.APPROVED:
        if not request.user.is_authenticated:
            from django.http import Http404

            raise Http404("Article not found.")

        is_author = article.author_id == request.user.id
        is_editor = (
            request.user.is_superuser
            or request.user.groups.filter(name="Editor").exists()
        )

        if not (is_author or is_editor):
            from django.http import Http404

            raise Http404("Article not found.")

    return render(
        request,
        "news/article_detail.html",
        {"article": article},
    )



@login_required
def journalist_dashboard(request):
    """Display the logged-in journalist's articles and newsletters."""

    if not (
        request.user.is_superuser
        or request.user.role == "journalist"
    ):
        raise PermissionDenied(
            "Only journalists can access this page."
        )

    articles = Article.objects.filter(
        author=request.user
    ).select_related("publisher")

    newsletters = Newsletter.objects.filter(
        author=request.user
    ).select_related("publisher")

    return render(
        request,
        "news/journalist_dashboard.html",
        {
            "articles": articles,
            "newsletters": newsletters,
        },
    )



@login_required
def article_create(request):
    """Allow journalists to submit articles for editorial approval."""

    if not (
        request.user.is_superuser
        or request.user.role == "journalist"
    ):
        raise PermissionDenied(
            "Only journalists can create articles."
        )

    if request.method == "POST":
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = Article.Status.PENDING
            article.approved_by = None
            article.approved_at = None
            article.save()

            return redirect("news:journalist_dashboard")
    else:
        form = ArticleForm()

    return render(
        request,
        "news/article_form.html",
        {"form": form},
    )



@login_required
def article_update(request, article_id):
    """Allow editors to edit any article and journalists to edit their own."""

    if not (
        request.user.is_superuser
        or request.user.role in ["journalist", "editor"]
    ):
        raise PermissionDenied(
            "You do not have permission to edit articles."
        )

    if request.user.role == "journalist" and not request.user.is_superuser:
        article = get_object_or_404(
            Article,
            pk=article_id,
            author=request.user,
        )
    else:
        article = get_object_or_404(
            Article,
            pk=article_id,
        )

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            article = form.save(commit=False)

            # Journalist edits require editorial review again.
            # Editor edits preserve the article's existing status.
            if request.user.role == "journalist":
                article.status = Article.Status.PENDING
                article.approved_by = None
                article.approved_at = None

            article.save()

            if request.user.role == "editor":
                return redirect("news:review_queue")

            return redirect("news:journalist_dashboard")

    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "news/article_form.html",
        {
            "form": form,
            "article": article,
        },
    )



@login_required
def article_delete(request, article_id):
    """Allow editors to delete any article and journalists to delete their own."""

    if not (
        request.user.is_superuser
        or request.user.role in ["journalist", "editor"]
    ):
        raise PermissionDenied(
            "You do not have permission to delete articles."
        )

    if request.user.role == "journalist" and not request.user.is_superuser:
        article = get_object_or_404(
            Article,
            pk=article_id,
            author=request.user,
        )
    else:
        article = get_object_or_404(
            Article,
            pk=article_id,
        )

    if request.method == "POST":
        article.delete()

        if request.user.role == "editor":
            return redirect("news:review_queue")

        return redirect("news:journalist_dashboard")

    return render(
        request,
        "news/article_confirm_delete.html",
        {"article": article},
    )


@login_required
def review_queue(request):
    """Show pending articles to editors."""

    if not (
        request.user.is_superuser
        or request.user.role == "editor"
    ):
        raise PermissionDenied(
            "Only editors can access the review queue."
        )

    articles = Article.objects.filter(
        status=Article.Status.PENDING
    ).select_related(
        "author",
        "publisher",
    ).order_by("created_at")

    return render(
        request,
        "news/review_queue.html",
        {"articles": articles},
    )


@login_required
def approve_article(request, article_id):
    """Allow editors to approve pending articles."""

    if not (
        request.user.is_superuser
        or request.user.role == "editor"
    ):
        raise PermissionDenied(
            "Only editors can approve articles."
        )

    if request.method != "POST":
        raise PermissionDenied(
            "Articles must be approved using the confirmation form."
        )

    article = get_object_or_404(
        Article,
        pk=article_id,
        status=Article.Status.PENDING,
    )

    article.status = Article.Status.APPROVED
    article.approved_by = request.user
    article.approved_at = timezone.now()
    article.save()

    return redirect("news:review_queue")


@login_required
def subscriptions(request):
    """Show journalists and publishers a reader can follow."""

    if not (
        request.user.is_superuser
        or request.user.role == "reader"
    ):
        raise PermissionDenied(
            "Only readers can manage subscriptions."
        )

    User = get_user_model()

    journalists = User.objects.filter(
        role="journalist"
    ).order_by("username")

    publishers = Publisher.objects.all().order_by("name")

    return render(
        request,
        "news/subscriptions.html",
        {
            "journalists": journalists,
            "publishers": publishers,
            "subscribed_journalists": (
                request.user.subscribed_journalists.all()
            ),
            "subscribed_publishers": (
                request.user.subscribed_publishers.all()
            ),
        },
    )


@login_required
def subscribe_journalist(request, journalist_id):
    """Subscribe to or unsubscribe from a journalist."""

    if not (
        request.user.is_superuser
        or request.user.role == "reader"
    ):
        raise PermissionDenied(
            "Only readers can manage subscriptions."
        )

    if request.method != "POST":
        raise PermissionDenied(
            "Subscriptions must be changed using a form."
        )

    User = get_user_model()

    journalist = get_object_or_404(
        User,
        pk=journalist_id,
        role="journalist",
    )

    if request.user.subscribed_journalists.filter(
        pk=journalist.pk
    ).exists():
        request.user.subscribed_journalists.remove(journalist)
    else:
        request.user.subscribed_journalists.add(journalist)

    return redirect("news:subscriptions")


@login_required
def subscribe_publisher(request, publisher_id):
    """Subscribe to or unsubscribe from a publisher."""

    if not (
        request.user.is_superuser
        or request.user.role == "reader"
    ):
        raise PermissionDenied(
            "Only readers can manage subscriptions."
        )

    if request.method != "POST":
        raise PermissionDenied(
            "Subscriptions must be changed using a form."
        )

    publisher = get_object_or_404(
        Publisher,
        pk=publisher_id,
    )

    if request.user.subscribed_publishers.filter(
        pk=publisher.pk
    ).exists():
        request.user.subscribed_publishers.remove(publisher)
    else:
        request.user.subscribed_publishers.add(publisher)

    return redirect("news:subscriptions")


@require_http_methods(["GET", "POST"])
def register(request):
    """Register a new reader or journalist account."""
    if request.user.is_authenticated:
        return redirect("news:article_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your account has been created successfully."
            )

            if user.role == "journalist":
                return redirect("news:journalist_dashboard")

            return redirect("news:article_list")
    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


class RoleBasedLoginView(LoginView):
    """Redirect users to the correct page for their role."""

    template_name = "registration/login.html"

    def get_success_url(self):
        """Return the destination appropriate for the user's role."""
        user = self.request.user

        if user.role == "journalist":
            return reverse("news:journalist_dashboard")

        if user.role == "editor":
            return reverse("news:review_queue")

        return reverse("news:article_list")

    def get_redirect_url(self):
        """Prevent custom redirects from overriding role-based navigation."""
        # Ignore the submitted "next" destination so role-based
        # redirects take priority.
        return ""

@login_required
def newsletter_create(request):
    """Allow journalists to create newsletters."""

    if request.user.role != "journalist":
        messages.error(
            request,
            "Only journalists can create newsletters.",
        )
        return redirect("news:article_list")

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()

            messages.success(
                request,
                "Newsletter created successfully.",
            )
            return redirect("news:journalist_dashboard")
    else:
        form = NewsletterForm()

    return render(
        request,
        "news/newsletter_form.html",
        {"form": form},
    )



@login_required
def newsletter_update(request, newsletter_id):
    """Allow editors to edit any newsletter and journalists their own."""

    if not (
        request.user.is_superuser
        or request.user.role in ["journalist", "editor"]
    ):
        raise PermissionDenied(
            "You do not have permission to edit newsletters."
        )

    if request.user.role == "journalist" and not request.user.is_superuser:
        newsletter = get_object_or_404(
            Newsletter,
            id=newsletter_id,
            author=request.user,
        )
    else:
        newsletter = get_object_or_404(
            Newsletter,
            id=newsletter_id,
        )

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            instance=newsletter,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Newsletter updated successfully.",
            )

            if request.user.role == "editor":
                return redirect("news:editor_newsletter_management")

            return redirect("news:journalist_dashboard")

    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "news/newsletter_form.html",
        {
            "form": form,
            "newsletter": newsletter,
        },
    )


@login_required
def newsletter_delete(request, newsletter_id):
    """Allow editors to delete any newsletter and journalists their own."""

    if not (
        request.user.is_superuser
        or request.user.role in ["journalist", "editor"]
    ):
        raise PermissionDenied(
            "You do not have permission to delete newsletters."
        )

    if request.user.role == "journalist" and not request.user.is_superuser:
        newsletter = get_object_or_404(
            Newsletter,
            id=newsletter_id,
            author=request.user,
        )
    else:
        newsletter = get_object_or_404(
            Newsletter,
            id=newsletter_id,
        )

    if request.method == "POST":
        newsletter.delete()

        messages.success(
            request,
            "Newsletter deleted successfully.",
        )

        if request.user.role == "editor":
            return redirect("news:editor_newsletter_management")

        return redirect("news:journalist_dashboard")

    return render(
        request,
        "news/newsletter_confirm_delete.html",
        {"newsletter": newsletter},
    )



@login_required
def editor_article_management(request):
    """Allow editors to view and manage all articles."""

    if not (
        request.user.is_superuser
        or request.user.role == "editor"
    ):
        raise PermissionDenied(
            "Only editors can manage all articles."
        )

    articles = Article.objects.select_related(
        "author",
        "publisher",
    ).order_by("-created_at")

    return render(
        request,
        "news/editor_article_management.html",
        {"articles": articles},
    )
@login_required
def editor_newsletter_management(request):
    """Allow editors to view and manage all newsletters."""

    if not (
        request.user.is_superuser
        or request.user.role == "editor"
    ):
        raise PermissionDenied(
            "Only editors can manage all newsletters."
        )

    newsletters = Newsletter.objects.select_related(
        "author",
        "publisher",
    ).prefetch_related(
        "articles",
    ).order_by("-created_at")

    return render(
        request,
        "news/editor_newsletter_management.html",
        {"newsletters": newsletters},
    )
@login_required
def newsletter_detail(request, newsletter_id):
    """Display the full newsletter and its selected articles."""

    newsletter = get_object_or_404(
        Newsletter.objects.prefetch_related("articles"),
        id=newsletter_id,
    )

    return render(
        request,
        "news/newsletter_detail.html",
        {
            "newsletter": newsletter,
        },
    )