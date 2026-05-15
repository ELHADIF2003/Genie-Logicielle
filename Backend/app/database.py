"""
Configuration SQLAlchemy : Engine, SessionLocal, Base.
Tous les modèles ORM hériteront de Base.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# === Engine : pool de connexions vers PostgreSQL ===
# pool_pre_ping=True : vérifie que la connexion est vivante avant chaque requête
# echo=False : mets True en dev pour voir le SQL généré (très instructif !)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

# === SessionLocal : usine à sessions ===
# autocommit=False + autoflush=False : comportement classique, contrôle manuel
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# === Base : classe parente de tous les modèles ORM ===
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : fournit une session BDD à chaque requête,
    et la ferme automatiquement à la fin (même si erreur).
    Pattern 'context manager' — à utiliser dans chaque endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()