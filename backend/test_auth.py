from auth import AuthService
from database import Database

# Test the authentication flow
auth = AuthService()
db = Database()

print("=" * 60)
print("TESTING SIGNUP AND LOGIN FLOW")
print("=" * 60)

# Test email and password
test_email = "testuser@example.com"
test_password = "MyPassword123"

print(f"\n1. Testing Signup with:")
print(f"   Email: {test_email}")
print(f"   Password: {test_password}")

# Signup
user = auth.signup(test_email, test_password)
if user:
    print(f"   SUCCESS: Signup successful! User ID: {user['id']}")
else:
    print(f"   FAILED: Signup failed (email might already exist)")
    # Try to get existing user
    existing = db.get_user_by_email(test_email)
    if existing:
        print(f"   -> User already exists with ID: {existing['id']}")

print(f"\n2. Testing Login with same credentials:")
print(f"   Email: {test_email}")
print(f"   Password: {test_password}")

# Login
login_result = auth.login(test_email, test_password)
if login_result:
    print(f"   SUCCESS: Login successful! User ID: {login_result['id']}")
else:
    print(f"   FAILED: Login failed - Invalid credentials")

print(f"\n3. Testing with WRONG password:")
wrong_password = "WrongPassword"
print(f"   Email: {test_email}")
print(f"   Password: {wrong_password}")

login_result2 = auth.login(test_email, wrong_password)
if login_result2:
    print(f"   ERROR: Login should have failed but succeeded!")
else:
    print(f"   SUCCESS: Correctly rejected wrong password")

print(f"\n4. Checking database directly:")
# Check what's stored
import sqlite3
conn = sqlite3.connect('commai.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (test_email,))
result = cursor.fetchone()
if result:
    print(f"   User ID: {result[0]}")
    print(f"   Email: {result[1]}")
    print(f"   Password Hash: {result[2][:30]}...")
    
    # Verify hash manually
    expected_hash = db.hash_password(test_password)
    stored_hash = result[2]
    print(f"\n5. Hash comparison:")
    print(f"   Expected hash: {expected_hash[:30]}...")
    print(f"   Stored hash:   {stored_hash[:30]}...")
    print(f"   Match: {expected_hash == stored_hash}")
conn.close()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
