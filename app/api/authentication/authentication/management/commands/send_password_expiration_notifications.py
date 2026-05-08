# authentication/authentication/management/commands/send_password_expiration_notifications.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from ...password_expiration_manager import PasswordExpirationManager


class Command(BaseCommand):
    """Django management command to send password expiration notifications"""
    help = 'Send password expiration reminder emails'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - shows what would be sent without actually sending emails',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force send notifications even if they were already sent',
        )
        parser.add_argument(
            '--days',
            type=int,
            choices=[1, 3],
            help='Send notifications only for specific days (1 or 3)',
        )
        parser.add_argument(
            '--expired-only',
            action='store_true',
            help='Send notifications only for passwords that expired today',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Send notifications only for a specific user email',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting password expiration notification job at {timezone.now()}'
            )
        )
        
        if options['test']:
            self.stdout.write(self.style.WARNING('Running in TEST MODE - no emails will be sent'))
            self._test_mode(options)
        else:
            notifications_sent = self._run_notifications(options)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Password expiration job completed. {notifications_sent} notifications sent.'
                )
            )
    
    def _run_notifications(self, options):
        """Run the actual notification process"""
        notifications_sent = 0
        
        if options.get('expired_only'):
            # Only process expired passwords
            expired_passwords = PasswordExpirationManager.get_expired_passwords()
            if options.get('user_email'):
                expired_passwords = expired_passwords.filter(user__email=options['user_email'])
            
            notifications_sent += PasswordExpirationManager._process_notification_batch(
                expired_passwords, 'expired'
            )
            self.stdout.write(f"Processed {expired_passwords.count()} expired passwords")
            
        elif options.get('days'):
            # Process specific day notifications
            days = options['days']
            passwords = PasswordExpirationManager.get_passwords_expiring_in_days(days)
            if options.get('user_email'):
                passwords = passwords.filter(user__email=options['user_email'])
            
            notification_type = '3_days' if days == 3 else '1_day'
            notifications_sent += PasswordExpirationManager._process_notification_batch(
                passwords, notification_type
            )
            self.stdout.write(f"Processed {passwords.count()} passwords expiring in {days} day(s)")
            
        else:
            # Process all notifications (default behavior)
            if options.get('user_email'):
                self.stdout.write(f"Processing notifications for user: {options['user_email']}")
                # Filter by user for each category
                passwords_3_days = PasswordExpirationManager.get_passwords_expiring_in_days(3).filter(
                    user__email=options['user_email']
                )
                passwords_1_day = PasswordExpirationManager.get_passwords_expiring_in_days(1).filter(
                    user__email=options['user_email']
                )
                expired_passwords = PasswordExpirationManager.get_expired_passwords().filter(
                    user__email=options['user_email']
                )
                
                notifications_sent += PasswordExpirationManager._process_notification_batch(passwords_3_days, '3_days')
                notifications_sent += PasswordExpirationManager._process_notification_batch(passwords_1_day, '1_day')
                notifications_sent += PasswordExpirationManager._process_notification_batch(expired_passwords, 'expired')
            else:
                # Process all users
                notifications_sent = PasswordExpirationManager.process_expiration_notifications()
        
        return notifications_sent
    
    def _test_mode(self, options):
        """Test mode to show what would be sent"""
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.WARNING("PASSWORD EXPIRATION NOTIFICATION TEST"))
        if options.get('user_email'):
            self.stdout.write(self.style.WARNING(f"USER FILTER: {options['user_email']}"))
        self.stdout.write(self.style.WARNING("=" * 60))
        
        if options.get('expired_only'):
            expired_passwords = PasswordExpirationManager.get_expired_passwords()
            if options.get('user_email'):
                expired_passwords = expired_passwords.filter(user__email=options['user_email'])
            self.stdout.write(f"\n📅 Passwords expired today: {expired_passwords.count()}")
            self._display_passwords(expired_passwords, "EXPIRED")
            
        elif options.get('days'):
            days = options['days']
            passwords = PasswordExpirationManager.get_passwords_expiring_in_days(days)
            if options.get('user_email'):
                passwords = passwords.filter(user__email=options['user_email'])
            self.stdout.write(f"\n📅 Passwords expiring in {days} day{'s' if days > 1 else ''}: {passwords.count()}")
            self._display_passwords(passwords, f"{days} DAY{'S' if days > 1 else ''}")
            
        else:
            # Show all categories
            passwords_3_days = PasswordExpirationManager.get_passwords_expiring_in_days(3)
            if options.get('user_email'):
                passwords_3_days = passwords_3_days.filter(user__email=options['user_email'])
            self.stdout.write(f"\n📅 Passwords expiring in 3 days: {passwords_3_days.count()}")
            self._display_passwords(passwords_3_days, "3 DAYS")
            
            passwords_1_day = PasswordExpirationManager.get_passwords_expiring_in_days(1)
            if options.get('user_email'):
                passwords_1_day = passwords_1_day.filter(user__email=options['user_email'])
            self.stdout.write(f"\n📅 Passwords expiring in 1 day: {passwords_1_day.count()}")
            self._display_passwords(passwords_1_day, "1 DAY")
            
            expired_passwords = PasswordExpirationManager.get_expired_passwords()
            if options.get('user_email'):
                expired_passwords = expired_passwords.filter(user__email=options['user_email'])
            self.stdout.write(f"\n📅 Passwords expired today: {expired_passwords.count()}")
            self._display_passwords(expired_passwords, "EXPIRED")
        
        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("Test completed. Remove --test flag to send actual emails."))
        
        # Show summary statistics
        total_users_affected = set()
        if not options.get('expired_only') and not options.get('days'):
            for entry in (PasswordExpirationManager.get_passwords_expiring_in_days(3) | 
                         PasswordExpirationManager.get_passwords_expiring_in_days(1) | 
                         PasswordExpirationManager.get_expired_passwords()):
                if not options.get('user_email') or entry.user.email == options['user_email']:
                    total_users_affected.add(entry.user.email)
            
            self.stdout.write(f"\n📊 Summary: {len(total_users_affected)} unique users would receive notifications")
    
    def _display_passwords(self, password_entries, category):
        """Display password entries in a formatted way"""
        if not password_entries.exists():
            self.stdout.write(f"  ✅ No passwords in {category} category")
            return
        
        notification_type_map = {
            '3 DAYS': '3_days', 
            '1 DAY': '1_day', 
            'EXPIRED': 'expired'
        }
        
        for entry in password_entries:
            already_notified = PasswordExpirationManager.has_notification_been_sent(
                entry, 
                notification_type_map.get(category, 'unknown')
            )
            
            status = "✅ Already notified" if already_notified else "📧 Will notify"
            site_info = f"Site: {entry.site}" if entry.site else "No site"
            username_info = f"User: {entry.username}" if entry.username else "No username"
            
            self.stdout.write(
                f"  {status} | {entry.user.email} | {entry.name} | "
                f"{site_info} | {username_info} | "
                f"Expires: {entry.expires_at.strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Show additional details for expired passwords
            if category == "EXPIRED" and entry.is_expired:
                days_expired = (timezone.now() - entry.expires_at).days
                self.stdout.write(f"    ⚠️  Expired {days_expired} day(s) ago")
    
    def _show_help_info(self):
        """Show additional help information"""
        self.stdout.write(self.style.HTTP_INFO("\n📖 Usage Examples:"))
        self.stdout.write("  Test mode (no emails sent):")
        self.stdout.write("    python manage.py send_password_expiration_notifications --test")
        self.stdout.write("\n  Send notifications for specific user:")
        self.stdout.write("    python manage.py send_password_expiration_notifications --user-email=user@example.com")
        self.stdout.write("\n  Send only 3-day warnings:")
        self.stdout.write("    python manage.py send_password_expiration_notifications --days=3")
        self.stdout.write("\n  Send only expired notifications:")
        self.stdout.write("    python manage.py send_password_expiration_notifications --expired-only")
        self.stdout.write("\n  Production usage (sends all notifications):")
        self.stdout.write("    python manage.py send_password_expiration_notifications")