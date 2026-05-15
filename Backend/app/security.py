"""
Fonctions de securite :
- Hashage et verification de mots de passe (bcrypt)
- Creation et decodage de tokens JWT
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.config import settings


# Limite de bcrypt : 72 bytes max pour le mot de passe
_BCRYPT_MAX_BYTES = 72


# ============================================================
# HASHAGE DES MOTS DE PASSE
# ============================================================

def hash_password(password: str) -> str:
    """
    Hache un mot de passe en clair avec bcrypt.
    Retourne le hash (string) a stocker en BDD.
    """
    # bcrypt travaille sur des bytes ; on tronque a 72 bytes si necessaire
    password_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifie qu'un mot de passe en clair correspond au hash bcrypt.
    Retourne True si OK, False sinon.
    """
    try:
        password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================================
# JSON WEB TOKENS (JWT)
# ============================================================

def create_access_token(
    subject: str,
    extra_claims: Optional[dict] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Genere un token JWT signe.
    """
    if expires_minutes is None:
        expires_minutes = settings.JWT_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode et verifie un token JWT.
    Retourne le payload si valide, None sinon.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None