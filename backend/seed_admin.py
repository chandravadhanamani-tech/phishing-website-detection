"""
seed_admin.py - Create Initial Admin Account
=============================================
Run this script ONCE after setting up the database to create the first admin user.

Usage:
    cd backend
    python seed_admin.py

The admin user can:
  - Access the admin dashboard at /admin
  - View all users and system-wide statistics
  - Activate/switch between trained ML models
"""

import sys
import getpass

# Add the backend directory to path so we can import app modules
sys.path.insert(0, ".")

from app.core.config import get_settings
from app.core.security import hash_password
from app.database import SessionLocal, init_db
from app.models.user import User

settings = get_settings()


def main():
    print("=" * 55)
    print("  PhishingShield - Admin Account Setup")
    print("=" * 55)
    print()

    # ── Collect admin details ──────────────────────────────────────────────────
    name = input("Enter admin name: ").strip()
    if not name or len(name) < 2:
        print("❌ Name must be at least 2 characters.")
        sys.exit(1)

    email = input("Enter admin email: ").strip().lower()
    if "@" not in email or "." not in email:
        print("❌ Please enter a valid email address.")
        sys.exit(1)

    password = getpass.getpass("Enter admin password (hidden): ")
    if len(password) < 8:
        print("❌ Password must be at least 8 characters long.")
        sys.exit(1)

    confirm = getpass.getpass("Confirm password (hidden): ")
    if password != confirm:
        print("❌ Passwords do not match.")
        sys.exit(1)

    # ── Initialize DB and create admin ────────────────────────────────────────
    print()
    print("🔧 Initializing database tables...")
    try:
        init_db()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print()
        print("Please check your .env file:")
        print(f"  DB_HOST     = {settings.db_host}")
        print(f"  DB_PORT     = {settings.db_port}")
        print(f"  DB_NAME     = {settings.db_name}")
        print(f"  DB_USER     = {settings.db_user}")
        print(f"  DB_PASSWORD = (hidden)")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Check for existing email
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if existing.role == "admin":
                print(f"⚠️  Admin account already exists for: {email}")
                print("    No changes made.")
            else:
                # Upgrade existing user to admin
                existing.role = "admin"
                db.commit()
                print(f"✅ Existing user '{email}' has been upgraded to admin role.")
            return

        # Create the admin user
        admin_user = User(
            name          = name,
            email         = email,
            password_hash = hash_password(password),
            role          = "admin",
            is_active     = True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print()
        print("✅ Admin account created successfully!")
        print()
        print(f"  Name:  {admin_user.name}")
        print(f"  Email: {admin_user.email}")
        print(f"  Role:  {admin_user.role}")
        print(f"  ID:    {admin_user.id}")
        print()
        print("🚀 You can now log in at:")
        print(f"   Frontend:  {settings.frontend_url}/login")
        print(f"   API Docs:  http://localhost:{settings.backend_port}/docs")
        print()

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create admin account: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
