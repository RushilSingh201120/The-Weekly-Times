"""Test news application functionality and API permissions."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.test import override_settings
from .models import ApprovedArticleLog
import requests

from rest_framework.test import APIClient

from .models import Article, Publisher, Newsletter


User = get_user_model()


class NewsAPIPermissionTests(TestCase):
    """Test role-based access to the article API."""

    def setUp(self):
        """Create test users, a publisher, and sample articles."""
        self.reader = User.objects.create_user(
            username="test_reader",
            password="TestPassword123!",
            email="reader@example.com",
            role="reader",
        )

        self.journalist = User.objects.create_user(
            username="test_journalist",
            password="TestPassword123!",
            role="journalist",
        )

        self.editor = User.objects.create_user(
            username="test_editor",
            password="TestPassword123!",
            role="editor",
        )

        self.publisher = Publisher.objects.create(
            
            name="Test Publisher",
            description="Publisher for automated tests.",
        )

        self.publisher.subscribers.add(self.reader)

        self.approved_article = Article.objects.create(
            title="Approved Test Article",
            content="This article is approved.",
            author=self.journalist,
            publisher=self.publisher,
            status=Article.Status.APPROVED,
            approved_by=self.editor,
        )

        self.pending_article = Article.objects.create(
            title="Pending Test Article",
            content="This article is awaiting approval.",
            author=self.journalist,
            publisher= self.publisher,
            status=Article.Status.PENDING,
        )

        self.client = APIClient()

    def test_unauthenticated_user_cannot_view_articles(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 401)

    def test_reader_can_view_approved_articles(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        article_ids = [item["id"] for item in response.data]
        self.assertIn(self.approved_article.id, article_ids)
        self.assertNotIn(self.pending_article.id, article_ids)

    def test_journalist_can_create_article(self):
        self.client.force_authenticate(user=self.journalist)

        response = self.client.post(
            "/api/articles/",
            {
                "title": "New Test Article",
                "content": "Created through an automated test.",
                "publisher": self.publisher.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["author"], self.journalist.id)
        self.assertEqual(
            response.data["status"],
            Article.Status.PENDING,
        )

    def test_reader_cannot_create_article(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post(
            "/api/articles/",
            {
                "title": "Reader Test Article",
                "content": "A reader should not create this.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_view_pending_article(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.get(
            f"/api/articles/{self.pending_article.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_journalist_can_update_own_article(self):
        self.client.force_authenticate(user=self.journalist)

        response = self.client.patch(
            f"/api/articles/{self.pending_article.id}/",
            {"title": "Updated Test Article"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["title"],
            "Updated Test Article",
        )

    def test_reader_cannot_update_article(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.patch(
            f"/api/articles/{self.approved_article.id}/",
            {"title": "Reader Attempt"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("news.signals.requests.post")
    @patch("news.signals.send_mail")
    def test_editor_can_approve_pending_article(
        self, mock_send_mail, mock_post
    ):
        mock_post.return_value.status_code = 201
        mock_post.return_value.text = "Created"
        mock_post.return_value.raise_for_status.return_value = None

        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
            "news:approve_article",
             args=[self.pending_article.id]
            )
        )

        self.assertEqual(response.status_code, 302)

        self.pending_article.refresh_from_db()

        self.assertEqual(
         self.pending_article.status,
         Article.Status.APPROVED
        )
        self.assertEqual(self.pending_article.approved_by, self.editor)
        self.assertIsNotNone(self.pending_article.approved_at)

        mock_send_mail.assert_called_once()
        mock_post.assert_called_once()

    def test_reader_cannot_approve_article(self):
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse(
                "news:approve_article",
                args=[self.pending_article.id],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_journalist_cannot_update_another_journalists_article(self):
        other_journalist = User.objects.create_user(
            username="other_journalist",
            password="TestPassword123!",
            role="journalist",
        )

        other_article = Article.objects.create(
            title="Another Journalist Article",
            content="This belongs to another journalist.",
            author=other_journalist,
            status=Article.Status.PENDING,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.patch(
            f"/api/articles/{other_article.id}/",
            {"title": "Unauthorised Update"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_journalist_cannot_delete_another_journalists_article(self):
        other_journalist = User.objects.create_user(
            username="delete_test_journalist",
            password="TestPassword123!",
            role="journalist",
        )

        other_article = Article.objects.create(
            title="Article Protected from Deletion",
            content="This belongs to another journalist.",
            author=other_journalist,
            status=Article.Status.PENDING,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.delete(
            f"/api/articles/{other_article.id}/"
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Article.objects.filter(id=other_article.id).exists()
        )

    def test_editor_can_delete_another_journalists_article(self):
        other_journalist = User.objects.create_user(
            username="editor_delete_test",
            password="TestPassword123!",
            role="journalist",
        )

        other_article = Article.objects.create(
            title="Article for Editor Deletion",
            content="An editor should be able to delete this.",
            author=other_journalist,
            status=Article.Status.PENDING,
        )

        self.client.force_authenticate(user=self.editor)

        response = self.client.delete(
            f"/api/articles/{other_article.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Article.objects.filter(id=other_article.id).exists()
        )
    
    def test_reader_can_view_subscribed_approved_articles(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/articles/subscribed/")

        self.assertEqual(response.status_code, 200)

        article_ids = [item["id"] for item in response.data]

        self.assertIn(self.approved_article.id, article_ids)
        self.assertNotIn(self.pending_article.id, article_ids)        
       
    def test_journalist_cannot_access_subscribed_articles(self):
        self.client.force_authenticate(user=self.journalist)

        response = self.client.get("/api/articles/subscribed/")

        self.assertEqual(response.status_code, 403)     

    
    def test_user_can_obtain_api_token(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "test_reader",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)     

    def test_reader_cannot_create_newsletter(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post(
            "/api/newsletters/",
            {
                "title": "Reader Test Newsletter",
                "content": "A reader should not create this newsletter.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        
    def test_reader_can_view_newsletters(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/newsletters/")

        self.assertEqual(response.status_code, 200)           
      
    def test_journalist_can_create_newsletter(self):
        self.client.force_authenticate(user=self.journalist)

        response = self.client.post(
            "/api/newsletters/",
            {
                "title": "Journalist Test Newsletter",
                "content": "A newsletter created by a journalist.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["author"],
            self.journalist.id,
        )     
   
    def test_journalist_can_update_own_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Original Newsletter",
            content="Original newsletter content.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.patch(
            f"/api/newsletters/{newsletter.id}/",
            {"title": "Updated Newsletter"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Newsletter")

    def test_journalist_cannot_update_another_journalists_newsletter(self):
        other_journalist = User.objects.create_user(
            username="newsletter_owner",
            password="TestPassword123!",
            role="journalist",
        )

        newsletter = Newsletter.objects.create(
            title="Another Journalist Newsletter",
            content="This belongs to another journalist.",
            author=other_journalist,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.patch(
            f"/api/newsletters/{newsletter.id}/",
            {"title": "Unauthorised Update"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_update_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Protected Newsletter",
            content="Readers cannot edit this.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.reader)

        response = self.client.patch(
            f"/api/newsletters/{newsletter.id}/",
            {"title": "Reader Attempt"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_delete_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Protected Newsletter",
            content="Readers cannot delete this.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.reader)

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_journalist_can_delete_own_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Newsletter to Delete",
            content="Created by the journalist.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Newsletter.objects.filter(id=newsletter.id).exists()
        )

    def test_journalist_cannot_delete_another_journalists_newsletter(self):
        other_journalist = User.objects.create_user(
            username="newsletter_delete_owner",
            password="TestPassword123!",
            role="journalist",
        )

        newsletter = Newsletter.objects.create(
            title="Protected Newsletter",
            content="Owned by another journalist.",
            author=other_journalist,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/"
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Newsletter.objects.filter(id=newsletter.id).exists()
        )

    def test_editor_can_update_another_journalists_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Journalist Newsletter",
            content="Original content.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            f"/api/newsletters/{newsletter.id}/",
            {"title": "Editor Updated Newsletter"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Editor Updated Newsletter")

    def test_editor_can_delete_another_journalists_newsletter(self):
        newsletter = Newsletter.objects.create(
            title="Newsletter for Editor Deletion",
            content="An editor can delete this.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.editor)

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Newsletter.objects.filter(id=newsletter.id).exists()
        )

    def test_newsletter_can_be_linked_to_articles(self):
        newsletter = Newsletter.objects.create(
            title="Newsletter with Articles",
            content="A newsletter containing articles.",
            author=self.journalist,
        )

        self.client.force_authenticate(user=self.journalist)

        response = self.client.patch(
            f"/api/newsletters/{newsletter.id}/",
            {"articles": [self.approved_article.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        newsletter.refresh_from_db()
        self.assertTrue(
            newsletter.articles.filter(
                id=self.approved_article.id
            ).exists()
        )
   
    def test_reader_cannot_create_publisher(self):
        self.client.force_authenticate(user=self.reader)

        response = self.client.post(
            "/api/publishers/",
            {
                "name": "Reader Publisher",
                "description": "A reader should not create this.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_journalist_cannot_create_publisher(self):
        self.client.force_authenticate(user=self.journalist)

        response = self.client.post(
            "/api/publishers/",
            {
                "name": "Journalist Publisher",
                "description": "A journalist should not create this.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_create_publisher(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.post(
            "/api/publishers/",
            {
                "name": "Editor Test Publisher",
                "description": "Created by an editor.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_editor_can_update_publisher(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            f"/api/publishers/{self.publisher.id}/",
            {"name": "Updated Test Publisher"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Test Publisher")

    def test_editor_can_delete_publisher(self):
        publisher = Publisher.objects.create(
            name="Publisher to Delete",
            description="Created for deletion testing.",
        )

        self.client.force_authenticate(user=self.editor)

        response = self.client.delete(
            f"/api/publishers/{publisher.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Publisher.objects.filter(id=publisher.id).exists()
        )

    @override_settings(
        APPROVED_ARTICLE_API_URL="https://example.com/api/approved/",
        INTERNAL_API_KEY="test-api-key",
    )
    @patch("news.signals.requests.post")
    @patch("news.signals.send_mail")
    def test_approval_sends_email_to_unique_subscribers(
        self, mock_send_mail, mock_post
    ):
        mock_post.return_value.status_code = 201
        mock_post.return_value.text = "Created"
        mock_post.return_value.raise_for_status.return_value = None

        # Create another reader subscribed to the journalist.
        second_reader = User.objects.create_user(
            username="second_reader",
            password="TestPassword123!",
            email="second@example.com",
            role="reader",
        )

        # Subscribe both readers to the journalist.
        self.journalist.journalist_subscribers.add(
            self.reader,
            second_reader,
        )

        # The first reader is already subscribed to the publisher.
        # This tests that duplicate email addresses are removed.
        self.publisher.subscribers.add(second_reader)

        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
                "news:approve_article",
                args=[self.pending_article.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        mock_send_mail.assert_called_once()

        sent_recipients = mock_send_mail.call_args.kwargs[
            "recipient_list"
        ]

        self.assertEqual(
            sorted(sent_recipients),
            ["reader@example.com", "second@example.com"],
        )

        mock_post.assert_called_once()

    @override_settings(
        APPROVED_ARTICLE_API_URL="https://example.com/api/approved/",
        INTERNAL_API_KEY="test-api-key",
    )
        
    @patch("news.signals.requests.post")
    @patch("news.signals.send_mail")
    def test_email_failure_does_not_prevent_api_submission(
        self, mock_send_mail, mock_post
    ):
        mock_send_mail.side_effect = Exception("Email service unavailable")

        mock_post.return_value.status_code = 201
        mock_post.return_value.text = "Created"
        mock_post.return_value.raise_for_status.return_value = None

        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
                "news:approve_article",
                args=[self.pending_article.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        mock_send_mail.assert_called_once()
        mock_post.assert_called_once()

        self.pending_article.refresh_from_db()

        self.assertEqual(
            self.pending_article.status,
            Article.Status.APPROVED,
        )    
    @override_settings(
        APPROVED_ARTICLE_API_URL="https://example.com/api/approved/",
        INTERNAL_API_KEY="test-api-key",
    )
    @patch("news.signals.requests.post")
    @patch("news.signals.send_mail")
    def test_api_failure_is_recorded(
        self, mock_send_mail, mock_post
    ):
        mock_post.side_effect = requests.RequestException(
            "Internal API unavailable"
        )

        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
                "news:approve_article",
                args=[self.pending_article.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        mock_send_mail.assert_called_once()
        mock_post.assert_called_once()

        log = ApprovedArticleLog.objects.get(
            article=self.pending_article
        )

        self.assertFalse(log.success)
        self.assertIn(
            "Internal API unavailable",
            log.error_message,
        )     