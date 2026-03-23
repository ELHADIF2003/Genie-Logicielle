# [IDMC - Génie Logicielle]
---
**Auteurs** :   EL HADIF Abderrahmane
                LAHMAR Mohamed Reda 
                BASSE Gregory
                
**Promotion** : Master MIAGE - IDMC

## Projet : Éducation et Performance Académique en France
[cite_start]Ce projet consiste à réaliser une plateforme interactive permettant aux utilisateurs d’explorer et d’analyser les données éducatives à travers des visualisations graphiques et des indicateurs statistiques[cite: 3].

## 📌 Problématique
[cite_start]Existe-t-il des inégalités structurelles entre académies en France en fonction des moyens éducatifs, de la composition sociale des élèves et des résultats scolaires ? [cite: 9]

## 📊 Fonctionnalités principales
L'application propose les services suivants selon le profil utilisateur :

### Pour l'Utilisateur :
* [cite_start]**Consultation et filtrage** des données par académie[cite: 27, 29, 30].
* [cite_start]**Visualisation interactive** via des graphiques et une carte de France[cite: 28, 32, 40].
* [cite_start]**Exportation** des données pour usage externe[cite: 33].

### Pour l'Administrateur :
* [cite_start]**Gestion des données** : Importation, nettoyage (suppression des doublons, normalisation) et fusion des datasets[cite: 36, 37, 46, 50].
* [cite_start]**Maintenance** : Mise à jour des tableaux de bord et gestion de la base de données[cite: 42, 51].

## 🛠 Architecture Technique
[cite_start]L'application repose sur la stack technologique suivante[cite: 60]:
* **Frontend** : HTML, CSS, JavaScript.
* **Backend** : Python.
* **Base de données** : Relationnelle (PostgreSQL ou SQLite).
* **Visualisation** : Bibliothèques spécialisées (Plotly, Chart.js ou D3.js).

## 📈 Indicateurs et Analyses
[cite_start]Le système calcule automatiquement plusieurs indicateurs clés[cite: 38, 39]:
* [cite_start]Taux de réussite et de mentions au baccalauréat (période 2021-2024)[cite: 19, 38].
* [cite_start]Indice de Position Sociale (IPS) moyen par académie[cite: 38].
* [cite_start]Analyse de corrélation entre l'IPS et la réussite scolaire[cite: 39, 81].

## 📁 Documentation Logicielle
[cite_start]Conformément aux exigences de Génie Logiciel, le dépôt inclut les diagrammes UML suivants[cite: 62, 68]:
* Diagrammes de Cas d’utilisation et de Séquence.
* Diagrammes de Classe et d'Activités.
* Diagramme d’État-transition.
* Modèle Physique de Données (MPD).

## 🚀 Installation et Lancement
*(Section à compléter par l'équipe lors du développement)*
1. Cloner le dépôt : `git clone [URL_DU_DEPOT]`
2. Installer les dépendances : `pip install -r requirements.txt`
3. Lancer l'application : `python src/backend/app.py`

