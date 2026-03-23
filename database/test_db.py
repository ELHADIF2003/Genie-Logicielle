from database.connection import get_engine
from sqlalchemy import text

try:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(f"✅ Connecté à : {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Échec de la connexion : {e}")