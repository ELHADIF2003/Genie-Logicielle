"""
Schemas Pydantic pour Dataset et endpoints admin.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    """Infos sur un dataset."""
    iddataset: int
    nomdataset: Optional[str]
    source: Optional[str]
    dateimportation: Optional[datetime]
    etat: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DatasetImportResult(BaseModel):
    """Resultat d'un import de dataset."""
    dataset: DatasetResponse
    type_detecte: str
    nb_lignes_brutes: int
    nb_lignes_importees: int
    nb_academies: int
    nb_lycees: int
    nb_resultats_bac: int
    message: str


class AdminStats(BaseModel):
    """KPI du dashboard admin."""
    nb_datasets: int
    nb_academies: int
    nb_lycees: int
    nb_resultats_bac: int
    nb_utilisateurs: int
    dernier_import: Optional[datetime]