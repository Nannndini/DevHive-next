import os
import logging
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()
logger = logging.getLogger(__name__)

# Preferred: a full connection string in DATABASE_URL (Supabase pooler, port 6543).
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback (what the previous version of this app used): build it from the password.
# User/host default to the values this project already used; override via env if needed.
if not DATABASE_URL:
    _pw = os.getenv("SUPABASE_PASSWORD")
    if _pw:
        _user = os.getenv("SUPABASE_DB_USER", "postgres.smsfqwxfiswxttzvpxmw")
        _host = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-south-1.pooler.supabase.com")
        DATABASE_URL = f"postgresql://{_user}:{urllib.parse.quote_plus(_pw)}@{_host}:6543/postgres"

# SQLAlchemy 2.1 changed the default driver for "postgresql://" from psycopg2 to
# psycopg3, which isn't installed here. Pin the driver explicitly.
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = "postgresql+psycopg2://" + DATABASE_URL[len("postgresql://"):]

# Don't crash at import when misconfigured: /api/health reports what is missing,
# and DB-backed routes fail with a clear message instead of a blank 500.
# Serverless + Supabase transaction pooler: don't hold a client-side pool.
engine = (
    create_engine(DATABASE_URL, poolclass=NullPool, pool_pre_ping=True) if DATABASE_URL else None
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_schema_ready = False


def ensure_schema() -> None:
    """Idempotently create the extension and tables. Cheap after the first call per cold start."""
    global _schema_ready
    if _schema_ready:
        return
    if engine is None:
        raise RuntimeError("DATABASE_URL (or SUPABASE_PASSWORD) is not set")
    from api import models  # noqa: F401  (registers models on Base)

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS title VARCHAR"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INTEGER,
                content TEXT,
                embedding vector(384)
            )
        """))
    _schema_ready = True
    logger.info("Schema ready")
