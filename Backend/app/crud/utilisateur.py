"""
Couche CRUD pour Utilisateur.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Utilisateur
from app.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[Utilisateur]:
    """Retourne un utilisateur par son email, ou None."""
    return db.query(Utilisateur).filter(Utilisateur.emailutilisateur == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[Utilisateur]:
    """Retourne un utilisateur par son ID, ou None."""
    return db.query(Utilisateur).filter(Utilisateur.idutilisateur == user_id).first()


def create_user(
    db: Session,
    nom: str,
    email: str,
    password: str,
    role: str = "utilisateur",
) -> Utilisateur:
    """
    Cree un utilisateur avec un mot de passe hache.
    Le mot de passe en clair n'est JAMAIS stocke.
    """
    user = Utilisateur(
        nomutilisateur=nom,
        emailutilisateur=email,
        motdepassehash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[Utilisateur]:
    """
    Verifie les credentials.
    Retourne l'utilisateur si OK, None sinon.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.motdepassehash):
        return None
    return user