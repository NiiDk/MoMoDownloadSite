# shop/email_utils.py
import threading
import logging
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Robust email service with explicit timeout handling and threading"""
    
    @staticmethod
    def _send_email_sync(subject, message, to_email, from_email, reply_to=None, html_message=None):
        """Internal synchronous sender with connection pooling and explicit timeout."""
        
        # Use settings for timeout and protocol
        timeout = getattr(settings, 'EMAIL_TIMEOUT', 30) 
        use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        use_tls = getattr(settings, 'EMAIL_USE_TLS', False)

        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=[to_email],
                reply_to=reply_to or [],
            )
            
            if html_message:
                email.content_subtype = 'html'
                email.body = html_message
            
            # Get connection with explicit timeout and protocols
            connection = get_connection(
                timeout=timeout,
                use_ssl=use_ssl,
                use_tls=use_tls,
            )
            
            email.connection = connection
            email.send(fail_silently=False)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            # --- FALLBACK: LOG FAILED EMAIL LOCALLY ---
            log_path = os.path.join(settings.BASE_DIR, 'failed_emails.log')
            with open(log_path, 'a') as f:
                f.write(f"{datetime.now()}: Error: {error_msg}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"To: {to_email}\n")
                f.write(f"Body snippet: {message[:100]}...\n\n")
                
            return False, error_msg

    @staticmethod
    def send_email_with_timeout(subject, message, to_email, from_email=None, 
                                html_message=None, reply_to=None, timeout=25):
        """
        Sends email in a separate thread with a time limit (default 25s).
        This prevents the main HTTP request from blocking/timing out.
        """
        
        result = {'success': False, 'error': None}
        
        def send_task():
            # The synchronous sender is executed in the thread
            success, error = EmailService._send_email_sync(
                subject, message, to_email, 
                from_email or settings.DEFAULT_FROM_EMAIL, 
                reply_to, html_message
            )
            result['success'] = success
            result['error'] = error
        
        thread = threading.Thread(target=send_task)
        thread.daemon = True
        thread.start()
        
        # Block the main process only for the specified timeout duration
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            logger.warning(f"⚠️ Thread timeout exceeded for email to {to_email}")
            return False, "Email sending thread timed out (server took too long to respond)."
        
        return result['success'], result.get('error')

    @staticmethod
    def send_contact_email(name, visitor_email, subject, message):
        """Sends the administrative contact email using the robust sender."""
        
        admin_email = settings.EMAIL_HOST_USER
        
        # Format the email content for the admin
        html_content = f"""
        <!DOCTYPE html>
        <html><head>...</head><body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee;">
                <h2>📧 New Contact Form Submission</h2>
                <p><strong>From:</strong> {name} &lt;{visitor_email}&gt;</p>
                <p><strong>Subject:</strong> {subject}</p>
                <hr>
                <p><strong>Message:</strong></p>
                <div style="white-space: pre-wrap; padding: 10px; background-color: #f8f8f8; border-radius: 5px;">{message}</div>
                <p style="font-size: small; color: #999;">Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body></html>
        """
        
        text_content = f"From: {name} <{visitor_email}>\nSubject: {subject}\nMessage:\n{message}"
        email_subject = f"[WEBSITE CONTACT] {subject}"
        
        # Send to admin with visitor's email as the Reply-To
        success, error = EmailService.send_email_with_timeout(
            subject=email_subject,
            message=text_content,
            html_message=html_content,
            to_email=admin_email,
            reply_to=[visitor_email],
            timeout=25
        )
        
        return success, error