from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str, role: str = "user"):
    # Ensure secure password hashing
    password_hash = generate_password_hash(password)
    
    # Create the user object
    db_user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    if not user.is_active:
        return None
    return user
