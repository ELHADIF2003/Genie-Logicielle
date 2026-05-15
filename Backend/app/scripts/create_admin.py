"""
Script interactif pour creer le premier admin.
Usage (depuis Backend/) : python -m app.scripts.create_admin
"""
from getpass import getpass

from app.crud import utilisateur as crud_user
from app.database import SessionLocal


def main() -> None:
    print("=" * 60)
    print("CREATION D'UN ADMIN")
    print("=" * 60)

    nom = input("Nom complet : ").strip()
    email = input("Email : ").strip().lower()
    password = getpass("Mot de passe (min 6 car.) : ")
    password2 = getpass("Confirmer le mot de passe : ")

    if password != password2:
        print("\n[ECHEC] Les mots de passe ne correspondent pas.")
        return

    if len(password) < 6:
        print("\n[ECHEC] Le mot de passe doit faire au moins 6 caracteres.")
        return

    db = SessionLocal()
    try:
        existing = crud_user.get_user_by_email(db, email=email)
        if existing is not None:
            print(f"\n[ECHEC] L'email {email} est deja utilise (id={existing.idutilisateur}).")
            return

        user = crud_user.create_user(
            db,
            nom=nom,
            email=email,
            password=password,
            role="admin",
        )
        print()
        print("=" * 60)
        print("ADMIN CREE AVEC SUCCES")
        print("=" * 60)
        print(f"   ID    : {user.idutilisateur}")
        print(f"   Email : {user.emailutilisateur}")
        print(f"   Role  : {user.role}")

    finally:
        db.close()


if __name__ == "__main__":
    main()