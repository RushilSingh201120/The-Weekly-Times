
from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path(
        "articles/<int:article_id>/",
        views.article_detail,
        name="article_detail",
    ),
    path(
        "journalist/",
        views.journalist_dashboard,
        name="journalist_dashboard",
    ),
    path(
        "journalist/articles/create/",
        views.article_create,
        name="article_create",
    ),
    
    path(
        "journalist/articles/<int:article_id>/edit/",
        views.article_update,
        name="article_update",
    ),
    path(
        "journalist/articles/<int:article_id>/delete/",
        views.article_delete,
        name="article_delete",
    ),
    path(
        "editor/review/",
        views.review_queue,
        name="review_queue",
    ),
    path(
        "editor/articles/<int:article_id>/approve/",
        views.approve_article,
        name="approve_article",
    ),

    path(
         "editor/articles/",
        views.editor_article_management,
        name="editor_article_management",
    ),  

    path(
        "editor/newsletters/",
        views.editor_newsletter_management,
        name="editor_newsletter_management",
    ),

    
    path(
        "subscriptions/",
        views.subscriptions,
        name="subscriptions",
    ),
    path(
        "subscriptions/journalist/<int:journalist_id>/",
        views.subscribe_journalist,
        name="subscribe_journalist",
    ),
    path(
        "subscriptions/publisher/<int:publisher_id>/",
        views.subscribe_publisher,
        name="subscribe_publisher",
    ),

    path("register/", views.register, name="register"),

    path(
        "journalist/articles/create/",
        views.article_create,
        name="article_create",
    ),

    path(
        "journalist/newsletters/create/",
        views.newsletter_create,
        name="newsletter_create",
    ),

    
    path(
     "journalist/newsletters/<int:newsletter_id>/edit/",
     views.newsletter_update,
     name="newsletter_update",
    ),
    path(
     "journalist/newsletters/<int:newsletter_id>/delete/",
     views.newsletter_delete,
     name="newsletter_delete",
    ),
   path(
     "newsletters/<int:newsletter_id>/",
     views.newsletter_detail,
     name="newsletter_detail",
    ),


]
