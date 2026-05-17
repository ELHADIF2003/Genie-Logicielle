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
    Calcule les KPI nationaux enrichis :
    - Taux de reussite = admis / inscrits
    - Taux de mention = (TB+B+AB) / admis
    - Taux d'echec = refuses / inscrits
    - Ecart F/G = taux_reussite_F - taux_reussite_G
    - IPS moyen + ecart-type (mesure d'inegalites)
    - Nb academies, nb lycees
    """
    if annee is None:
        annee = get_latest_year(db)

    # === Stats globales bac (tous sexes) ===
    totals = db.query(
        func.sum(ResultatBac.nbinscrits).label("total_inscrits"),
        func.sum(ResultatBac.nbadmis).label("total_admis"),
        func.sum(ResultatBac.nbrefuses).label("total_refuses"),
        func.sum(
            ResultatBac.nbmentiontb + ResultatBac.nbmentionb + ResultatBac.nbmentionab
        ).label("total_mentions"),
    ).filter(ResultatBac.annee == annee).first()

    total_inscrits = int(totals.total_inscrits or 0)
    total_admis = int(totals.total_admis or 0)
    total_refuses = int(totals.total_refuses or 0)
    total_mentions = int(totals.total_mentions or 0)

    taux_reussite = (total_admis / total_inscrits * 100) if total_inscrits > 0 else 0.0
    taux_mention = (total_mentions / total_admis * 100) if total_admis > 0 else 0.0
    taux_echec = (total_refuses / total_inscrits * 100) if total_inscrits > 0 else 0.0

    # === Stats par sexe (pour ecart F/G) ===
    stats_par_sexe = db.query(
        ResultatBac.sexe,
        func.sum(ResultatBac.nbinscrits).label("inscrits"),
        func.sum(ResultatBac.nbadmis).label("admis"),
    ).filter(
        ResultatBac.annee == annee,
        ResultatBac.sexe.in_(["F", "M"]),
    ).group_by(ResultatBac.sexe).all()

    taux_f = None
    taux_m = None
    for row in stats_par_sexe:
        inscrits = int(row.inscrits or 0)
        admis = int(row.admis or 0)
        if inscrits > 0:
            taux = round(admis / inscrits * 100, 2)
            if row.sexe == "F":
                taux_f = taux
            elif row.sexe == "M":
                taux_m = taux

    ecart_fg = None
    if taux_f is not None and taux_m is not None:
        ecart_fg = round(taux_f - taux_m, 2)

    # === IPS : moyenne et ecart-type (mesure d'inegalites) ===
    # stddev_pop : ecart-type sur l'ensemble de la population (pas un echantillon)
    ips_stats = db.query(
        func.avg(Lycee.ips).label("moyenne"),
        func.stddev_pop(Lycee.ips).label("ecart_type"),
    ).filter(Lycee.ips.isnot(None)).first()

    ips_moyen = float(ips_stats.moyenne) if ips_stats.moyenne else 0.0
    ips_ecart_type = float(ips_stats.ecart_type) if ips_stats.ecart_type else 0.0

    # === Comptes globaux ===
    nb_academies = db.query(func.count(Academie.idacademie)).scalar() or 0
    nb_lycees = db.query(func.count(Lycee.idlycee)).scalar() or 0

    return {
        "annee": annee,
        # Indicateurs de réussite
        "taux_reussite_national": round(taux_reussite, 2),
        "taux_mention_national": round(taux_mention, 2),
        "taux_echec_national": round(taux_echec, 2),
        # Indicateur de parité
        "taux_reussite_filles": taux_f,
        "taux_reussite_garcons": taux_m,
        "ecart_filles_garcons": ecart_fg,
        # Indicateurs sociaux (IPS)
        "ips_moyen_national": round(ips_moyen, 2),
        "ips_ecart_type": round(ips_ecart_type, 2),
        # Comptes
        "nb_academies": nb_academies,
        "nb_lycees": nb_lycees,
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

# ============================================================
# AGRÉGATIONS PAR RÉGION ACADÉMIQUE
# ============================================================

def get_indicators_by_region(
    db: Session,
    annee: Optional[int] = None,
) -> List[dict]:
    """
    Agrege les indicateurs par region academique.
    Une region = plusieurs academies.
    """
    if annee is None:
        annee = get_latest_year(db)

    # On veut : pour chaque region, somme des inscrits/admis/mentions + moyenne IPS
    query = (
        db.query(
            Academie.regionacademie,
            func.avg(Academie.ipsmoyen).label("ips_moyen"),
            func.sum(ResultatBac.nbinscrits).label("nb_inscrits"),
            func.sum(ResultatBac.nbadmis).label("nb_admis"),
            func.sum(
                ResultatBac.nbmentiontb + ResultatBac.nbmentionb + ResultatBac.nbmentionab
            ).label("nb_mentions"),
        )
        .outerjoin(ResultatBac, (ResultatBac.idacademie == Academie.idacademie)
                                & (ResultatBac.annee == annee))
        .filter(Academie.regionacademie.isnot(None))
        .group_by(Academie.regionacademie)
        .order_by(Academie.regionacademie)
    )

    results = []
    for row in query.all():
        nb_inscrits = int(row.nb_inscrits or 0)
        nb_admis = int(row.nb_admis or 0)
        nb_mentions = int(row.nb_mentions or 0)

        taux_reussite = (nb_admis / nb_inscrits * 100) if nb_inscrits > 0 else None
        taux_mention = (nb_mentions / nb_admis * 100) if nb_admis > 0 else None

        results.append({
            "regionacademie": row.regionacademie,
            "ipsmoyen": float(row.ips_moyen) if row.ips_moyen else None,
            "taux_reussite": round(taux_reussite, 2) if taux_reussite is not None else None,
            "taux_mention": round(taux_mention, 2) if taux_mention is not None else None,
            "nb_admis": nb_admis,
            "nb_inscrits": nb_inscrits,
            "annee": annee,
        })

    return results


def get_correlation_points_regions(db: Session, annee: Optional[int] = None) -> List[dict]:
    """Points (ips, taux_reussite) par region pour scatter plot."""
    regions = get_indicators_by_region(db, annee=annee)
    points = []
    for r in regions:
        if r["ipsmoyen"] is not None and r["taux_reussite"] is not None:
            points.append({
                "regionacademie": r["regionacademie"],
                "ips": r["ipsmoyen"],
                "taux_reussite": r["taux_reussite"],
            })
    return points


def get_top_regions(
    db: Session,
    critere: str = "ips",
    n: int = 5,
    annee: Optional[int] = None,
) -> List[dict]:
    """Top N regions selon un critere."""
    if critere not in ("ips", "taux_reussite", "taux_mention"):
        critere = "ips"

    regions = get_indicators_by_region(db, annee=annee)
    key = "ipsmoyen" if critere == "ips" else critere
    regions = [r for r in regions if r.get(key) is not None]
    regions.sort(key=lambda x: x[key], reverse=True)

    return regions[:n]