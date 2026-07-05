# 🔄 Migration Guide - Upgrading to Secure CommAI

## Overview
This guide helps you upgrade from the previous version to the new secure version with bcrypt, rate limiting, and comprehensive testing.

---

## ⚠️ Important Changes

### 1. Password Hashing Changed
- **Old**: SHA-256
- **New**: Bcrypt
- **Impact**: Existing passwords won't work

### 2. Environment Variables
- **Old**: Set in start.bat
- **New**: Stored in .env file
- **Impact**: Need to create .env file

### 3. New Dependencies
- bcrypt
- python-dotenv
- slowapi
- pytest

---

## 📋 Migration Steps

### Step 1: Backup Your Data (Optional)
```bash
# Backup your database
copy backend\commai.db backend\commai.db.backup
```

### Step 2: Update Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create .env File
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your settings (optional)
notepad .env
```

### Step 4: Reset Database
**Option A: Delete and recreate (recommended)**
```bash
# Delete old database
del backend\commai.db

# Database will be recreated automatically on next start
```

**Option B: Keep data but reset passwords**
- Users will need to create new accounts or use OTP login
- Old passwords won't work due to bcrypt upgrade

### Step 5: Start the Server
```bash
# Run the updated start script
start.bat
```

### Step 6: Verify Installation
```bash
# Run tests to ensure everything works
run_tests.bat
```

---

## 🔧 Configuration Changes

### Old Configuration (start.bat)
```batch
REM set GMAIL_USER=your-email@gmail.com
REM set GMAIL_APP_PASSWORD=your-password
```

### New Configuration (.env)
```bash
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-password
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
SECRET_KEY=your-secret-key
RATE_LIMIT_PER_MINUTE=60
```

---

## 🔐 Security Improvements

### What's New
1. **Bcrypt Password Hashing**
   - Industry-standard security
   - Automatic salting
   - Brute-force resistant

2. **Rate Limiting**
   - Prevents brute-force attacks
   - Protects against API abuse
   - Configurable limits

3. **Input Validation**
   - Email format validation
   - Password length requirements
   - Request size limits

4. **Comprehensive Logging**
   - All actions logged to commai.log
   - Security events tracked
   - Error monitoring

5. **Environment Variables**
   - Credentials not in code
   - Easy configuration
   - Git-safe

---

## 👥 User Impact

### For Existing Users
- **Must create new account** or use OTP login
- Old passwords won't work (bcrypt upgrade)
- Email addresses preserved if keeping database

### For New Users
- No impact - everything works out of the box

---

## 🧪 Testing

### Verify Security Features
```bash
# Run all tests
pytest -v

# Run security tests only
pytest backend/test_security.py -v

# Check password hashing
pytest backend/test_security.py::TestDatabase::test_password_hashing -v
```

### Expected Results
- All tests should pass
- Passwords should be bcrypt hashed ($2b$ prefix)
- Rate limiting should work

---

## 📊 Feature Comparison

| Feature | Old Version | New Version |
|---------|-------------|-------------|
| Password Hashing | SHA-256 | Bcrypt |
| Rate Limiting | ❌ None | ✅ SlowAPI |
| Input Validation | Basic | Pydantic |
| Error Handling | Basic | Comprehensive |
| Logging | Print | Structured |
| Tests | Minimal | 80+ cases |
| Config | Hardcoded | .env file |
| Security Score | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🐛 Troubleshooting

### "Module 'bcrypt' not found"
```bash
pip install bcrypt
```

### "Can't login with old password"
This is expected. Create a new account:
1. Go to signup page
2. Use same email
3. Create new password

Or use OTP login (no password needed).

### "Rate limit exceeded"
Wait 1 minute or adjust in .env:
```bash
RATE_LIMIT_PER_MINUTE=120
```

### ".env file not found"
```bash
copy .env.example .env
```

### Tests fail
```bash
# Delete old database
del backend\commai.db

# Reinstall dependencies
pip install -r requirements.txt

# Run tests again
pytest
```

---

## 📝 Checklist

Before going live, verify:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created and configured
- [ ] Old database backed up (if needed)
- [ ] Database reset for bcrypt
- [ ] Tests pass (`pytest -v`)
- [ ] Server starts successfully
- [ ] Can create new account
- [ ] Can login with new account
- [ ] Rate limiting works
- [ ] Logs are being written to commai.log

---

## 🚀 Post-Migration

### Monitor Logs
```bash
# View logs in real-time
tail -f backend/commai.log  # Linux/Mac
Get-Content backend/commai.log -Wait  # PowerShell
```

### Run Tests Regularly
```bash
# Before deploying changes
pytest

# With coverage report
pytest --cov=backend --cov-report=html
```

### Update Configuration
Edit `.env` file as needed:
- Add API keys when ready
- Adjust rate limits based on usage
- Configure email settings

---

## 📚 Additional Documentation

- **SECURITY_IMPROVEMENTS.md** - Detailed security changes
- **TESTING_GUIDE.md** - How to run and write tests
- **README.md** - Updated with new features

---

## ✅ Migration Complete!

Your CommAI installation is now upgraded with:
- ✅ Bcrypt password hashing
- ✅ Rate limiting protection
- ✅ Comprehensive testing
- ✅ Better error handling
- ✅ Secure configuration

**Enjoy your more secure CommAI! 🎉**
