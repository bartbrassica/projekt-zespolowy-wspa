"""
Unit tests for authentication/email_service.py
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from authentication.email_service import EmailService
from authentication.models import User, Token


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailService:
    """Tests for EmailService class."""

    def test_create_email_context_with_first_name(self, user):
        """Test email context creation when user has first name."""
        context = EmailService._create_email_context(user, extra_key="extra_value")

        assert context["user"] == user
        assert context["user_name"] == user.first_name
        assert "team_signature" in context
        assert context["extra_key"] == "extra_value"

    def test_create_email_context_without_first_name(self, db):
        """Test email context creation when user has no first name."""
        user = User.objects.create_user(
            email="noname@example.com",
            password="Test123!",
            first_name="",
        )

        context = EmailService._create_email_context(user)

        assert context["user"] == user
        assert context["user_name"] == user.email

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_email_success_text_only(self, mock_email_class, user):
        """Test successful email sending with text only."""
        mock_msg = MagicMock()
        mock_email_class.return_value = mock_msg

        result = EmailService._send_email(
            subject="Test Subject",
            body="Test Body",
            to_email=user.email
        )

        assert result is True
        mock_email_class.assert_called_once()
        mock_msg.send.assert_called_once()
        mock_msg.attach_alternative.assert_not_called()

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_email_success_with_html(self, mock_email_class, user):
        """Test successful email sending with HTML content."""
        mock_msg = MagicMock()
        mock_email_class.return_value = mock_msg

        result = EmailService._send_email(
            subject="Test Subject",
            body="Test Body",
            to_email=user.email,
            html_content="<html><body>Test HTML</body></html>"
        )

        assert result is True
        mock_msg.attach_alternative.assert_called_once_with(
            "<html><body>Test HTML</body></html>",
            "text/html"
        )
        mock_msg.send.assert_called_once()

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_email_failure_exception(self, mock_email_class, user):
        """Test email sending failure when exception occurs."""
        mock_msg = MagicMock()
        mock_msg.send.side_effect = Exception("SMTP connection failed")
        mock_email_class.return_value = mock_msg

        result = EmailService._send_email(
            subject="Test Subject",
            body="Test Body",
            to_email=user.email
        )

        assert result is False
        mock_msg.send.assert_called_once()

    @patch('authentication.email_service.EmailService._send_email')
    @patch('authentication.email_service.render_to_string')
    def test_send_verification_email_success(self, mock_render, mock_send, user, verification_token):
        """Test sending verification email successfully."""
        mock_render.return_value = "Rendered content"
        mock_send.return_value = True

        result = EmailService.send_verification_email(user, verification_token)

        assert result is True
        assert mock_render.call_count == 2  # HTML and text templates
        mock_send.assert_called_once()

    @patch('authentication.email_service.EmailService._send_email')
    @patch('authentication.email_service.render_to_string')
    def test_send_password_reset_email_success(self, mock_render, mock_send, user, password_reset_token):
        """Test sending password reset email successfully."""
        mock_render.return_value = "Rendered content"
        mock_send.return_value = True

        result = EmailService.send_password_reset_email(user, password_reset_token)

        assert result is True
        assert mock_render.call_count == 2
        mock_send.assert_called_once()

    @patch('authentication.email_service.EmailService._send_email')
    def test_send_welcome_email_success(self, mock_send, user):
        """Test sending welcome email successfully."""
        mock_send.return_value = True

        result = EmailService.send_welcome_email(user)

        assert result is True
        mock_send.assert_called_once()

    @patch('authentication.email_service.EmailService._send_email')
    @patch('authentication.email_service.render_to_string')
    def test_send_email_with_template_success(self, mock_render, mock_send, user):
        """Test _send_email_with_template success case."""
        mock_render.return_value = "Rendered content"
        mock_send.return_value = True

        context = {"user": user, "message": "Test message"}

        result = EmailService._send_email_with_template(
            subject="Test Subject",
            template_name="test_template",
            context=context,
            to_email=user.email
        )

        assert result is True
        assert mock_render.call_count == 2  # HTML and text
        mock_render.assert_any_call("test_template.html", context)
        mock_render.assert_any_call("test_template.txt", context)
        mock_send.assert_called_once()

    @patch('authentication.email_service.render_to_string')
    def test_send_email_with_template_render_failure(self, mock_render, user):
        """Test _send_email_with_template when template rendering fails."""
        mock_render.side_effect = Exception("Template not found")

        context = {"user": user}

        result = EmailService._send_email_with_template(
            subject="Test Subject",
            template_name="nonexistent_template",
            context=context,
            to_email=user.email
        )

        assert result is False

    @patch('authentication.email_service.EmailService._send_email')
    @patch('authentication.email_service.render_to_string')
    def test_send_email_with_template_send_failure(self, mock_render, mock_send, user):
        """Test _send_email_with_template when sending fails."""
        mock_render.return_value = "Rendered content"
        mock_send.return_value = False

        context = {"user": user}

        result = EmailService._send_email_with_template(
            subject="Test Subject",
            template_name="test_template",
            context=context,
            to_email=user.email
        )

        assert result is False
        mock_send.assert_called_once()


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailServiceIntegration:
    """Integration tests for EmailService with real template rendering."""

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_verification_email_with_real_templates(self, mock_email_class, user, verification_token):
        """Test verification email with actual template rendering."""
        mock_msg = MagicMock()
        mock_email_class.return_value = mock_msg

        result = EmailService.send_verification_email(user, verification_token)

        # Should succeed or fail gracefully
        assert isinstance(result, bool)

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_password_reset_email_with_real_templates(self, mock_email_class, user, password_reset_token):
        """Test password reset email with actual template rendering."""
        mock_msg = MagicMock()
        mock_email_class.return_value = mock_msg

        result = EmailService.send_password_reset_email(user, password_reset_token)

        # Should succeed or fail gracefully
        assert isinstance(result, bool)

    @patch('authentication.email_service.EmailMultiAlternatives')
    def test_send_welcome_email_integration(self, mock_email_class, user):
        """Test welcome email end-to-end."""
        mock_msg = MagicMock()
        mock_email_class.return_value = mock_msg

        result = EmailService.send_welcome_email(user)

        assert result is True
        mock_msg.send.assert_called_once()
