"""
Schemas Pydantic pour ResultatBac.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResultatBacResponse(BaseModel):
    """Resultat bac pour une academie / annee / voie / sexe."""
    idresultat: int
    annee: int
    voie: Optional[str]
    sexe: Optional[str]
    nbinscrits: int
    nbadmis: int
    nbmentiontb: int
    nbmentionb: int
    nbmentionab: int
    nbadmissansmention: int
    nbrefuses: int
    idacademie: Optional[int]

    model_config = ConfigDict(from_attributes=True)