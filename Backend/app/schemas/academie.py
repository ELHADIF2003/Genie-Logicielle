"""
Schemas Pydantic pour Academie.
Definissent le format des reponses API.
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AcademieResponse(BaseModel):
    """Schema retourne par l'API pour une academie."""
    idacademie: int
    nomacademie: Optional[str]
    regionacademie: Optional[str]
    ipsmoyen: Optional[Decimal]

    # Permet a Pydantic de lire les attributs d'un objet SQLAlchemy
    model_config = ConfigDict(from_attributes=True)