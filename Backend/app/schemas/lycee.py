"""
Schemas Pydantic pour Lycee.
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LyceeResponse(BaseModel):
    """Schema retourne par l'API pour un lycee."""
    idlycee: int
    nomlycee: Optional[str]
    secteur: Optional[str]
    typelycee: Optional[str]
    departement: Optional[str]
    ips: Optional[Decimal]
    idacademie: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class LyceeListResponse(BaseModel):
    """Reponse pour une liste paginee de lycees."""
    total: int
    page: int
    page_size: int
    items: list[LyceeResponse]