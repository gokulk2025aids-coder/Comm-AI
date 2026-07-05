import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from auth import AuthService
import tempfile
import shutil

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    db = Database(db_path)
    yield db
    shutil.rmtree(temp_dir)

@pytest.fixture
def auth_service(temp_db):
    """Create auth service with temp database"""
    service = AuthService()
    service.db = temp_db
    return service

class TestDatabase:
    def test_create_user(self, temp_db):
        """Test user creation"""
        user_id = temp_db.create_user("test@example.com", "password123")
        assert user_id is not None
        assert user_id > 0
    
    def test_create_duplicate_user(self, temp_db):
        """Test duplicate user creation fails"""
        temp_db.create_user("test@example.com", "password123")
        user_id = temp_db.create_user("test@example.com", "password456")
        assert user_id is None
    
    def test_verify_user_correct_password(self, temp_db):
        """Test user verification with correct password"""
        temp_db.create_user("test@example.com", "password123")
        user_id = temp_db.verify_user("test@example.com", "password123")
        assert user_id is not None
    
    def test_verify_user_wrong_password(self, temp_db):
        """Test user verification with wrong password"""
        temp_db.create_user("test@example.com", "password123")
        user_id = temp_db.verify_user("test@example.com", "wrongpassword")
        assert user_id is None
    
    def test_get_user_by_email(self, temp_db):
        """Test getting user by email"""
        temp_db.create_user("test@example.com", "password123")
        user = temp_db.get_user_by_email("test@example.com")
        assert user is not None
        assert user["email"] == "test@example.com"
    
    def test_get_nonexistent_user(self, temp_db):
        """Test getting non-existent user"""
        user = temp_db.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    def test_password_hashing(self, temp_db):
        """Test that passwords are hashed"""
        import sqlite3
        temp_db.create_user("test@example.com", "password123")
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", ("test@example.com",))
        stored_password = cursor.fetchone()[0]
        conn.close()
        
        # Password should be hashed (bcrypt hash starts with $2b$)
        assert stored_password != "password123"
        assert stored_password.startswith("$2b$")
    
    def test_otp_storage_and_verification(self, temp_db):
        """Test OTP storage and verification"""
        from datetime import datetime, timedelta
        email = "test@example.com"
        otp = "123456"
        expires_at = datetime.now() + timedelta(minutes=10)
        
        temp_db.store_otp(email, otp, expires_at)
        result = temp_db.verify_otp(email, otp)
        assert result is True
    
    def test_expired_otp(self, temp_db):
        """Test that expired OTP fails verification"""
        from datetime import datetime, timedelta
        email = "test@example.com"
        otp = "123456"
        # Set expiration to past time using SQLite compatible format
        expires_at = datetime.now() - timedelta(minutes=5)
        
        # Store OTP with past expiration
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
        cursor.execute(
            "INSERT INTO otps (email, otp, expires_at) VALUES (?, ?, datetime('now', '-10 minutes'))",
            (email, otp)
        )
        conn.commit()
        conn.close()
        
        # Try to verify - should fail because it's expired
        result = temp_db.verify_otp(email, otp)
        assert result is False
    
    def test_save_and_get_analysis(self, temp_db):
        """Test saving and retrieving analysis"""
        user_id = temp_db.create_user("test@example.com", "password123")
        email_text = "Test email content"
        analysis = {"summary": "Test summary", "tone": "Formal"}
        
        analysis_id = temp_db.save_analysis(user_id, email_text, analysis)
        assert analysis_id is not None
        
        analyses = temp_db.get_user_analyses(user_id)
        assert len(analyses) == 1
        assert analyses[0]["email_text"] == email_text
        assert analyses[0]["analysis"]["summary"] == "Test summary"
    
    def test_update_password(self, temp_db):
        """Test password update"""
        email = "test@example.com"
        temp_db.create_user(email, "oldpassword")
        
        success = temp_db.update_password(email, "newpassword")
        assert success is True
        
        # Verify old password doesn't work
        user_id = temp_db.verify_user(email, "oldpassword")
        assert user_id is None
        
        # Verify new password works
        user_id = temp_db.verify_user(email, "newpassword")
        assert user_id is not None

class TestAuthService:
    def test_generate_otp(self, auth_service):
        """Test OTP generation"""
        otp = auth_service.generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_request_otp_invalid_email(self, auth_service):
        """Test OTP request with invalid email"""
        with pytest.raises(ValueError):
            auth_service.request_otp("invalid-email")
    
    def test_signup_invalid_email(self, auth_service):
        """Test signup with invalid email"""
        with pytest.raises(ValueError):
            auth_service.signup("invalid-email", "password123")
    
    def test_signup_short_password(self, auth_service):
        """Test signup with short password"""
        with pytest.raises(ValueError):
            auth_service.signup("test@example.com", "12345")
    
    def test_signup_success(self, auth_service):
        """Test successful signup"""
        user = auth_service.signup("test@example.com", "password123")
        assert user is not None
        assert user["email"] == "test@example.com"
    
    def test_login_success(self, auth_service):
        """Test successful login"""
        auth_service.signup("test@example.com", "password123")
        user = auth_service.login("test@example.com", "password123")
        assert user is not None
        assert user["email"] == "test@example.com"
    
    def test_login_wrong_password(self, auth_service):
        """Test login with wrong password"""
        auth_service.signup("test@example.com", "password123")
        user = auth_service.login("test@example.com", "wrongpassword")
        assert user is None
    
    def test_login_nonexistent_user(self, auth_service):
        """Test login with non-existent user"""
        user = auth_service.login("nonexistent@example.com", "password123")
        assert user is None
    
    def test_verify_otp_login_creates_user(self, auth_service):
        """Test that OTP login creates user if doesn't exist"""
        from datetime import datetime, timedelta
        email = "newuser@example.com"
        otp = "123456"
        expires_at = datetime.now() + timedelta(minutes=10)
        
        auth_service.db.store_otp(email, otp, expires_at)
        user = auth_service.verify_otp_login(email, otp)
        
        assert user is not None
        assert user["email"] == email
        
        # Verify user was created in database
        db_user = auth_service.db.get_user_by_email(email)
        assert db_user is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
