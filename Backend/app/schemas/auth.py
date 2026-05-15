"""
Schemas Pydantic pour l'authentification.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# === REQUETES (ce que le client envoie) ===

class LoginRequest(BaseModel):
    """Donnees envoyees pour se connecter."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Donnees envoyees pour creer un nouvel utilisateur."""
    nom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 caracteres")
    role: str = Field(default="utilisateur", description="'utilisateur' ou 'admin'")


# === REPONSES (ce que l'API renvoie) ===

class TokenResponse(BaseModel):
    """Reponse apres un login reussi."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserResponse(BaseModel):
    """Infos sur un utilisateur (sans le mot de passe !)."""
    idutilisateur: int
    nomutilisateur: Optional[str]
    emailutilisateur: Optional[str]
    role: Optional[str]

    model_config = ConfigDict(from_attributes=True)