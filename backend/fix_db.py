from database import engine; from sqlalchemy import text; 
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE documents ADD COLUMN IF NOT EXISTS title VARCHAR;'))
    conn.commit()

