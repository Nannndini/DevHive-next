from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("SUPABASE_PASSWORD")
DATABASE_URL = f"postgresql://postgres.smsfqwxfiswxttzvpxmw:{password}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()