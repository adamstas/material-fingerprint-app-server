from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.material import Base

engine = create_engine('sqlite:///materials.db', connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) # creates all tables based on models

def get_db(): # provides DB session for each request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
