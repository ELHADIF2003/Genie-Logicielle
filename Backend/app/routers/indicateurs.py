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
    IndicateursRegion,           
    PointCorrelation,
    PointCorrelationRegion,      
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
    """
    Telecharge le CSV d'un dataset.
    Cherche d'abord dans uploads/ (datasets importes via admin),
    puis dans data/ (datasets initiaux).
    """
    from fastapi.responses import FileResponse
    from app.config import BASE_DIR
    from app.crud import dataset as crud_dataset

    ds = crud_dataset.get_dataset_by_id(db, dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset introuvable")

    # 1. Chercher d'abord dans uploads/ (datasets uploades via l'admin)
    uploads_dir = BASE_DIR / "uploads"
    candidate = uploads_dir / f"dataset_{dataset_id}.csv"
    if candidate.exists():
        # Nom convivial pour le telechargement
        download_name = f"{ds.nomdataset or 'dataset'}.csv".replace(" ", "_")
        return FileResponse(
            path=str(candidate),
            media_type="text/csv",
            filename=download_name,
        )

    # 2. Sinon, mapper sur les CSV initiaux dans data/
    data_dir = BASE_DIR / "data"
    file_mapping = {
        "ips-lycees": data_dir / "IPS-Lycees.csv",
        "resultats-bac": data_dir / "Résultat-Bac-Par-Academie.csv",
        "resultat-bac": data_dir / "Résultat-Bac-Par-Academie.csv",
    }

    nom_normalise = (ds.nomdataset or "").lower().replace("é", "e")
    for key, path in file_mapping.items():
        if key in nom_normalise and path.exists():
            return FileResponse(
                path=str(path),
                media_type="text/csv",
                filename=path.name,
            )

    raise HTTPException(
        status_code=404,
        detail="Fichier CSV non disponible pour ce dataset",
    )
# ============================================================
# ENDPOINTS REGIONAUX (niveau geographique = Régional)
# ============================================================

@router.get("/regions", response_model=List[IndicateursRegion])
def indicateurs_regions(
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """Stats agregees par region academique."""
    return crud_indicateur.get_indicators_by_region(db, annee=annee)


@router.get("/correlation-regions", response_model=List[PointCorrelationRegion])
def correlation_regions(
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """Points (IPS, taux_reussite) pour scatter plot, agreges par region."""
    return crud_indicateur.get_correlation_points_regions(db, annee=annee)


@router.get("/top-regions", response_model=List[IndicateursRegion])
def top_regions(
    critere: str = Query("ips", description="Critere : 'ips', 'taux_reussite', 'taux_mention'"),
    n: int = Query(5, ge=1, le=20, description="Nombre de regions"),
    annee: int | None = Query(None, description="Annee (defaut : plus recente)"),
    db: Session = Depends(get_db),
):
    """Top N regions selon un critere."""
    return crud_indicateur.get_top_regions(db, critere=critere, n=n, annee=annee)