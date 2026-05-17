# 📊 IDMC - ÉduData France

> Plateforme d'analyse des inégalités éducatives entre académies en France.

**Promotion** : Master 1 MIAGE - IDMC (Université de Lorraine)

**Auteurs** :
- EL HADIF Abderrahmane
- LAHMAR Mohamed Reda
- BASSE Gregory
- Mahamat Garba Hadjé Aché
- KIAZI TSAKA NGOMA Febbe

---

## 🎯 Problématique

> Existe-t-il des inégalités structurelles entre académies en France en fonction des moyens éducatifs, de la composition sociale des élèves et des résultats scolaires ?

Le projet propose une plateforme interactive permettant d'explorer et d'analyser les données éducatives à travers des visualisations graphiques et des indicateurs statistiques.

## 📊 Fonctionnalités

### Espace Utilisateur (public)
- 🏠 **Accueil** : KPI nationaux (taux de réussite, IPS moyen, nb académies)
- 🗺️ **Carte interactive** : visualisation géographique des indicateurs (Leaflet)
- 📈 **Graphiques** : corrélation IPS × Réussite, Top 5 académies, évolution temporelle
- ⚖️ **Comparateur** : confrontation directe de 2 académies
- 📦 **Catalogue Open Data** : liste des datasets disponibles

### Espace Administrateur (authentifié)
- 🔐 **Connexion sécurisée** : bcrypt + JWT
- 📊 **Dashboard** : suivi technique de la plateforme
- 📥 **Import de datasets** : upload de fichiers CSV avec détection automatique du type
- 🗑️ **Gestion des datasets** : suppression en cascade

## 🛠️ Stack technique

| Couche | Technologie |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (vanilla), Chart.js, Leaflet |
| **Backend** | Python 3.13, FastAPI, SQLAlchemy ORM |
| **Base de données** | PostgreSQL 18 |
| **Authentification** | bcrypt (hashing), JWT (sessions) |
| **Data processing** | pandas, numpy |
| **Documentation API** | OpenAPI / Swagger (auto-générée) |

## 📦 Installation

### Prérequis

