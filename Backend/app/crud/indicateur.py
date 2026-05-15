"""
CRUD pour les indicateurs calcules.
C'est ici que vit la "logique metier" du projet :
calcul des taux, agregations, correlations.
"""
from typing import List, Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models import Academie, Lycee, ResultatBac


# ============================================================
# ANNEE MAX (par defaut pour les stats)
# ============================================================

def get_latest_year(db: Session) -> int:
    """Retourne l'annee la plus recente dans ResultatBac."""
    result = db.query(func.max(ResultatBac.annee)).scalar()
    return result if result else 2024


# ============================================================
# INDICATEURS NATIONAUX (pour les KPI du hero)
# ============================================================

def get_national_indicators(db: Session, annee: Optional[int] = None) -> dict:
    """
    Calcule les 3 KPI nationaux du hero accueil :
    - taux de reussite national (= somme admis / somme inscrits)
    - IPS moyen national (moyenne des IPS des lycees)
    - nb academies
    - nb lycees
    """
    if annee is None:
        annee = get_latest_year(db)

    # Sommes globales des inscrits et admis pour l'annee
    totals = db.query(
        func.sum(ResultatBac.nbinscrits).label("total_inscrits"),
        func.sum(ResultatBac.nbadmis).label("total_admis"),
    ).filter(ResultatBac.annee == annee).first()

    total_inscrits = int(totals.total_inscrits or 0)
    total_admis = int(totals.total_admis or 0)

    taux_reussite = (total_admis / total_inscrits * 100) if total_inscrits > 0 else 0.0

    # IPS moyen national (moyenne des IPS de tous les lycees)
    ips_moyen = db.query(func.avg(Lycee.ips)).scalar()
    ips_moyen = float(ips_moyen) if ips_moyen else 0.0

    # Comptes
    nb_academies = db.query(func.count(Academie.idacademie)).scalar()
    nb_lycees = db.query(func.count(Lycee.idlycee)).scalar()

    return {
        "taux_reussite_national": round(taux_reussite, 2),
        "ips_moyen_national": round(ips_moyen, 2),
        "nb_academies": nb_academies,
        "nb_lycees": nb_lycees,
        "annee": annee,
    }


# ============================================================
# INDICATEURS PAR ACADEMIE (carte, top, comparateur)
# ============================================================

def get_indicators_by_academie(
    db: Session,
    annee: Optional[int] = None,
    academie_id: Optional[int] = None,
) -> List[dict]:
    """
    Calcule les indicateurs par academie pour une annee donnee.
    - taux de reussite = admis / inscrits
    - taux de mention = (TB + B + AB) / admis
    - IPS moyen = deja stocke dans Academie.ipsmoyen

    Si academie_id fourni : retourne juste cette academie (pour le comparateur).
    Sinon : toutes les academies.
    """
    if annee is None:
        annee = get_latest_year(db)

    # Pour chaque academie, on somme les inscrits/admis/mentions pour l'annee
    query = (
        db.query(
            Academie.idacademie,
            Academie.nomacademie,
            Academie.regionacademie,
            Academie.ipsmoyen,
            func.sum(ResultatBac.nbinscrits).label("nb_inscrits"),
            func.sum(ResultatBac.nbadmis).label("nb_admis"),
            func.sum(
                ResultatBac.nbmentiontb + ResultatBac.nbmentionb + ResultatBac.nbmentionab
            ).label("nb_mentions"),
        )
        .outerjoin(ResultatBac, (ResultatBac.idacademie == Academie.idacademie)
                                & (ResultatBac.annee == annee))
        .group_by(
            Academie.idacademie,
            Academie.nomacademie,
            Academie.regionacademie,
            Academie.ipsmoyen,
        )
    )

    if academie_id is not None:
        query = query.filter(Academie.idacademie == academie_id)

    query = query.order_by(Academie.nomacademie)

    results = []
    for row in query.all():
        nb_inscrits = int(row.nb_inscrits or 0)
        nb_admis = int(row.nb_admis or 0)
        nb_mentions = int(row.nb_mentions or 0)

        taux_reussite = (nb_admis / nb_inscrits * 100) if nb_inscrits > 0 else None
        taux_mention = (nb_mentions / nb_admis * 100) if nb_admis > 0 else None

        results.append({
            "idacademie": row.idacademie,
            "nomacademie": row.nomacademie,
            "regionacademie": row.regionacademie,
            "ipsmoyen": float(row.ipsmoyen) if row.ipsmoyen else None,
            "taux_reussite": round(taux_reussite, 2) if taux_reussite is not None else None,
            "taux_mention": round(taux_mention, 2) if taux_mention is not None else None,
            "nb_admis": nb_admis,
            "nb_inscrits": nb_inscrits,
            "annee": annee,
        })

    return results


# ============================================================
# CORRELATION IPS x REUSSITE (scatter plot)
# ============================================================

def get_correlation_points(db: Session, annee: Optional[int] = None) -> List[dict]:
    """
    Retourne les points (ips, taux_reussite) pour le nuage de points.
    Un point = une academie.
    """
    indicators = get_indicators_by_academie(db, annee=annee)
    points = []
    for ind in indicators:
        if ind["ipsmoyen"] is not None and ind["taux_reussite"] is not None:
            points.append({
                "idacademie": ind["idacademie"],
                "nomacademie": ind["nomacademie"],
                "ips": ind["ipsmoyen"],
                "taux_reussite": ind["taux_reussite"],
            })
    return points


# ============================================================
# EVOLUTION NATIONALE (line chart)
# ============================================================

def get_evolution_nationale(db: Session) -> List[dict]:
    """
    Retourne l'evolution du taux de reussite et mention par annee (niveau national).
    """
    query = (
        db.query(
            ResultatBac.annee,
            func.sum(ResultatBac.nbinscrits).label("inscrits"),
            func.sum(ResultatBac.nbadmis).label("admis"),
            func.sum(
                ResultatBac.nbmentiontb + ResultatBac.nbmentionb + ResultatBac.nbmentionab
            ).label("mentions"),
        )
        .group_by(ResultatBac.annee)
        .order_by(ResultatBac.annee)
    )

    results = []
    for row in query.all():
        inscrits = int(row.inscrits or 0)
        admis = int(row.admis or 0)
        mentions = int(row.mentions or 0)

        results.append({
            "annee": row.annee,
            "taux_reussite": round(admis / inscrits * 100, 2) if inscrits > 0 else 0.0,
            "taux_mention": round(mentions / admis * 100, 2) if admis > 0 else 0.0,
        })

    return results


# ============================================================
# TOP N ACADEMIES (pour le bar chart)
# ============================================================

def get_top_academies(
    db: Session,
    critere: str = "ips",
    n: int = 5,
    annee: Optional[int] = None,
) -> List[dict]:
    """
    Retourne le top N des academies selon un critere.
    Criteres acceptes : 'ips', 'taux_reussite', 'taux_mention'
    """
    if critere not in ("ips", "taux_reussite", "taux_mention"):
        critere = "ips"

    indicators = get_indicators_by_academie(db, annee=annee)

    # Clef de tri : ips -> ipsmoyen, sinon le champ tel quel
    key = "ipsmoyen" if critere == "ips" else critere

    # Filtrer les academies sans valeur pour le critere
    indicators = [i for i in indicators if i.get(key) is not None]

    # Tri decroissant
    indicators.sort(key=lambda x: x[key], reverse=True)

    return indicators[:n]