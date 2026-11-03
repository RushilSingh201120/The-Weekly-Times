
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import api_views


urlpatterns = [
    # Internal approved-article submission endpoint
    path(
        "approved/",
        api_views.approved_article_api,
        name="approved_article_api",
    ),

    # Token authentication
    path(
        "token/",
        obtain_auth_token,
        name="api_token_auth",
    ),

        # Articles
    path(
        "articles/",
        api_views.ArticleListCreateAPIView.as_view(),
        name="api_article_list",
    ),
    path(
        "articles/subscribed/",
        api_views.SubscribedArticlesAPIView.as_view(),
        name="api_subscribed_articles",
    ),
    path(
        "articles/<int:pk>/",
        api_views.ArticleDetailAPIView.as_view(),
        name="api_article_detail",
    ),

    # Newsletters
    path(
        "newsletters/",
        api_views.NewsletterListCreateAPIView.as_view(),
        name="api_newsletter_list",
    ),
    path(
        "newsletters/<int:pk>/",
        api_views.NewsletterDetailAPIView.as_view(),
        name="api_newsletter_detail",
    ),

    # Publishers
    path(
        "publishers/",
        api_views.PublisherListCreateAPIView.as_view(),
        name="api_publisher_list",
    ),
    path(
        "publishers/<int:pk>/",
        api_views.PublisherDetailAPIView.as_view(),
        name="api_publisher_detail",
    ),
]
