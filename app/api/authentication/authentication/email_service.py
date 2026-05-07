from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .config import config
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_verification_email(user, token):
        """Send account verification email to user"""
        try:
            # Construct verification URL
            # For now, use frontend URL - you can change this based on your setup
            verification_url = f"{config.FRONTEND_URL}/verify-email?token={token.token}"
            # Direct API verification URL (works without frontend):
            # verification_url = f"http://localhost:8000/api/auth/verify-email/{token.token}"
            
            # Email context
            context = {
                'user': user,
                'verification_url': verification_url,
                'token': token.token,
            }
            
            # Render email templates
            subject = "Verify Your Digital Lockbox Account"
            html_content = render_to_string('emails/account_verification.html', context)
            text_content = render_to_string('emails/account_verification.txt', context)
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=config.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            
            logger.info(f"Verification email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, token):
        """Send password reset email to user"""
        try:
            # Construct password reset URL
            reset_url = f"{config.FRONTEND_URL}/reset-password?token={token.token}"
            
            # Email context
            context = {
                'user': user,
                'reset_url': reset_url,
                'token': token.token,
            }
            
            # Render email templates (you can create these later if needed)
            subject = "Reset Your Digital Lockbox Password"
            
            # For now, use a simple text email for password reset
            text_content = f"""
Hello {user.first_name or user.email},

You requested to reset your password for your Digital Lockbox account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours. If you didn't request this password reset, please ignore this email.

---
Digital Lockbox Team
"""
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=config.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            
            # Send email
            msg.send()
            
            logger.info(f"Password reset email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email after successful verification"""
        try:
            context = {
                'user': user,
                'app_url': config.FRONTEND_URL,
            }
            
            subject = "Welcome to Digital Lockbox!"
            text_content = f"""
Hello {user.first_name or user.email},

Welcome to Digital Lockbox! Your account has been successfully verified.

You can now start using Digital Lockbox to securely store and manage your passwords.

Get started: {config.FRONTEND_URL}

Features you can now use:
- Store unlimited passwords securely
- Generate strong, unique passwords
- Access your passwords from any device
- Organize passwords with folders and tags

Thank you for choosing Digital Lockbox to keep your digital life secure!

---
Digital Lockbox Team
"""
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=config.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            
            # Send email
            msg.send()
            
            logger.info(f"Welcome email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False