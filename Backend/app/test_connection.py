"""
Script de test : vérifie qu'on arrive à se connecter à PostgreSQL.
Usage: python -m Backend.app.test_connection
"""
from sqlalchemy import text

from app.database import engine
from app.config import settings


def test_connection() -> None:
    """Tente une connexion et exécute SELECT version()."""
    print(f"🔌 Tentative de connexion à : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"👤 Utilisateur : {settings.DB_USER}")
    print("-" * 60)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Connexion réussie !")
            print(f"📊 Version PostgreSQL : {version}")
    except Exception as exc:
        print(f"❌ Échec de la connexion :")
        print(f"   → {type(exc).__name__}: {exc}")
        print()
        print("💡 Checklist :")
        print("   - PostgreSQL est-il démarré ? (services Windows)")
        print("   - Le mot de passe dans .env est-il correct ?")
        print("   - La BDD 'projet_gl' existe-t-elle ?")


if __name__ == "__main__":
    test_connection()