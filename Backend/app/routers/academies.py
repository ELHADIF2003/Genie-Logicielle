"""
Endpoints REST pour les academies et leurs resultats bac.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import academie as crud_academie
from app.crud import resultat_bac as crud_resultat
from app.database import get_db
from app.schemas.academie import AcademieResponse
from app.schemas.resultat_bac import ResultatBacResponse


router = APIRouter(
    prefix="/academies",
    tags=["Academies"],
)


@router.get("/", response_model=List[AcademieResponse])
def list_academies(db: Session = Depends(get_db)):
    """Retourne la liste de toutes les academies."""
    return crud_academie.get_all_academies(db)


@router.get("/{academie_id}", response_model=AcademieResponse)
def get_academie(academie_id: int, db: Session = Depends(get_db)):
    """Retourne une academie par son ID."""
    acad = crud_academie.get_academie_by_id(db, academie_id)
    if acad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academie {academie_id} introuvable",
        )
    return acad


@router.get("/{academie_id}/resultats-bac", response_model=List[ResultatBacResponse])
def get_academie_resultats(
    academie_id: int,
    annee: int | None = Query(None, description="Filtrer par annee (ex: 2023)"),
    voie: str | None = Query(None, description="Filtrer par voie (ex: BAC GENERAL)"),
    sexe: str | None = Query(None, description="Filtrer par sexe (F ou M)"),
    db: Session = Depends(get_db),
):
    """
    Retourne les resultats du bac pour une academie donnee.
    Filtres optionnels : annee, voie, sexe.
    """
    # Verifier que l'academie existe
    acad = crud_academie.get_academie_by_id(db, academie_id)
    if acad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academie {academie_id} introuvable",
        )

    return crud_resultat.get_resultats_by_academie(
        db,
        academie_id=academie_id,
        annee=annee,
        voie=voie,
        sexe=sexe,
    )