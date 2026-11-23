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

# Local fallback: build it from parts. Nothing project-specific is hard-coded.
if not DATABASE_URL:
    _pw = os.getenv("SUPABASE_PASSWORD")
    _user = os.getenv("SUPABASE_DB_USER")  # e.g. postgres.<project-ref>
    _host = os.getenv("SUPABASE_DB_HOST")  # e.g. aws-1-ap-south-1.pooler.supabase.com
    if _pw and _user and _host:
        DATABASE_URL = (
            f"postgresql://{_user}:{urllib.parse.quote_plus(_pw)}@{_host}:6543/postgres"
        )

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set (or SUPABASE_PASSWORD + SUPABASE_DB_USER + SUPABASE_DB_HOST)."
    )

# SQLAlchemy 2.1 changed the default driver for "postgresql://" from psycopg2 to
# psycopg3, which isn't installed here. Pin the driver explicitly.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg2://" + DATABASE_URL[len("postgresql://"):]

# Serverless + Supabase transaction pooler: don't hold a client-side pool.
engine = create_engine(DATABASE_URL, poolclass=NullPool, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_schema_ready = False


def ensure_schema() -> None:
    """Idempotently create the extension and tables. Cheap after the first call per cold start."""
    global _schema_ready
    if _schema_ready:
        return
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
