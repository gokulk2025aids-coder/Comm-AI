import smtplib
import random
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from database import Database

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.db = Database()
        self.gmail_user = os.getenv("GMAIL_USER", "")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
    
    def generate_otp(self):
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def send_otp_email(self, email, otp):
        """Send OTP via email or print to console in dev mode"""
        if not self.gmail_user or not self.gmail_password:
            logger.info(f"Dev mode: OTP for {email} is {otp}")
            # Force output to console with multiple methods
            otp_message = f"\n{'='*50}\nOTP for {email}: {otp}\n{'='*50}\n"
            
            # Method 1: Standard print
            try:
                print(otp_message, flush=True)
            except Exception as e1:
                logger.error(f"Standard print failed: {e1}")
                
                # Method 2: Direct to stdout
                try:
                    import sys
                    sys.stdout.write(otp_message)
                    sys.stdout.flush()
                except Exception as e2:
                    logger.error(f"Stdout write failed: {e2}")
                    
                    # Method 3: Direct to stderr as fallback
                    try:
                        sys.stderr.write(otp_message)
                        sys.stderr.flush()
                    except Exception as e3:
                        logger.error(f"All console output methods failed: {e3}")
            
            logger.warning(f"*** DEVELOPMENT MODE OTP: {otp} for {email} ***")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = email
            msg['Subject'] = "Your CommAI Login OTP"
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #6366f1;">CommAI Email Analyzer</h2>
                    <p>Your One-Time Password (OTP) is:</p>
                    <h1 style="color: #6366f1; letter-spacing: 5px;">{otp}</h1>
                    <p>This OTP will expire in 10 minutes.</p>
                    <p style="color: #666; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"OTP email sent successfully to {email}")
            return True
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            # Fallback to console in case of email error
            otp_message = f"\n{'='*50}\nOTP for {email}: {otp}\n{'='*50}\n"
            
            # Method 1: Standard print
            try:
                print(otp_message, flush=True)
            except Exception as e1:
                logger.error(f"Standard print failed: {e1}")
                
                # Method 2: Direct to stdout
                try:
                    import sys
                    sys.stdout.write(otp_message)
                    sys.stdout.flush()
                except Exception as e2:
                    logger.error(f"Stdout write failed: {e2}")
                    
                    # Method 3: Direct to stderr as fallback
                    try:
                        sys.stderr.write(otp_message)
                        sys.stderr.flush()
                    except Exception as e3:
                        logger.error(f"All console output methods failed: {e3}")
            
            logger.warning(f"*** EMAIL FAILED - CONSOLE OTP: {otp} for {email} ***")
            return True
    
    def request_otp(self, email):
        """Request OTP for email authentication"""
        try:
            logger.info(f"Processing OTP request for: {email}")
            if not email or '@' not in email:
                raise ValueError("Invalid email address")
            
            # Check if user is registered before sending OTP
            existing_user = self.db.get_user_by_email(email)
            if not existing_user:
                logger.warning(f"OTP requested for unregistered email: {email}")
                raise ValueError("This email is not registered. Please sign up first.")
            
            otp = self.generate_otp()
            logger.info(f"Generated OTP for {email}: {otp}")
            
            expires_at = datetime.now() + timedelta(minutes=10)
            logger.info(f"Storing OTP in database for {email}")
            
            self.db.store_otp(email, otp, expires_at)
            logger.info(f"OTP stored successfully for {email}")
            
            logger.info(f"Sending OTP email to {email}")
            result = self.send_otp_email(email, otp)
            logger.info(f"OTP email sent result for {email}: {result}")
            
            return result
        except Exception as e:
            logger.error(f"OTP request error for {email}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def verify_otp_login(self, email, otp):
        """Verify OTP and create/login user"""
        try:
            if not email or not otp:
                raise ValueError("Email and OTP are required")
            
            if self.db.verify_otp(email, otp):
                user = self.db.get_user_by_email(email)
                if not user:
                    # Create user with a random secure password for OTP-only users
                    import secrets
                    random_password = secrets.token_urlsafe(32)
                    user_id = self.db.create_user(email, random_password)
                    logger.info(f"New user created via OTP: {email}")
                    return {"id": user_id, "email": email}
                return user
            return None
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            raise
    
    def signup(self, email, password):
        """Create new user account"""
        try:
            if not email or '@' not in email:
                raise ValueError("Invalid email address")
            if not password or len(password) < 6:
                raise ValueError("Password must be at least 6 characters")
            
            user_id = self.db.create_user(email, password)
            if user_id:
                logger.info(f"New user signup: {email}")
                return {"id": user_id, "email": email}
            return None
        except Exception as e:
            logger.error(f"Signup error: {e}")
            raise
    
    def login(self, email, password):
        """Authenticate user with email and password"""
        try:
            if not email or not password:
                raise ValueError("Email and password are required")
            
            user_id = self.db.verify_user(email, password)
            if user_id:
                return {"id": user_id, "email": email}
            return None
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
