"""
Couche CRUD pour Academie.
Regroupe toutes les requetes BDD liees aux academies.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Academie


def get_all_academies(db: Session) -> List[Academie]:
    """Retourne toutes les academies, triees par nom."""
    return db.query(Academie).order_by(Academie.nomacademie).all()


def get_academie_by_id(db: Session, academie_id: int) -> Optional[Academie]:
    """Retourne une academie par son ID, ou None si introuvable."""
    return db.query(Academie).filter(Academie.idacademie == academie_id).first()