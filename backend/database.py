from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("SUPABASE_PASSWORD")
# Direct connection (bypasses pooler region issues)
DATABASE_URL = f"postgresql://postgres:{password}@db.smsfqwxfiswxttzvpxmw.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()