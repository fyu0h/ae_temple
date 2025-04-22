import os
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.init_db import init_db, create_tables

def main() -> None:
    # Create media directory
    from app.core.config import settings
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    
    # Initialize DB
    db = SessionLocal()
    init_db(db)
    print("Database initialized")

if __name__ == "__main__":
    main() 