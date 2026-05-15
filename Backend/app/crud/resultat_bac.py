"""
Couche CRUD pour ResultatBac.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import ResultatBac


def get_resultats_by_academie(
    db: Session,
    academie_id: int,
    annee: Optional[int] = None,
    voie: Optional[str] = None,
    sexe: Optional[str] = None,
) -> List[ResultatBac]:
    """
    Retourne les resultats bac d'une academie.
    Filtres optionnels : annee, voie, sexe.
    """
    query = db.query(ResultatBac).filter(ResultatBac.idacademie == academie_id)

    if annee is not None:
        query = query.filter(ResultatBac.annee == annee)
    if voie is not None:
        query = query.filter(ResultatBac.voie == voie)
    if sexe is not None:
        query = query.filter(ResultatBac.sexe == sexe)

    return query.order_by(ResultatBac.annee.desc(), ResultatBac.voie).all()