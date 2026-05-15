"""
Endpoints REST pour l'authentification.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import utilisateur as crud_user
from app.database import get_db
from app.models import Utilisateur
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security import create_access_token, decode_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)


# === Dependance pour recuperer le token depuis le header Authorization ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ============================================================
# DEPENDANCES DE PROTECTION DES ROUTES
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    """
    Dependance : recupere l'utilisateur courant depuis le token JWT.
    A utiliser avec Depends(get_current_user) pour proteger une route.
    Leve 401 si le token est invalide / expire / utilisateur introuvable.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expire",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin(
    current_user: Utilisateur = Depends(get_current_user),
) -> Utilisateur:
    """
    Dependance : verifie que l'utilisateur courant est admin.
    A utiliser sur les routes admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux administrateurs",
        )
    return current_user


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Cree un nouvel utilisateur.
    En pratique : a proteger par get_current_admin pour eviter qu'on puisse
    creer des admins librement. Pour l'instant on laisse ouvert pour pouvoir
    creer le premier admin.
    """
    # Verifier que l'email n'est pas deja pris
    existing = crud_user.get_user_by_email(db, email=request.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'email {request.email} est deja utilise",
        )

    user = crud_user.create_user(
        db,
        nom=request.nom,
        email=request.email,
        password=request.password,
        role=request.role,
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Connexion : verifie email + password, retourne un JWT.
    """
    user = crud_user.authenticate_user(db, email=request.email, password=request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    token = create_access_token(
        subject=user.emailutilisateur,
        extra_claims={"role": user.role, "id": user.idutilisateur},
    )

    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Utilisateur = Depends(get_current_user)):
    """
    Retourne l'utilisateur courant.
    Protege : requiert un token JWT valide.
    """
    return current_user
@router.post("/token", response_model=TokenResponse, include_in_schema=True)
def login_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Endpoint compatible OAuth2 (form-data) pour le bouton Authorize de Swagger.
    Utilise le champ 'username' pour l'email.
    Les clients normaux (ton front) utilisent /auth/login avec du JSON.
    """
    user = crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=user.emailutilisateur,
        extra_claims={"role": user.role, "id": user.idutilisateur},
    )
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
    )