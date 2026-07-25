import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add frontend/api to path to import database config
sys.path.append(os.path.abspath("frontend/api"))

load_dotenv("frontend/api/.env")

password = os.getenv("SUPABASE_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL and password:
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(password)
    DATABASE_URL = f"postgresql://postgres.smsfqwxfiswxttzvpxmw:{encoded_password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

print("Connecting to:", DATABASE_URL.split("@")[-1] if DATABASE_URL else "None")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check columns of documents table
        res = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'documents'
        """)).fetchall()
        print("Documents table columns:")
        for r in res:
            print(f"- {r[0]}: {r[1]}")
else:
    print("No database URL found.")
