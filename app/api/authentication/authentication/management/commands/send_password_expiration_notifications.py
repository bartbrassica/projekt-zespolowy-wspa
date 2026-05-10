from django.core.management.base import BaseCommand
from django.utils import timezone
from ...password_expiration_manager import PasswordExpirationManager


class Command(BaseCommand):
    help = "Send password expiration reminder emails"

    NOTIFICATION_TYPES = {
        "THREE_DAYS": "3_days",
        "ONE_DAY": "1_day",
        "EXPIRED": "expired",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Test mode - shows what would be sent without actually sending emails",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force send notifications even if they were already sent",
        )
        parser.add_argument(
            "--days",
            type=int,
            choices=[1, 3],
            help="Send notifications only for specific days (1 or 3)",
        )
        parser.add_argument(
            "--expired-only",
            action="store_true",
            help="Send notifications only for passwords that expired today",
        )
        parser.add_argument(
            "--user-email",
            type=str,
            help="Send notifications only for a specific user email",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting password expiration notification job at {timezone.now()}"
            )
        )

        if options["test"]:
            self.stdout.write(
                self.style.WARNING("Running in TEST MODE - no emails will be sent")
            )
            self._test_mode(options)
        else:
            notifications_sent = self._run_notifications(options)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Password expiration job completed. {notifications_sent} notifications sent."
                )
            )

    def _get_filtered_passwords(self, query_method, days=None, user_email=None):
        if days:
            passwords = query_method(days)
        else:
            passwords = query_method()

        if user_email:
            passwords = passwords.filter(user__email=user_email)

        return passwords

    def _run_notifications(self, options):
        """Run the actual notification process"""
        user_email = options.get("user_email")

        if options.get("expired_only"):
            return self._process_expired_only(user_email)
        elif options.get("days"):
            return self._process_specific_days(options["days"], user_email)
        else:
            return self._process_all_notifications(user_email)

    def _process_expired_only(self, user_email):
        expired_passwords = self._get_filtered_passwords(
            PasswordExpirationManager.get_expired_passwords, user_email=user_email
        )
        notifications_sent = PasswordExpirationManager._process_notification_batch(
            expired_passwords, self.NOTIFICATION_TYPES["EXPIRED"]
        )
        self.stdout.write(f"Processed {expired_passwords.count()} expired passwords")
        return notifications_sent

    def _process_specific_days(self, days, user_email):
        passwords = self._get_filtered_passwords(
            PasswordExpirationManager.get_passwords_expiring_in_days,
            days=days,
            user_email=user_email,
        )
        notification_type = (
            self.NOTIFICATION_TYPES["THREE_DAYS"]
            if days == 3
            else self.NOTIFICATION_TYPES["ONE_DAY"]
        )
        notifications_sent = PasswordExpirationManager._process_notification_batch(
            passwords, notification_type
        )
        self.stdout.write(
            f"Processed {passwords.count()} passwords expiring in {days} day(s)"
        )
        return notifications_sent

    def _process_all_notifications(self, user_email):
        if user_email:
            self.stdout.write(f"Processing notifications for user: {user_email}")
            passwords_3_days = self._get_filtered_passwords(
                PasswordExpirationManager.get_passwords_expiring_in_days,
                days=3,
                user_email=user_email,
            )
            passwords_1_day = self._get_filtered_passwords(
                PasswordExpirationManager.get_passwords_expiring_in_days,
                days=1,
                user_email=user_email,
            )
            expired_passwords = self._get_filtered_passwords(
                PasswordExpirationManager.get_expired_passwords, user_email=user_email
            )

            notifications_sent = 0
            notifications_sent += PasswordExpirationManager._process_notification_batch(
                passwords_3_days, self.NOTIFICATION_TYPES["THREE_DAYS"]
            )
            notifications_sent += PasswordExpirationManager._process_notification_batch(
                passwords_1_day, self.NOTIFICATION_TYPES["ONE_DAY"]
            )
            notifications_sent += PasswordExpirationManager._process_notification_batch(
                expired_passwords, self.NOTIFICATION_TYPES["EXPIRED"]
            )
            return notifications_sent
        else:
            return PasswordExpirationManager.process_expiration_notifications()

    def _test_mode(self, options):
        """Test mode to show what would be sent"""
        self._print_test_header(options)

        if options.get("expired_only"):
            self._test_expired_only(options.get("user_email"))
        elif options.get("days"):
            self._test_specific_days(options["days"], options.get("user_email"))
        else:
            self._test_all_categories(options.get("user_email"))

        self._print_test_footer(options)

    def _print_test_header(self, options):
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.WARNING("PASSWORD EXPIRATION NOTIFICATION TEST"))
        if options.get("user_email"):
            self.stdout.write(
                self.style.WARNING(f"USER FILTER: {options['user_email']}")
            )
        self.stdout.write(self.style.WARNING("=" * 60))

    def _test_expired_only(self, user_email):
        expired_passwords = self._get_filtered_passwords(
            PasswordExpirationManager.get_expired_passwords, user_email=user_email
        )
        self.stdout.write(f"\n📅 Passwords expired today: {expired_passwords.count()}")
        self._display_passwords(expired_passwords, "EXPIRED")

    def _test_specific_days(self, days, user_email):
        passwords = self._get_filtered_passwords(
            PasswordExpirationManager.get_passwords_expiring_in_days,
            days=days,
            user_email=user_email,
        )
        self.stdout.write(
            f"\n📅 Passwords expiring in {days} day{'s' if days > 1 else ''}: {passwords.count()}"
        )
        self._display_passwords(passwords, f"{days} DAY{'S' if days > 1 else ''}")

    def _test_all_categories(self, user_email):
        passwords_3_days = self._get_filtered_passwords(
            PasswordExpirationManager.get_passwords_expiring_in_days,
            days=3,
            user_email=user_email,
        )
        self.stdout.write(
            f"\n📅 Passwords expiring in 3 days: {passwords_3_days.count()}"
        )
        self._display_passwords(passwords_3_days, "3 DAYS")

        passwords_1_day = self._get_filtered_passwords(
            PasswordExpirationManager.get_passwords_expiring_in_days,
            days=1,
            user_email=user_email,
        )
        self.stdout.write(
            f"\n📅 Passwords expiring in 1 day: {passwords_1_day.count()}"
        )
        self._display_passwords(passwords_1_day, "1 DAY")

        expired_passwords = self._get_filtered_passwords(
            PasswordExpirationManager.get_expired_passwords, user_email=user_email
        )
        self.stdout.write(f"\n📅 Passwords expired today: {expired_passwords.count()}")
        self._display_passwords(expired_passwords, "EXPIRED")

    def _print_test_footer(self, options):
        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                "Test completed. Remove --test flag to send actual emails."
            )
        )

        if not options.get("expired_only") and not options.get("days"):
            self._show_summary_statistics(options.get("user_email"))

    def _show_summary_statistics(self, user_email):
        total_users_affected = set()
        for entry in (
            PasswordExpirationManager.get_passwords_expiring_in_days(3)
            | PasswordExpirationManager.get_passwords_expiring_in_days(1)
            | PasswordExpirationManager.get_expired_passwords()
        ):
            if not user_email or entry.user.email == user_email:
                total_users_affected.add(entry.user.email)

        self.stdout.write(
            f"\n📊 Summary: {len(total_users_affected)} unique users would receive notifications"
        )

    def _display_passwords(self, password_entries, category):
        """Display password entries in a formatted way"""
        if not password_entries.exists():
            self.stdout.write(f"  ✅ No passwords in {category} category")
            return

        notification_type_map = {
            "3 DAYS": self.NOTIFICATION_TYPES["THREE_DAYS"],
            "1 DAY": self.NOTIFICATION_TYPES["ONE_DAY"],
            "EXPIRED": self.NOTIFICATION_TYPES["EXPIRED"],
        }

        for entry in password_entries:
            already_notified = PasswordExpirationManager.has_notification_been_sent(
                entry, notification_type_map.get(category, "unknown")
            )

            status = "✅ Already notified" if already_notified else "📧 Will notify"
            site_info = f"Site: {entry.site}" if entry.site else "No site"
            username_info = (
                f"User: {entry.username}" if entry.username else "No username"
            )

            self.stdout.write(
                f"  {status} | {entry.user.email} | {entry.name} | "
                f"{site_info} | {username_info} | "
                f"Expires: {entry.expires_at.strftime('%Y-%m-%d %H:%M')}"
            )

            if category == "EXPIRED" and entry.is_expired:
                days_expired = (timezone.now() - entry.expires_at).days
                self.stdout.write(f"    ⚠️  Expired {days_expired} day(s) ago")
