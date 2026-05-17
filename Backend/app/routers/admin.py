"""
Endpoints REST pour l'administration.
Toutes les routes sont protegees par get_current_admin.
"""
import shutil
from pathlib import Path
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.crud import dataset as crud_dataset
from app.database import get_db
from app.models import Utilisateur
from app.routers.auth import get_current_admin
from app.schemas.dataset import AdminStats, DatasetImportResult, DatasetResponse
from app.services.admin_import import import_uploaded_file


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(get_current_admin)],
)

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".csv"}
MAX_FILE_SIZE_MB = 50


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db)):
    """KPI du dashboard admin."""
    return crud_dataset.get_admin_stats(db)


@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    """Liste tous les datasets avec leurs stats."""
    from sqlalchemy import func
    from app.models import Lycee, Indicateur, ResultatBac

    datasets = crud_dataset.get_all_datasets(db)

    # On calcule le total de resultats bac une seule fois
    # (la table ResultatBac n'a pas de FK vers Dataset dans le schema actuel)
    total_resultats_bac = db.query(func.count(ResultatBac.idresultat)).scalar() or 0

    result = []
    for ds in datasets:
        # Nombre de lycees lies a ce dataset
        nb_lycees = db.query(func.count(Lycee.idlycee)).filter(
            Lycee.iddataset == ds.iddataset
        ).scalar() or 0

        # Type du dataset (deduit du nom)
        nom_lower = (ds.nomdataset or "").lower()
        is_bac = "bac" in nom_lower or "resultat" in nom_lower

        # Si dataset bac : on affiche le total de ResultatBac (compteur global)
        # Si dataset ips/lycee : on affiche le nb de lycees
        if is_bac:
            nb_lignes = total_resultats_bac
            type_dataset = "bac"
        else:
            nb_lignes = nb_lycees
            type_dataset = "lycees"

        result.append({
            "iddataset": ds.iddataset,
            "nomdataset": ds.nomdataset,
            "source": ds.source,
            "dateimportation": ds.dateimportation.isoformat() if ds.dateimportation else None,
            "etat": ds.etat,
            "nb_lignes": nb_lignes,
            "nb_lycees": nb_lycees,
            "type": type_dataset,
        })
    return result


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Retourne un dataset par son ID."""
    ds = crud_dataset.get_dataset_by_id(db, dataset_id)
    if ds is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} introuvable",
        )
    return ds


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Supprime un dataset et ses donnees liees."""
    success = crud_dataset.delete_dataset(db, dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} introuvable",
        )
    return None


@router.post(
    "/datasets/import",
    response_model=DatasetImportResult,
    status_code=status.HTTP_201_CREATED,
)
async def import_dataset(
    file: UploadFile = File(..., description="Fichier CSV"),
    nom_dataset: str = Form(...),
    source: str = Form("upload_admin"),
    db: Session = Depends(get_db),
    current_admin: Utilisateur = Depends(get_current_admin),
):
    """Upload un CSV et l'importe en BDD."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension non autorisee : {ext}",
        )

    safe_filename = Path(file.filename).name
    save_path = UPLOAD_DIR / f"{current_admin.idutilisateur}_{safe_filename}"

    try:
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    size_mb = save_path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux ({size_mb:.1f} Mo). Max: {MAX_FILE_SIZE_MB} Mo.",
        )

    try:
        result = import_uploaded_file(
            db,
            file_path=save_path,
            nom_dataset=nom_dataset,
            source=source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pendant l'import : {exc}",
        )
    # Au lieu de supprimer le fichier, on le garde pour permettre
    # le re-telechargement plus tard depuis la page data.html
    if save_path.exists() and result and "dataset" in result:
        ds_id = result["dataset"].iddataset
        permanent_path = UPLOAD_DIR / f"dataset_{ds_id}{ext}"
        try:
            # Si un ancien fichier existait deja pour ce dataset, on le remplace
            if permanent_path.exists():
                permanent_path.unlink()
            save_path.rename(permanent_path)
        except Exception:
            # Si on n'arrive pas a renommer, au moins on supprime le temp
            save_path.unlink(missing_ok=True)

    return result