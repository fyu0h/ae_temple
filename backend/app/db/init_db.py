from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate
from app.db.base import Base, engine

def init_db(db: Session) -> None:
    """Initialize the database."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial admin user if it doesn't exist
    user = crud.user.get_user_by_email(db, email="admin@example.com")
    if not user:
        user_in = UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin123"  # Change this in production
        )
        user = crud.user.create_user(db, user=user_in)
        # Set as admin
        user.is_admin = True
        db.add(user)
        db.commit()
        db.refresh(user)

def create_tables() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine) 