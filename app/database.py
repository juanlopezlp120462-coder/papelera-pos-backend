import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# DATABASE_URL viene de una variable de entorno.
# - En Railway/Render/Supabase te dan algo como:
#   postgresql://usuario:password@host:5432/nombre_db
# - Si no está seteada, usa SQLite local (papelera.db) para poder
#   probar todo en tu PC antes de subirlo a la nube.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./papelera.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()