"""
create_custom_admin.py - Create or update an admin user with custom details.

Usage:
    cd backend
    python create_custom_admin.py "Chandra" "your_email@example.com" "your_password"
"""

import sys
sys.path.insert(0, ".")

from app.database import SessionLocal, init_db
from app.models.user import User
from app.core.security import hash_password

def main():
    if len(sys.argv) < 4:
        print("Usage: python create_custom_admin.py <Name> <Email> <Password>")
        print("Example: python create_custom_admin.py \"Chandra\" \"chandra@example.com\" \"mysecretpass123\"")
        sys.exit(1)

    name     = sys.argv[1].strip()
    email    = sys.argv[2].strip().lower()
    password = sys.argv[3]

    print("[+] Initializing database tables...")
    init_db()

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            existing.name          = name
            existing.password_hash = hash_password(password)
            existing.role          = "admin"
            existing.is_active     = True
            db.commit()
            print(f"[+] Existing account '{email}' updated to Admin role for '{name}'.")
        else:
            new_admin = User(
                name          = name,
                email         = email,
                password_hash = hash_password(password),
                role          = "admin",
                is_active     = True,
            )
            db.add(new_admin)
            db.commit()
            print(f"[+] New Admin account created successfully for '{name}' ({email})!")

        print("==================================================")
        print(f" Name:     {name}")
        print(f" Email:    {email}")
        print(f" Role:     admin")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print(f"[-] Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
