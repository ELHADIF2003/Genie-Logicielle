"""
Schemas pour les indicateurs calcules (stats, agregations).
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class IndicateursNationaux(BaseModel):
    """KPI affiches sur la page d'accueil user."""
    taux_reussite_national: float
    ips_moyen_national: float
    nb_academies: int
    nb_lycees: int
    annee: int


class IndicateursAcademie(BaseModel):
    """Stats d'une academie (pour la carte et le top)."""
    idacademie: int
    nomacademie: Optional[str]
    regionacademie: Optional[str]
    ipsmoyen: Optional[float]
    taux_reussite: Optional[float]
    taux_mention: Optional[float]
    nb_admis: int
    nb_inscrits: int
    annee: int


class ComparateurAcademies(BaseModel):
    """Reponse du comparateur : 2 academies face a face."""
    annee: int
    academie_a: IndicateursAcademie
    academie_b: IndicateursAcademie


class PointCorrelation(BaseModel):
    """Un point du scatter plot IPS x Reussite."""
    idacademie: int
    nomacademie: Optional[str]
    ips: float
    taux_reussite: float


class EvolutionPoint(BaseModel):
    """Un point de la courbe d'evolution (1 annee)."""
    annee: int
    taux_reussite: float
    taux_mention: float