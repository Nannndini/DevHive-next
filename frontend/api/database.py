from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Read Supabase REST API credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read raw Postgres Connection String for SQLAlchemy (pgvector support)
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local testing if only parts are provided
if not DATABASE_URL:
    import urllib.parse
    password = os.getenv("SUPABASE_PASSWORD")
    if password:
        encoded_password = urllib.parse.quote_plus(password)
        DATABASE_URL = f"postgresql://postgres.smsfqwxfiswxttzvpxmw:{encoded_password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

# Initialize SQLAlchemy Engine safely
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

Base = declarative_base()