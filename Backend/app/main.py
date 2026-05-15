"""
Point d'entree de l'application FastAPI.
API REST pour la plateforme IDMC - EduData France.

Usage (depuis Backend/) : uvicorn app.main:app --reload
Documentation interactive : http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import academies, admin, auth, indicateurs, lycees


# === Metadonnees pour la documentation OpenAPI ===
TAGS_METADATA = [
    {
        "name": "Root",
        "description": "Endpoint racine de l'API.",
    },
    {
        "name": "Authentification",
        "description": "Connexion, inscription et gestion des sessions JWT.",
    },
    {
        "name": "Academies",
        "description": "Acces public aux donnees des academies francaises.",
    },
    {
        "name": "Lycees",
        "description": "Acces public aux donnees des lycees (avec pagination et filtres).",
    },
    {
        "name": "Indicateurs",
        "description": "Indicateurs calcules : KPI nationaux, correlations, top 5, evolution temporelle.",
    },
    {
        "name": "Administration",
        "description": "Endpoints reserves aux administrateurs (authentification JWT requise).",
    },
]


DESCRIPTION = """
## 📊 IDMC - EduData France API

API REST pour la plateforme d'analyse des inegalites educatives entre academies en France.

### Fonctionnalites principales

- 🏛️ **Donnees publiques** : academies, lycees, resultats du bac
- 📈 **Indicateurs calcules** : taux de reussite, IPS moyen, correlations
- 🔐 **Espace admin** : import de datasets, gestion (authentification JWT)
- 📊 **Documentation interactive** : Swagger UI sur `/docs`, ReDoc sur `/redoc`

### Securite

- Mots de passe haches avec **bcrypt** (rounds=12)
- Sessions geres par **JWT** (algorithme HS256)
- Routes admin protegees par dependance FastAPI

### Stack

- **Framework** : FastAPI + Uvicorn
- **ORM** : SQLAlchemy
- **BDD** : PostgreSQL
- **Validation** : Pydantic v2

---

*Projet realise dans le cadre du M1 MIAGE - IDMC (Universite de Lorraine)*
"""


app = FastAPI(
    title="IDMC - EduData France API",
    description=DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Equipe IDMC - M1 MIAGE",
        "url": "https://github.com/ELHADIF2003/Genie-Logicielle",
    },
    license_info={
        "name": "Licence academique - Universite de Lorraine",
    },
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
)


# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Routers ===
app.include_router(auth.router)
app.include_router(academies.router)
app.include_router(lycees.router)
app.include_router(indicateurs.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"])
def read_root():
    """Endpoint de bienvenue."""
    return {
        "message": "Bienvenue sur l'API IDMC - EduData France",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }