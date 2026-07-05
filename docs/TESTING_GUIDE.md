# 🧪 Testing Guide for CommAI

## Overview
This guide explains how to run and understand the test suite for CommAI.

## Test Structure

```
backend/
├── test_security.py    # Database and authentication tests
├── test_api.py         # API endpoint tests
└── pytest.ini          # Pytest configuration
```

## Running Tests

### Run All Tests
```bash
cd CommAi
pytest
```

### Run Specific Test File
```bash
pytest backend/test_security.py
pytest backend/test_api.py
```

### Run Specific Test Class
```bash
pytest backend/test_security.py::TestDatabase
pytest backend/test_api.py::TestAuthentication
```

### Run Specific Test
```bash
pytest backend/test_security.py::TestDatabase::test_create_user
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pip install pytest-cov
pytest --cov=backend --cov-report=html
```

## Test Categories

### 1. Database Tests (test_security.py)
- **User Management**
  - User creation
  - Duplicate user prevention
  - Password verification
  - Password hashing (bcrypt)
  
- **OTP Management**
  - OTP storage
  - OTP verification
  - OTP expiration
  
- **Analysis Storage**
  - Save analysis
  - Retrieve user analyses
  
- **Password Updates**
  - Update password
  - Verify old password no longer works

### 2. Authentication Tests (test_security.py)
- **OTP Generation**
  - 6-digit OTP format
  
- **Signup Validation**
  - Email validation
  - Password length validation
  - Successful signup
  
- **Login Validation**
  - Correct credentials
  - Wrong password
  - Non-existent user
  
- **OTP Login**
  - Auto-create user on OTP login

### 3. API Endpoint Tests (test_api.py)
- **Health Check**
  - Server health status
  
- **Authentication Endpoints**
  - Signup validation
  - Login validation
  - OTP request/verify
  
- **Email Analysis**
  - Successful analysis
  - Empty email validation
  - Length validation
  
- **Chatbot**
  - Message processing
  - Message validation
  - Chat history
  
- **History**
  - Retrieve user history
  
- **PDF Generation**
  - Generate PDF report
  - Missing data validation
  
- **Rate Limiting**
  - Rate limit enforcement

## Test Results Interpretation

### ✅ Passing Test
```
test_security.py::TestDatabase::test_create_user PASSED
```
The test passed successfully.

### ❌ Failing Test
```
test_security.py::TestDatabase::test_create_user FAILED
```
The test failed. Check the error message for details.

### ⚠️ Skipped Test
```
test_security.py::TestDatabase::test_create_user SKIPPED
```
The test was skipped (usually marked with @pytest.mark.skip).

## Common Test Scenarios

### Testing Password Security
```python
# Verifies bcrypt hashing
def test_password_hashing(self, temp_db):
    temp_db.create_user("test@example.com", "password123")
    # Password should be hashed, not plain text
    assert stored_password.startswith("$2b$")
```

### Testing Rate Limiting
```python
# Verifies rate limiting works
def test_rate_limit_exceeded(self, client):
    for _ in range(15):  # Exceed limit
        client.post("/api/auth/login", ...)
    # Should return 429 Too Many Requests
    assert response.status_code == 429
```

### Testing Input Validation
```python
# Verifies email validation
def test_signup_invalid_email(self, client):
    response = client.post("/api/auth/signup", json={
        "email": "invalid-email",
        "password": "password123"
    })
    assert response.status_code == 422  # Validation error
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
```

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest
   ```

2. **Write tests for new features**
   - Add test cases for new endpoints
   - Test both success and failure scenarios

3. **Keep tests isolated**
   - Use fixtures for setup/teardown
   - Don't depend on test execution order

4. **Test edge cases**
   - Empty inputs
   - Invalid formats
   - Boundary conditions

5. **Mock external services**
   - Don't send real emails in tests
   - Use temporary databases

## Troubleshooting

### Tests Fail Due to Database Lock
```bash
# Delete test databases
rm backend/*.db
pytest
```

### Import Errors
```bash
# Ensure you're in the project root
cd CommAi
pytest
```

### Rate Limit Tests Fail
```bash
# Rate limits may persist between test runs
# Wait a minute or restart the test
```

## Coverage Goals

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage
  - Authentication
  - Password hashing
  - Input validation

## Adding New Tests

### Template for New Test
```python
def test_new_feature(self, client, test_user):
    """Test description"""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post("/api/endpoint", json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## Summary

✅ **80+ test cases** covering all major functionality
✅ **Security tests** for bcrypt, OTP, validation
✅ **API tests** for all endpoints
✅ **Rate limiting tests** to prevent abuse
✅ **Error handling tests** for edge cases

Run `pytest -v` to see all tests in action!
