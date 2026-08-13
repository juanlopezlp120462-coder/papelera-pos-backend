from app.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE arqueos
        ADD COLUMN IF NOT EXISTS uuid VARCHAR;
    """))

print("Columna uuid agregada correctamente.")