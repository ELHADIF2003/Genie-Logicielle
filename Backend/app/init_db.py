"""
Script d'initialisation de la base de donnees.
Lit le fichier database/BDD.sql et execute les CREATE TABLE.

Usage (depuis Backend/) : python -m app.init_db
"""
from pathlib import Path

from sqlalchemy import text

from app.config import BASE_DIR
from app.database import engine


SQL_FILE = BASE_DIR / "database" / "BDD.sql"


def init_database() -> None:
    """Execute le script SQL pour creer les tables."""
    print(f"Lecture du fichier SQL : {SQL_FILE}")

    if not SQL_FILE.exists():
        print(f"[ECHEC] Fichier introuvable : {SQL_FILE}")
        return

    sql_content = SQL_FILE.read_text(encoding="utf-8")
    print(f"Fichier charge ({len(sql_content)} caracteres)")
    print("-" * 60)

    # Execute le script dans une transaction
    # Si ca plante, aucune table n'est creee (tout ou rien)
    try:
        with engine.begin() as connection:
            connection.execute(text(sql_content))
        print("[OK] Tables creees avec succes !")
    except Exception as exc:
        print(f"[ECHEC] Erreur SQL :")
        print(f"   -> {type(exc).__name__}: {exc}")
        print()
        print("Astuce : si les tables existent deja, il faut les supprimer avant :")
        print("   DROP TABLE IF EXISTS Indicateur, ResultatBac, Lycee, Dataset, Academie, Utilisateur CASCADE;")
        return

    # Verification : liste les tables creees
    print()
    print("Tables presentes dans la BDD :")
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        for row in result:
            print(f"   - {row[0]}")


if __name__ == "__main__":
    init_database()