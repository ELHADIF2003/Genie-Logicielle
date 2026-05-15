"""
Couche CRUD pour Lycee.
"""
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Lycee


def get_lycees(
    db: Session,
    academie_id: Optional[int] = None,
    secteur: Optional[str] = None,
    type_lycee: Optional[str] = None,
    departement: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[Lycee], int]:
    """
    Retourne une liste paginee de lycees avec filtres optionnels.
    Retourne (items, total) pour pouvoir calculer la pagination cote API.
    """
    query = db.query(Lycee)

    # Filtres dynamiques (seulement si fournis)
    if academie_id is not None:
        query = query.filter(Lycee.idacademie == academie_id)
    if secteur is not None:
        query = query.filter(Lycee.secteur == secteur)
    if type_lycee is not None:
        query = query.filter(Lycee.typelycee == type_lycee)
    if departement is not None:
        query = query.filter(Lycee.departement == departement)

    # Total AVANT pagination
    total = query.count()

    # Pagination : offset + limit
    offset = (page - 1) * page_size
    items = query.order_by(Lycee.nomlycee).offset(offset).limit(page_size).all()

    return items, total


def get_lycee_by_id(db: Session, lycee_id: int) -> Optional[Lycee]:
    """Retourne un lycee par son ID."""
    return db.query(Lycee).filter(Lycee.idlycee == lycee_id).first()