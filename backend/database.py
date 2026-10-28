import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Por padrão usa PostgreSQL, mas permite fallback local em SQLite para testar rapidamente o MVP sem precisar subir container agora
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./brusque_mesa.db"  # Troque para "postgresql://usuario:senha@localhost:5432/brusque_mesa" em produção
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

