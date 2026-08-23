import sys
import os
import getpass

# Add project root to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import get_database_url, get_engine, get_session_maker, Base
from src.database.auth_crud import create_user, get_user_by_email

def main():
    print("=== EMIPredict AI Admin Initialization ===")
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email is required.")
        return
        
    password = getpass.getpass("Enter admin password: ")
    if not password:
        print("Password is required.")
        return
        
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return

    print("Connecting to database...")
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        print("WARNING: Using in-memory SQLite for local testing (data will be lost when script ends).")
        print("To persist this admin, please configure POSTGRES_URI in .streamlit/secrets.toml first.")
        url = "sqlite:///:memory:"
        
    engine = get_engine(url)
    
    # Ensure tables exist
    from src.database.models import User
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = get_session_maker(engine)
    
    with SessionLocal() as db:
        existing_user = get_user_by_email(db, email)
        if existing_user:
            print(f"Error: A user with email {email} already exists.")
            return
            
        try:
            create_user(db, email, password, role="admin")
            print(f"Success! Admin account for {email} created securely.")
        except Exception as e:
            print(f"Error creating admin account: {e}")

if __name__ == "__main__":
    main()
