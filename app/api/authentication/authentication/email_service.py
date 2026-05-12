from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .config import config
from .consts import EmailConstants, EmailMessages
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def _create_email_context(user: User, **kwargs: Any) -> dict[str, Any]:
        """
        Create base email context.

        :param user: User instance
        :param kwargs: Additional context variables
        :return: Email context dictionary
        """
        context = {
            "user": user,
            "user_name": user.first_name or user.email,
            "team_signature": EmailConstants.TEAM_SIGNATURE.value,
        }
        context.update(kwargs)
        return context

    @staticmethod
    def _send_email(
        subject: str, body: str, to_email: str, html_content: str | None = None
    ) -> bool:
        """
        Send email with given parameters.

        :param subject: Email subject
        :param body: Email body (text)
        :param to_email: Recipient email
        :param html_content: Optional HTML content
        :return: True if sent successfully, False otherwise
        """
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=config.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )

            if html_content:
                msg.attach_alternative(html_content, "text/html")

            msg.send()
            logger.info(f"Email '{subject}' sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email '{subject}' to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(user: User, token: Any) -> bool:
        """
        Send account verification email to user.

        :param user: User instance
        :param token: Verification token
        :return: True if sent successfully, False otherwise
        """
        verification_url = f"{config.FRONTEND_URL}/verify-email?token={token.token}"

        context = EmailService._create_email_context(
            user, verification_url=verification_url, token=token.token
        )

        html_content = render_to_string(
            EmailConstants.VERIFICATION_TEMPLATE_HTML.value, context
        )
        text_content = render_to_string(
            EmailConstants.VERIFICATION_TEMPLATE_TXT.value, context
        )

        return EmailService._send_email(
            subject=EmailConstants.VERIFICATION_SUBJECT.value,
            body=text_content,
            to_email=user.email,
            html_content=html_content,
        )

    @staticmethod
    def send_password_reset_email(user: User, token: Any) -> bool:
        """
        Send password reset email to user.

        :param user: User instance
        :param token: Password reset token
        :return: True if sent successfully, False otherwise
        """
        reset_url = f"{config.FRONTEND_URL}/reset-password?token={token.token}"

        context = EmailService._create_email_context(user, reset_url=reset_url)

        html_content = render_to_string('emails/password_reset.html', context)
        text_content = render_to_string('emails/password_reset.txt', context)

        return EmailService._send_email(
            subject=EmailConstants.PASSWORD_RESET_SUBJECT.value,
            body=text_content,
            to_email=user.email,
            html_content=html_content,
        )

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """
        Send welcome email after successful verification.

        :param user: User instance
        :return: True if sent successfully, False otherwise
        """
        context = EmailService._create_email_context(user, app_url=config.FRONTEND_URL)

        text_content = EmailMessages.WELCOME_BODY.value.format(**context)

        return EmailService._send_email(
            subject=EmailConstants.WELCOME_SUBJECT.value,
            body=text_content,
            to_email=user.email,
        )

    @staticmethod
    def _send_email_with_template(
        subject: str, template_name: str, context: dict[str, Any], to_email: str
    ) -> bool:
        """
        Send email using HTML and text templates.

        :param subject: Email subject
        :param template_name: Template name (without extension)
        :param context: Template context
        :param to_email: Recipient email
        :return: True if sent successfully, False otherwise
        """
        try:
            html_content = render_to_string(f"{template_name}.html", context)
            text_content = render_to_string(f"{template_name}.txt", context)

            return EmailService._send_email(
                subject=subject,
                body=text_content,
                to_email=to_email,
                html_content=html_content,
            )

        except Exception as e:
            logger.error(
                f"Failed to render email templates '{template_name}': {str(e)}"
            )
            return False
