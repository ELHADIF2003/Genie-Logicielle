"""
Test rapide des modeles ORM.
Usage (depuis Backend/) : python -m app.test_models
"""
from app.database import SessionLocal
from app.models import Academie


def test_models() -> None:
    db = SessionLocal()

    try:
        # 1. CREATE : on insere une academie de test
        print("1. Creation d'une academie de test...")
        test_acad = Academie(
            nomacademie="TEST_ACADEMIE",
            regionacademie="TEST_REGION",
            ipsmoyen=100.50,
        )
        db.add(test_acad)
        db.commit()
        db.refresh(test_acad)
        print(f"   [OK] Creee : {test_acad}")

        # 2. READ : on la recupere depuis la BDD
        print("\n2. Lecture depuis la BDD...")
        acad_recup = db.query(Academie).filter(
            Academie.nomacademie == "TEST_ACADEMIE"
        ).first()
        print(f"   [OK] Trouvee : {acad_recup}")
        print(f"   Nom      : {acad_recup.nomacademie}")
        print(f"   Region   : {acad_recup.regionacademie}")
        print(f"   IPS moyen: {acad_recup.ipsmoyen}")

        # 3. DELETE : on nettoie pour ne pas laisser de pollution
        print("\n3. Suppression de l'academie de test...")
        db.delete(acad_recup)
        db.commit()
        print("   [OK] Supprimee")

        print("\n[SUCCES] Les modeles ORM fonctionnent parfaitement !")

    except Exception as exc:
        db.rollback()
        print(f"\n[ECHEC] {type(exc).__name__}: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    test_models()