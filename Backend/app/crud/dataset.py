"""
Couche CRUD pour Dataset.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Academie, Dataset, Indicateur, Lycee, ResultatBac, Utilisateur


def get_all_datasets(db: Session) -> List[Dataset]:
    """Retourne tous les datasets tries par date d'import."""
    return db.query(Dataset).order_by(Dataset.dateimportation.desc()).all()


def get_dataset_by_id(db: Session, dataset_id: int) -> Optional[Dataset]:
    return db.query(Dataset).filter(Dataset.iddataset == dataset_id).first()


def delete_dataset(db: Session, dataset_id: int) -> bool:
    """
    Supprime un dataset et toutes les donnees liees.
    Retourne True si supprime, False si introuvable.
    """
    ds = db.query(Dataset).filter(Dataset.iddataset == dataset_id).first()
    if ds is None:
        return False

    # Supprimer d'abord les lignes liees (les FK ne sont pas en CASCADE)
    db.query(Lycee).filter(Lycee.iddataset == dataset_id).delete()
    db.query(Indicateur).filter(Indicateur.iddataset == dataset_id).delete()

    db.delete(ds)
    db.commit()
    return True


def get_admin_stats(db: Session) -> dict:
    """Calcule les stats pour le dashboard admin."""
    nb_datasets = db.query(func.count(Dataset.iddataset)).scalar() or 0
    nb_academies = db.query(func.count(Academie.idacademie)).scalar() or 0
    nb_lycees = db.query(func.count(Lycee.idlycee)).scalar() or 0
    nb_bac = db.query(func.count(ResultatBac.idresultat)).scalar() or 0
    nb_users = db.query(func.count(Utilisateur.idutilisateur)).scalar() or 0
    dernier = db.query(func.max(Dataset.dateimportation)).scalar()

    return {
        "nb_datasets": nb_datasets,
        "nb_academies": nb_academies,
        "nb_lycees": nb_lycees,
        "nb_resultats_bac": nb_bac,
        "nb_utilisateurs": nb_users,
        "dernier_import": dernier,
    }