- Python 3.11+ ([python.org](https://www.python.org/))
- PostgreSQL 14+ ([postgresql.org](https://www.postgresql.org/))
- VS Code avec extension Live Server (recommandé pour le front)

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd Genie-Logicielle
```

### 2. Configurer la base de données

Dans pgAdmin ou via psql, créer la base :

```sql
CREATE DATABASE projet_gl;
```

Puis exécuter le script de création des tables :

```bash
# Soit via pgAdmin (Query Tool > Open File > database/BDD.sql)
# Soit via psql :
psql -U postgres -d projet_gl -f database/BDD.sql
```

### 3. Créer l'environnement Python

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copier le modèle et adapter avec vos identifiants :

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac
```

Éditer `.env` :
```env
DB_USER=postgres
DB_PASSWORD=votre_mdp
DB_HOST=localhost
DB_PORT=5432
DB_NAME=projet_gl

JWT_SECRET_KEY=changez_moi_en_une_chaine_aleatoire_longue
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### 5. Importer les données initiales

Placer les CSV dans `data/` :
- `IPS-Lycees.csv`
- `Résultat-Bac-Par-Academie.csv`

Puis lancer le pipeline ETL :

```bash
cd Backend
python -m app.scripts.run_import
```

### 6. Créer le premier admin

```bash
python -m app.scripts.create_admin
```

### 7. Lancer le back-end

```bash
uvicorn app.main:app --reload
```

L'API est accessible sur : **http://localhost:8000**

Documentation interactive : **http://localhost:8000/docs**

### 8. Lancer le front-end

Dans VS Code, clic droit sur `Front-End/Home/home.html` → **"Open with Live Server"**.

Ou via Python :
```bash
cd Front-End
python -m http.server 5500
```

Le front est accessible sur : **http://127.0.0.1:5500/Front-End/Home/home.html**

## 📁 Architecture du projet

```
Genie-Logicielle/
├── Backend/                          # API FastAPI
│   └── app/
│       ├── main.py                   # Point d'entrée FastAPI
│       ├── config.py                 # Configuration (.env)
│       ├── database.py               # Connexion SQLAlchemy
│       ├── security.py               # bcrypt + JWT
│       ├── models/                   # Modèles ORM
│       ├── schemas/                  # Schémas Pydantic
│       ├── routers/                  # Endpoints REST
│       ├── crud/                     # Requêtes BDD
│       ├── services/                 # Logique métier (ETL)
│       └── scripts/                  # Scripts utilitaires
│
├── Front-End/                        # Pages HTML/CSS/JS
│   ├── Home/                         # Page d'accueil
│   ├── User/                         # Pages utilisateur
│   ├── Admin/                        # Pages administrateur
│   ├── js/                           # Scripts partagés
│   └── data/                         # GeoJSON (carte)
│
├── database/
│   └── BDD.sql                       # Script de création des tables
│
├── data/                             # CSV sources (non commités)
├── .env.example                      # Modèle des variables d'env
├── .gitignore
├── requirements.txt
└── README.md
```
## 📈 Indicateurs calculés

Le système calcule automatiquement :
- **Taux de réussite au bac** par académie, année, voie, sexe
- **Taux de mentions** (TB + B + AB) / total admis
- **Indice de Position Sociale (IPS)** moyen par académie
- **Corrélation IPS × Réussite** (nuage de points)
- **Évolution temporelle** des taux nationaux (2021-2024)

## 🔐 Sécurité

- Mots de passe hachés avec **bcrypt** (rounds=12)
- Sessions gérées par **JWT** signés HS256 (expiration 60 min)
- Routes admin protégées par dépendance FastAPI `get_current_admin`
- CORS configuré (à restreindre en production)
- Variables sensibles dans `.env` (jamais commité)

## 📁 Documentation logicielle

Conformément aux exigences de Génie Logiciel, le dépôt inclut :
- Diagrammes de Cas d'utilisation et de Séquence
- Diagrammes de Classe et d'Activités
- Diagramme d'État-transition
- Modèle Physique de Données (MPD)

## 📚 API

L'API expose les routes suivantes (documentation interactive sur `/docs`) :

### Publiques
- `GET /academies/` — Liste des académies
- `GET /academies/{id}` — Détail d'une académie
- `GET /academies/{id}/resultats-bac` — Résultats bac par académie
- `GET /lycees/` — Liste paginée des lycées (filtres : académie, secteur, type, département)
- `GET /lycees/{id}` — Détail d'un lycée
- `GET /indicateurs/national` — KPI nationaux
- `GET /indicateurs/academies` — Stats par académie
- `GET /indicateurs/comparateur` — Comparaison 2 académies
- `GET /indicateurs/correlation` — Données scatter plot
- `GET /indicateurs/evolution` — Évolution temporelle
- `GET /indicateurs/top-academies` — Top N selon un critère
- `GET /indicateurs/datasets-publics` — Catalogue des datasets

### Authentification
- `POST /auth/register` — Créer un utilisateur
- `POST /auth/login` — Connexion (JSON)
- `POST /auth/token` — Connexion (form-data, pour Swagger)
- `GET /auth/me` — Profil de l'utilisateur courant

### Admin (protégées)
- `GET /admin/stats` — KPI du dashboard
- `GET /admin/datasets` — Liste des datasets
- `GET /admin/datasets/{id}` — Détail d'un dataset
- `POST /admin/datasets/import` — Upload + import d'un CSV
- `DELETE /admin/datasets/{id}` — Supprimer un dataset

## 🧪 Tests

```bash
cd Backend
pytest
```

## 📄 Licence

Projet académique réalisé dans le cadre du M1 MIAGE - IDMC (Université de Lorraine), promotion 2025-2026.

Les données utilisées sont publiées sous **Licence Ouverte (Etalab)** par le Ministère de l'Éducation Nationale.