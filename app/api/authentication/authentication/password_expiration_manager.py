from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import models
from django.conf import settings
from datetime import timedelta
import logging
import uuid
import datetime
import time

from .models import User, PasswordExpirationNotification
from .password_manager_models import PasswordEntry
from .config import config

logger = logging.getLogger(__name__)


class PasswordExpirationManager:
    """Manages password expiration notifications"""
    
    @staticmethod
    def get_passwords_expiring_in_days(days: int):
        """Get passwords expiring in exactly N days"""
        target_date = timezone.now().date() + timedelta(days=days)
        start_of_day = timezone.make_aware(
            datetime.datetime.combine(target_date, datetime.time.min)
        )
        end_of_day = timezone.make_aware(
            datetime.datetime.combine(target_date, datetime.time.max)
        )
        
        return PasswordEntry.objects.filter(
            expires_at__range=(start_of_day, end_of_day),
            expires_at__isnull=False
        ).select_related('user')
    
    @staticmethod
    def get_expired_passwords():
        """Get passwords that expired today"""
        today = timezone.now().date()
        start_of_day = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time.min)
        )
        end_of_day = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time.max)
        )
        
        return PasswordEntry.objects.filter(
            expires_at__range=(start_of_day, end_of_day),
            expires_at__isnull=False
        ).select_related('user')
    
    @staticmethod
    def has_notification_been_sent(password_entry, notification_type):
        """Check if notification has already been sent"""
        return PasswordExpirationNotification.objects.filter(
            password_entry=password_entry,
            notification_type=notification_type,
            email_sent_successfully=True
        ).exists()
    
    @staticmethod
    def send_expiration_email(user, passwords_data, notification_type):
        """Send password expiration email"""
        try:
            # Determine email subject and template based on notification type
            if notification_type == '3_days':
                subject = "Password Expiration Warning - 3 Days Remaining"
                template_name = 'emails/password_expiring_3_days'
            elif notification_type == '1_day':
                subject = "Password Expiration Alert - 1 Day Remaining"
                template_name = 'emails/password_expiring_1_day'
            elif notification_type == 'expired':
                subject = "Password Expired - Immediate Action Required"
                template_name = 'emails/password_expired'
            else:
                logger.error(f"Unknown notification type: {notification_type}")
                return False
            
            # Prepare email context
            context = {
                'user': user,
                'passwords': passwords_data,
                'notification_type': notification_type,
                'dashboard_url': f"{config.FRONTEND_URL}/passwords",
                'total_count': len(passwords_data),
            }
            
            # Render email templates
            html_content = render_to_string(f'{template_name}.html', context)
            text_content = render_to_string(f'{template_name}.txt', context)
            
            # Create and send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=config.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Password expiration email sent to {user.email} for {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password expiration email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def process_expiration_notifications():
        """Main method to process all expiration notifications"""
        notifications_sent = 0
        
        # Process 3-day warnings
        passwords_3_days = PasswordExpirationManager.get_passwords_expiring_in_days(3)
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            passwords_3_days, '3_days'
        )
        
        # Process 1-day warnings
        passwords_1_day = PasswordExpirationManager.get_passwords_expiring_in_days(1)
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            passwords_1_day, '1_day'
        )
        
        # Process expired passwords
        expired_passwords = PasswordExpirationManager.get_expired_passwords()
        notifications_sent += PasswordExpirationManager._process_notification_batch(
            expired_passwords, 'expired'
        )
        
        logger.info(f"Password expiration notification job completed. {notifications_sent} notifications sent.")
        return notifications_sent
    
    @staticmethod
    def _process_notification_batch(password_entries, notification_type):
        """Process a batch of password entries for notifications"""
        notifications_sent = 0
        
        # Group passwords by user
        user_passwords = {}
        for entry in password_entries:
            # Skip if notification already sent
            if PasswordExpirationManager.has_notification_been_sent(entry, notification_type):
                continue
                
            if entry.user not in user_passwords:
                user_passwords[entry.user] = []
            
            user_passwords[entry.user].append({
                'name': entry.name,
                'site': entry.site,
                'username': entry.username,
                'expires_at': entry.expires_at,
                'days_until_expiry': entry.days_until_expiry,
            })
        
        # Send emails to users
        for user, passwords_data in user_passwords.items():
            email_sent = PasswordExpirationManager.send_expiration_email(
                user, passwords_data, notification_type
            )
            
            # Record notifications
            for password_data in passwords_data:
                password_entry = password_entries.filter(
                    user=user,
                    name=password_data['name'],
                    site=password_data['site']
                ).first()
                
                if password_entry:
                    PasswordExpirationNotification.objects.create(
                        password_entry=password_entry,
                        notification_type=notification_type,
                        email_sent_successfully=email_sent
                    )
            
            if email_sent:
                notifications_sent += 1
        
        return notifications_sent