"""
Endpoints REST pour les lycees.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import lycee as crud_lycee
from app.database import get_db
from app.schemas.lycee import LyceeListResponse, LyceeResponse


router = APIRouter(
    prefix="/lycees",
    tags=["Lycees"],
)


@router.get("/", response_model=LyceeListResponse)
def list_lycees(
    academie_id: int | None = Query(None, description="Filtrer par ID d'academie"),
    secteur: str | None = Query(None, description="'public' ou 'prive sous contrat'"),
    type_lycee: str | None = Query(None, description="LEGT, LP, LPO"),
    departement: str | None = Query(None, description="Code departement (ex: 75)"),
    page: int = Query(1, ge=1, description="Numero de page"),
    page_size: int = Query(50, ge=1, le=200, description="Nb de resultats par page"),
    db: Session = Depends(get_db),
):
    """
    Liste paginee des lycees avec filtres optionnels.

    Exemples :
    - `/lycees/` : tous les lycees, page 1
    - `/lycees/?academie_id=5` : lycees de l'academie 5
    - `/lycees/?secteur=public&page=2` : 2eme page des lycees publics
    """
    items, total = crud_lycee.get_lycees(
        db,
        academie_id=academie_id,
        secteur=secteur,
        type_lycee=type_lycee,
        departement=departement,
        page=page,
        page_size=page_size,
    )
    return LyceeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get("/{lycee_id}", response_model=LyceeResponse)
def get_lycee(lycee_id: int, db: Session = Depends(get_db)):
    """Retourne un lycee par son ID."""
    lyc = crud_lycee.get_lycee_by_id(db, lycee_id)
    if lyc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lycee {lycee_id} introuvable",
        )
    return lyc