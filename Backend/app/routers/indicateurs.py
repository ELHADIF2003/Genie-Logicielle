"""
Endpoints REST pour les indicateurs calcules.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import indicateur as crud_indicateur
from app.crud import academie as crud_academie
from app.database import get_db
from app.schemas.indicateur import (
    ComparateurAcademies,
    EvolutionPoint,
    IndicateursAcademie,
    IndicateursNationaux,
    PointCorrelation,
)


router = APIRouter(
    prefix="/indicateurs",
    tags=["Indicateurs"],
)


@router.get("/national", response_model=IndicateursNationaux)
def indicateurs_national(
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """
    KPI nationaux pour la page d'accueil user :
    - taux de reussite national
    - IPS moyen national
    - nb academies, nb lycees
    """
    return crud_indicateur.get_national_indicators(db, annee=annee)


@router.get("/academies", response_model=List[IndicateursAcademie])
def indicateurs_academies(
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """
    Stats par academie pour l'annee donnee.
    Utilise pour la carte interactive, le tableau, etc.
    """
    return crud_indicateur.get_indicators_by_academie(db, annee=annee)


@router.get("/comparateur", response_model=ComparateurAcademies)
def comparateur(
    acad_a: int = Query(..., description="ID de la 1ere academie"),
    acad_b: int = Query(..., description="ID de la 2eme academie"),
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """
    Comparateur : retourne les stats de 2 academies pour comparaison.
    """
    # Verifier que les 2 academies existent
    if crud_academie.get_academie_by_id(db, acad_a) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academie A ({acad_a}) introuvable",
        )
    if crud_academie.get_academie_by_id(db, acad_b) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academie B ({acad_b}) introuvable",
        )

    stats_a = crud_indicateur.get_indicators_by_academie(db, annee=annee, academie_id=acad_a)
    stats_b = crud_indicateur.get_indicators_by_academie(db, annee=annee, academie_id=acad_b)

    # get_indicators_by_academie retourne une liste, mais filtre => 1 seule entree
    return ComparateurAcademies(
        annee=stats_a[0]["annee"],
        academie_a=stats_a[0],
        academie_b=stats_b[0],
    )


@router.get("/correlation", response_model=List[PointCorrelation])
def correlation_ips_reussite(
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """
    Points (IPS, taux_reussite) pour le scatter plot.
    1 point = 1 academie.
    """
    return crud_indicateur.get_correlation_points(db, annee=annee)


@router.get("/evolution", response_model=List[EvolutionPoint])
def evolution_nationale(db: Session = Depends(get_db)):
    """
    Evolution du taux de reussite et mention par annee (niveau national).
    Pour le line chart de la page graphiques.
    """
    return crud_indicateur.get_evolution_nationale(db)


@router.get("/top-academies", response_model=List[IndicateursAcademie])
def top_academies(
    critere: str = Query("ips", description="Critere : 'ips', 'taux_reussite', 'taux_mention'"),
    n: int = Query(5, ge=1, le=30, description="Nombre d'academies"),
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """
    Top N academies selon un critere.
    Pour le bar chart de la page graphiques.
    """
    return crud_indicateur.get_top_academies(db, critere=critere, n=n, annee=annee)

@router.get("/datasets-publics", response_model=list[dict])
def list_public_datasets(db: Session = Depends(get_db)):
    """
    Liste publique des datasets disponibles (pour la page data.html).
    Pas d'authentification requise.
    """
    from app.crud import dataset as crud_dataset
    datasets = crud_dataset.get_all_datasets(db)
    return [
        {
            "iddataset": ds.iddataset,
            "nomdataset": ds.nomdataset,
            "source": ds.source,
            "dateimportation": ds.dateimportation.isoformat() if ds.dateimportation else None,
            "etat": ds.etat,
        }
        for ds in datasets
    ]

@router.get("/datasets-publics/{dataset_id}/download")
def download_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Telecharge le CSV original d'un dataset."""
    from fastapi.responses import FileResponse
    from app.config import BASE_DIR
    from app.crud import dataset as crud_dataset

    ds = crud_dataset.get_dataset_by_id(db, dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset introuvable")

    # Mapping nom dataset -> fichier CSV
    data_dir = BASE_DIR / "data"
    file_mapping = {
        "ips-lycees": data_dir / "IPS-Lycees.csv",
        "resultats-bac": data_dir / "Résultat-Bac-Par-Academie.csv",
    }

    # Recherche tolérante (en minuscules, sans accents)
    nom_normalise = (ds.nomdataset or "").lower().replace("é", "e")
    csv_path = None
    for key, path in file_mapping.items():
        if key in nom_normalise:
            csv_path = path
            break

    if csv_path is None or not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Fichier CSV non disponible pour ce dataset",
        )

    return FileResponse(
        path=str(csv_path),
        media_type="text/csv",
        filename=csv_path.name,
    )