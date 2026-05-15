"""
Regroupement des modeles ORM.
Permet d'importer facilement : from app.models import Academie, Lycee, ...
"""
from app.models.academie import Academie
from app.models.dataset import Dataset
from app.models.lycee import Lycee
from app.models.resultat_bac import ResultatBac
from app.models.indicateur import Indicateur
from app.models.utilisateur import Utilisateur

__all__ = [
    "Academie",
    "Dataset",
    "Lycee",
    "ResultatBac",
    "Indicateur",
    "Utilisateur",
]