import pytest
from fastapi.testclient import TestClient
import sys
import os
import tempfile
import shutil
import random

# Set testing mode BEFORE importing main
os.environ["TESTING"] = "true"

sys.path.insert(0, os.path.dirname(__file__))

# Import after path is set
from database import Database

# Create a test database for the entire test session
test_db_path = None
test_db = None

def setup_module():
    """Setup test database before all tests"""
    global test_db_path, test_db
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test.db")
    test_db = Database(test_db_path)
    
    # Patch the database in main module
    import main
    main.db = test_db
    main.auth_service.db = test_db
    main.chatbot.db = test_db

def teardown_module():
    """Cleanup test database after all tests"""
    global test_db_path
    if test_db_path and os.path.exists(os.path.dirname(test_db_path)):
        shutil.rmtree(os.path.dirname(test_db_path))

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def test_user(client):
    """Create a test user and return credentials"""
    email = f"testuser{random.randint(10000, 99999)}@example.com"
    password = "testpass123"
    
    response = client.post("/api/auth/signup", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        user_data = response.json()["user"]
        user_data["password"] = password
        return user_data
    
    pytest.fail(f"Failed to create test user: {response.json()}")

class TestHealthCheck:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestAuthentication:
    def test_signup_success(self, client):
        """Test successful user signup"""
        email = f"newuser{random.randint(10000, 99999)}@example.com"
        response = client.post("/api/auth/signup", json={
            "email": email,
            "password": "password123"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "user" in response.json()
    
    def test_signup_invalid_email(self, client):
        """Test signup with invalid email"""
        response = client.post("/api/auth/signup", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422  # Validation error
    
    def test_signup_short_password(self, client):
        """Test signup with short password"""
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "12345"
        })
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
    
    def test_request_otp(self, client):
        """Test OTP request"""
        response = client.post("/api/auth/request-otp", json={
            "email": "test@example.com"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_request_otp_invalid_email(self, client):
        """Test OTP request with invalid email"""
        response = client.post("/api/auth/request-otp", json={
            "email": "invalid-email"
        })
        assert response.status_code == 422
    
    def test_verify_otp_invalid_format(self, client):
        """Test OTP verification with invalid format"""
        response = client.post("/api/auth/verify-otp", json={
            "email": "test@example.com",
            "otp": "12345"  # Only 5 digits
        })
        assert response.status_code == 422

class TestEmailAnalysis:
    def test_analyze_email_success(self, client, test_user):
        """Test successful email analysis"""
        response = client.post("/api/analyze", json={
            "email_text": "Dear Sir, I am writing to request information about your services. Thank you.",
            "user_id": test_user["id"]
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "analysis" in response.json()
    
    def test_analyze_empty_email(self, client, test_user):
        """Test analysis with empty email"""
        response = client.post("/api/analyze", json={
            "email_text": "",
            "user_id": test_user["id"]
        })
        assert response.status_code == 422
    
    def test_analyze_short_email(self, client, test_user):
        """Test analysis with too short email"""
        response = client.post("/api/analyze", json={
            "email_text": "Hi",
            "user_id": test_user["id"]
        })
        assert response.status_code == 422
    
    def test_analyze_too_long_email(self, client, test_user):
        """Test analysis with too long email"""
        response = client.post("/api/analyze", json={
            "email_text": "a" * 60000,  # Exceeds 50000 limit
            "user_id": test_user["id"]
        })
        assert response.status_code == 422

class TestChatbot:
    def test_chat_success(self, client, test_user):
        """Test successful chat interaction"""
        response = client.post("/api/chat", json={
            "message": "How do I write a professional email?",
            "user_id": test_user["id"]
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "response" in response.json()
    
    def test_chat_empty_message(self, client, test_user):
        """Test chat with empty message"""
        response = client.post("/api/chat", json={
            "message": "",
            "user_id": test_user["id"]
        })
        assert response.status_code == 422
    
    def test_chat_too_long_message(self, client, test_user):
        """Test chat with too long message"""
        response = client.post("/api/chat", json={
            "message": "a" * 6000,  # Exceeds 5000 limit
            "user_id": test_user["id"]
        })
        assert response.status_code == 422
    
    def test_get_chat_history(self, client, test_user):
        """Test getting chat history"""
        # First send a message
        client.post("/api/chat", json={
            "message": "Test message",
            "user_id": test_user["id"]
        })
        
        # Then get history
        response = client.get(f"/api/chat-history/{test_user['id']}")
        assert response.status_code == 200
        assert response.json()["success"] is True

class TestHistory:
    def test_get_history(self, client, test_user):
        """Test getting analysis history"""
        # First create an analysis
        client.post("/api/analyze", json={
            "email_text": "Test email for history with enough characters to pass validation",
            "user_id": test_user["id"]
        })
        
        # Then get history
        response = client.post("/api/history", json={
            "user_id": test_user["id"]
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["history"]) > 0

class TestPDFGeneration:
    def test_generate_pdf_success(self, client):
        """Test successful PDF generation"""
        response = client.post("/api/generate-pdf", json={
            "email_text": "Test email content",
            "analysis": {
                "summary": "Test summary",
                "tone": "Formal",
                "sentiment": "Positive",
                "tone_reasoning": "Professional language",
                "intent": "Request",
                "confidence": "85%",
                "polarity": 0.5,
                "subjectivity": 0.5,
                "emotion": "Neutral",
                "key_points": ["Point 1"],
                "action_items": [],
                "priority": "Medium",
                "priority_reason": "Standard",
                "suggested_reply": "Thank you"
            }
        })
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    def test_generate_pdf_missing_data(self, client):
        """Test PDF generation with missing data"""
        response = client.post("/api/generate-pdf", json={
            "email_text": "Test email"
        })
        assert response.status_code == 400

class TestRateLimiting:
    def test_rate_limit_behavior(self, client):
        """Test that rate limiting is configured"""
        # Make several requests
        responses = []
        for _ in range(5):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            responses.append(response.status_code)
        
        # Should get 401 (unauthorized) not 500 (server error)
        assert all(status in [401, 429] for status in responses)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
