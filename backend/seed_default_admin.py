"""
seed_default_admin.py - Non-interactive admin creator script.
Default admin credentials:
  Email:    admin@phishingshield.local
  Password: admin1234password
"""

import sys
sys.path.insert(0, ".")

from app.database import SessionLocal, init_db
from app.models.user import User
from app.core.security import hash_password

def seed_default_admin():
    print("[+] Initializing database tables...")
    init_db()

    db = SessionLocal()
    try:
        email = "admin@phishingshield.local"
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            print(f"[+] Admin account '{email}' already exists.")
            return

        admin_user = User(
            name="Admin User",
            email=email,
            password_hash=hash_password("admin1234password"),
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()

        print("==================================================")
        print(" SUCCESS: Default Admin Account Created!")
        print("==================================================")
        print(" Email:    admin@phishingshield.local")
        print(" Password: admin1234password")
        print(" Role:     admin")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print(f"[-] Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_admin()
