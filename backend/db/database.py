# importing libraries and methods
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# load the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Δημιουργία σύνδεσης
engine = create_engine(DATABASE_URL)

# Factory για sessions
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Base class για τα models
Base = declarative_base()

# testing για το αν δουλεύει η σύνδεση στο db
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")

# Dependency για FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
