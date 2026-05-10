from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User
from datetime import timedelta
import logging
from typing import Any

from .models import PasswordExpirationNotification, PasswordEntry
from .email_service import EmailService
from .config import config
from .consts import PasswordExpirationConstants
from .utils import get_date_range_for_day, serialize_password_data

logger = logging.getLogger(__name__)


class PasswordExpirationManager:
    """Manages password expiration notifications."""

    @staticmethod
    def get_passwords_expiring_in_days(days: int) -> QuerySet[PasswordEntry]:
        """
        Get passwords expiring in exactly N days.

        :param days: Number of days from now
        :return: QuerySet of PasswordEntry objects
        """
        target_date = timezone.now().date() + timedelta(days=days)
        start_of_day, end_of_day = get_date_range_for_day(target_date)

        return PasswordEntry.objects.filter(
            expires_at__range=(start_of_day, end_of_day), expires_at__isnull=False
        ).select_related("user")

    @staticmethod
    def get_expired_passwords() -> QuerySet[PasswordEntry]:
        """
        Get passwords that expired today.

        :return: QuerySet of PasswordEntry objects
        """
        today = timezone.now().date()
        start_of_day, end_of_day = get_date_range_for_day(today)

        return PasswordEntry.objects.filter(
            expires_at__range=(start_of_day, end_of_day), expires_at__isnull=False
        ).select_related("user")

    @staticmethod
    def has_notification_been_sent(
        password_entry: PasswordEntry, notification_type: str
    ) -> bool:
        """
        Check if notification has already been sent.

        :param password_entry: Password entry to check
        :param notification_type: Type of notification
        :return: True if notification was already sent
        """
        return PasswordExpirationNotification.objects.filter(
            password_entry=password_entry,
            notification_type=notification_type,
            email_sent_successfully=True,
        ).exists()

    @staticmethod
    def _get_email_config(notification_type: str) -> tuple[str, str]:
        """
        Get email subject and template for notification type.

        :param notification_type: Type of notification
        :return: Tuple of (subject, template_name)
        :raises ValueError: If notification type is unknown
        """
        config_map = {
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value: (
                PasswordExpirationConstants.SUBJECT_3_DAYS.value,
                PasswordExpirationConstants.TEMPLATE_3_DAYS.value,
            ),
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value: (
                PasswordExpirationConstants.SUBJECT_1_DAY.value,
                PasswordExpirationConstants.TEMPLATE_1_DAY.value,
            ),
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value: (
                PasswordExpirationConstants.SUBJECT_EXPIRED.value,
                PasswordExpirationConstants.TEMPLATE_EXPIRED.value,
            ),
        }

        if notification_type not in config_map:
            raise ValueError(f"Unknown notification type: {notification_type}")

        return config_map[notification_type]

    @staticmethod
    def _create_email_context(
        user: User, passwords_data: list[dict[str, Any]], notification_type: str
    ) -> dict[str, Any]:
        """
        Create context for email template.

        :param user: User receiving the notification
        :param passwords_data: List of password data dictionaries
        :param notification_type: Type of notification
        :return: Email template context
        """
        return {
            "user": user,
            "passwords": passwords_data,
            "notification_type": notification_type,
            "dashboard_url": f"{config.FRONTEND_URL}/passwords",
            "total_count": len(passwords_data),
        }

    @staticmethod
    def send_expiration_email(
        user: User, passwords_data: list[dict[str, Any]], notification_type: str
    ) -> bool:
        """
        Send password expiration email.

        :param user: User to send email to
        :param passwords_data: List of password data dictionaries
        :param notification_type: Type of notification
        :return: True if email sent successfully
        """
        try:
            subject, template_name = PasswordExpirationManager._get_email_config(
                notification_type
            )
            context = PasswordExpirationManager._create_email_context(
                user, passwords_data, notification_type
            )

            return EmailService._send_email_with_template(
                subject=subject,
                template_name=template_name,
                context=context,
                to_email=user.email,
            )

        except ValueError as e:
            logger.error(str(e))
            return False
        except Exception as e:
            logger.error(
                f"Failed to send password expiration email to {user.email}: {str(e)}"
            )
            return False

    @staticmethod
    def _group_passwords_by_user(
        password_entries: QuerySet[PasswordEntry], notification_type: str
    ) -> dict[User, list[dict[str, Any]]]:
        """
        Group password entries by user, excluding already notified entries.

        :param password_entries: QuerySet of password entries
        :param notification_type: Type of notification
        :return: Dictionary mapping users to their password data
        """
        user_passwords = {}

        for entry in password_entries:
            if PasswordExpirationManager.has_notification_been_sent(
                entry, notification_type
            ):
                continue

            if entry.user not in user_passwords:
                user_passwords[entry.user] = []

            user_passwords[entry.user].append(serialize_password_data(entry))

        return user_passwords

    @staticmethod
    def _find_password_entry(
        password_entries: QuerySet[PasswordEntry],
        user: User,
        password_data: dict[str, Any],
    ) -> PasswordEntry | None:
        """
        Find password entry by user and password data.

        :param password_entries: QuerySet of password entries
        :param user: User instance
        :param password_data: Password data dictionary
        :return: PasswordEntry instance or None
        """
        return password_entries.filter(
            user=user, name=password_data["name"], site=password_data["site"]
        ).first()

    @staticmethod
    def _create_notification_records(
        password_entries: QuerySet[PasswordEntry],
        user: User,
        passwords_data: list[dict[str, Any]],
        notification_type: str,
        email_sent: bool,
    ) -> None:
        """
        Create notification records for password entries.

        :param password_entries: QuerySet of password entries
        :param user: User instance
        :param passwords_data: List of password data dictionaries
        :param notification_type: Type of notification
        :param email_sent: Whether email was sent successfully
        """
        for password_data in passwords_data:
            password_entry = PasswordExpirationManager._find_password_entry(
                password_entries, user, password_data
            )

            if password_entry:
                PasswordExpirationNotification.objects.create(
                    password_entry=password_entry,
                    notification_type=notification_type,
                    email_sent_successfully=email_sent,
                )

    @staticmethod
    def _process_notification_batch(
        password_entries: QuerySet[PasswordEntry], notification_type: str
    ) -> int:
        """
        Process a batch of password entries for notifications.

        :param password_entries: QuerySet of password entries
        :param notification_type: Type of notification
        :return: Number of notifications sent
        """
        notifications_sent = 0
        user_passwords = PasswordExpirationManager._group_passwords_by_user(
            password_entries, notification_type
        )

        for user, passwords_data in user_passwords.items():
            email_sent = PasswordExpirationManager.send_expiration_email(
                user, passwords_data, notification_type
            )

            PasswordExpirationManager._create_notification_records(
                password_entries, user, passwords_data, notification_type, email_sent
            )

            if email_sent:
                notifications_sent += 1

        return notifications_sent

    @staticmethod
    def process_expiration_notifications() -> int:
        """
        Main method to process all expiration notifications.

        :return: Total number of notifications sent
        """
        notifications_sent = 0

        # Process 3-day warnings
        passwords_3_days = PasswordExpirationManager.get_passwords_expiring_in_days(
            PasswordExpirationConstants.WARNING_DAYS_3.value
        )
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            passwords_3_days, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        # Process 1-day warnings
        passwords_1_day = PasswordExpirationManager.get_passwords_expiring_in_days(
            PasswordExpirationConstants.WARNING_DAYS_1.value
        )
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            passwords_1_day, PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value
        )

        # Process expired passwords
        expired_passwords = PasswordExpirationManager.get_expired_passwords()
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            expired_passwords,
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value,
        )

        logger.info(
            f"Password expiration notification job completed. {notifications_sent} notifications sent."
        )
        return notifications_sent
