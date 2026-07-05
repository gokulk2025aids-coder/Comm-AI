from database import Database
from auth import AuthService
import getpass

db = Database()
auth = AuthService()

print("=" * 60)
print("COMMAI ACCOUNT CHECKER & PASSWORD RESET")
print("=" * 60)

# Show all users
import sqlite3
conn = sqlite3.connect('commai.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email, created_at FROM users ORDER BY id")
users = cursor.fetchall()
conn.close()

print("\nRegistered users:")
print("-" * 60)
for user in users:
    print(f"ID: {user[0]:<3} | Email: {user[1]:<35} | Created: {user[2]}")
print("-" * 60)

print("\n\nOPTIONS:")
print("1. Test login with your credentials")
print("2. Reset password for an account")
print("3. Exit")

choice = input("\nEnter your choice (1-3): ").strip()

if choice == "1":
    print("\n--- TEST LOGIN ---")
    email = input("Enter your email: ").strip()
    password = getpass.getpass("Enter your password: ")
    
    result = auth.login(email, password)
    if result:
        print(f"\nSUCCESS! Login works correctly.")
        print(f"User ID: {result['id']}")
        print(f"Email: {result['email']}")
    else:
        print(f"\nFAILED! Invalid credentials.")
        print(f"Either the email doesn't exist or the password is wrong.")

elif choice == "2":
    print("\n--- RESET PASSWORD ---")
    email = input("Enter the email address: ").strip()
    
    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        print(f"\nERROR: No account found with email: {email}")
    else:
        print(f"\nAccount found: ID {user['id']}")
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("\nERROR: Passwords don't match!")
        elif len(new_password) < 6:
            print("\nERROR: Password must be at least 6 characters!")
        else:
            success = db.update_password(email, new_password)
            if success:
                print(f"\nSUCCESS! Password updated for {email}")
                print(f"You can now login with your new password.")
            else:
                print(f"\nERROR: Failed to update password.")

else:
    print("\nExiting...")

print("\n" + "=" * 60)
