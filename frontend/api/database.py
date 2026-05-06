from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

import urllib.parse
password = os.getenv("SUPABASE_PASSWORD")
encoded_password = urllib.parse.quote_plus(password) if password else ""
DATABASE_URL = f"postgresql://postgres.smsfqwxfiswxttzvpxmw:{encoded_password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()