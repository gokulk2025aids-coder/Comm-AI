import sqlite3
import bcrypt
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="commai.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # OTP table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Email analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_text TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using bcrypt for secure storage"""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise ValueError("Failed to hash password")
    
    def create_user(self, email, password):
        """Create new user with hashed password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if not email or not password:
                raise ValueError("Email and password are required")
            
            hashed = self.hash_password(password)
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"User created successfully: {email}")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed - email already exists: {email}")
            return None
        except Exception as e:
            logger.error(f"User creation error: {e}")
            raise
        finally:
            conn.close()
    
    def verify_user(self, email, password):
        """Verify user credentials using bcrypt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            logger.info(f"Attempting login for: {email}")
            cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Login attempt for non-existent user: {email}")
                return None
            
            user_id, stored_hash = result
            logger.info(f"User found, verifying password for: {email}")
            
            # Ensure password and hash are properly encoded
            try:
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash
                
                # Check if password matches
                if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                    logger.info(f"Successful login: {email}")
                    return user_id
                else:
                    logger.warning(f"Failed login attempt - incorrect password: {email}")
                    return None
            except Exception as bcrypt_error:
                logger.error(f"Bcrypt verification error for {email}: {bcrypt_error}")
                logger.error(f"Stored hash type: {type(stored_hash)}, length: {len(stored_hash) if stored_hash else 0}")
                raise ValueError(f"Password verification failed: {str(bcrypt_error)}")
                
        except ValueError as ve:
            # Re-raise ValueError for proper error handling
            raise
        except Exception as e:
            logger.error(f"User verification error for {email}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise ValueError(f"Login failed: {str(e)}")
        finally:
            conn.close()
    
    def get_user_by_email(self, email):
        """Get user by email address"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            return {"id": result[0], "email": result[1]} if result else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None
        finally:
            conn.close()
    
    def store_otp(self, email, otp, expires_at):
        """Store hashed OTP for email verification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_otp = bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
            cursor.execute("INSERT INTO otps (email, otp, expires_at) VALUES (?, ?, ?)",
                          (email, hashed_otp, expires_at))
            conn.commit()
            logger.info(f"OTP stored for: {email}")
        except Exception as e:
            logger.error(f"Error storing OTP: {e}")
            raise
        finally:
            conn.close()

    def verify_otp(self, email, otp):
        """Verify hashed OTP and check expiration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, otp FROM otps
                WHERE email = ? AND expires_at > datetime('now')
            """, (email,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(otp.encode('utf-8'), result[1].encode('utf-8')):
                cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
                conn.commit()
                logger.info(f"OTP verified successfully for: {email}")
                return True
            logger.warning(f"Invalid or expired OTP for: {email}")
            return False
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return False
        finally:
            conn.close()
    
    def save_analysis(self, user_id, email_text, analysis_result):
        """Save email analysis to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Store current timestamp explicitly
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO analyses (user_id, email_text, analysis_result, created_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, email_text, json.dumps(analysis_result), current_time))
            conn.commit()
            analysis_id = cursor.lastrowid
            logger.info(f"Analysis saved for user {user_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_analyses(self, user_id, limit=10):
        """Get user's analysis history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, email_text, analysis_result, created_at 
                FROM analyses 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            results = cursor.fetchall()
            return [{
                "id": r[0],
                "email_text": r[1],
                "analysis": json.loads(r[2]),
                "created_at": r[3]
            } for r in results]
        except Exception as e:
            logger.error(f"Error fetching user analyses: {e}")
            return []
        finally:
            conn.close()
    
    def delete_analysis(self, analysis_id, user_id):
        """Delete a specific analysis from user's history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Analysis {analysis_id} deleted for user {user_id}")
            else:
                logger.warning(f"Failed to delete analysis {analysis_id} for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            return False
        finally:
            conn.close()
    
    def save_chat(self, user_id, message, response):
        """Save chat interaction to history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Store current timestamp explicitly
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO chat_history (user_id, message, response, created_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, message, response, current_time))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving chat: {e}")
        finally:
            conn.close()
    
    def get_chat_history(self, user_id, limit=20):
        """Get user's chat history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT message, response, created_at 
                FROM chat_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            results = cursor.fetchall()
            return [{"message": r[0], "response": r[1], "created_at": r[2]} for r in reversed(results)]
        except Exception as e:
            logger.error(f"Error fetching chat history: {e}")
            return []
        finally:
            conn.close()
    
    def update_password(self, email, new_password):
        """Update user password with new hash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed = self.hash_password(new_password)
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Password updated for: {email}")
            return success
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False
        finally:
            conn.close()
