"""
Script principal d'import des donnees.
Execute le pipeline complet : Extract -> Transform -> Load.

Usage (depuis Backend/) : python -m app.scripts.run_import
"""
from pathlib import Path

from app.config import BASE_DIR
from app.database import SessionLocal
from app.services.data_cleaner import (
    clean_ips_data,
    clean_bac_data,
    extract_academies,
)
from app.services.data_importer import (
    import_academies,
    create_dataset,
    import_lycees,
    import_resultats_bac,
)


DATA_DIR = BASE_DIR / "data"
IPS_FILE = DATA_DIR / "IPS-Lycees.csv"
BAC_FILE = DATA_DIR / "Résultat-Bac-Par-Academie.csv"


def main() -> None:
    print("=" * 60)
    print("PIPELINE D'IMPORT DES DONNEES EDUCATIVES")
    print("=" * 60)

    # Verifier que les fichiers existent
    if not IPS_FILE.exists():
        print(f"[ECHEC] Fichier introuvable : {IPS_FILE}")
        return
    if not BAC_FILE.exists():
        print(f"[ECHEC] Fichier introuvable : {BAC_FILE}")
        return

    # === EXTRACT + TRANSFORM ===
    print("\n--- PHASE 1 : NETTOYAGE ---")
    ips_df = clean_ips_data(IPS_FILE)
    bac_df = clean_bac_data(BAC_FILE)
    academies_df = extract_academies(ips_df, bac_df)

    # === LOAD ===
    print("\n--- PHASE 2 : INSERTION EN BDD ---")
    db = SessionLocal()
    try:
        # 1. Academies en premier (pour avoir les IDs)
        acad_map = import_academies(db, academies_df)

        # 2. Creer les datasets
        ds_ips_id = create_dataset(db, "IPS-Lycees", "data.education.gouv.fr")
        ds_bac_id = create_dataset(db, "Resultats-Bac", "education.gouv.fr")

        # 3. Lycees (depend des academies et du dataset IPS)
        nb_lycees = import_lycees(db, ips_df, acad_map, ds_ips_id)

        # 4. Resultats bac (depend des academies)
        nb_bac = import_resultats_bac(db, bac_df, acad_map)

        print("\n" + "=" * 60)
        print("IMPORT TERMINE AVEC SUCCES")
        print("=" * 60)
        print(f"   - {len(acad_map)} academies")
        print(f"   - {nb_lycees} lycees")
        print(f"   - {nb_bac} resultats bac")

    except Exception as exc:
        db.rollback()
        print(f"\n[ECHEC] Erreur pendant l'import : {exc}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()