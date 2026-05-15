"""
Insertion des donnees nettoyees en BDD.
Responsabilite : Load du pipeline ETL.
"""
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Academie, Dataset, Lycee, ResultatBac


# ============================================================
# IMPORT DES ACADEMIES
# ============================================================

def import_academies(db: Session, academies_df: pd.DataFrame) -> dict:
    """
    Insere les academies et retourne un dict {nomacademie: idacademie}
    (utile pour mapper les FK par la suite).
    """
    print(f"[IMPORT] Insertion de {len(academies_df)} academies...")

    name_to_id = {}
    for _, row in academies_df.iterrows():
        # Verifier si l'academie existe deja (pour ne pas dupliquer)
        existing = db.query(Academie).filter(
            Academie.nomacademie == row["nomacademie"]
        ).first()

        if existing:
            name_to_id[row["nomacademie"]] = existing.idacademie
            continue

        acad = Academie(
            nomacademie=row["nomacademie"],
            regionacademie=row["regionacademie"] if pd.notna(row["regionacademie"]) else None,
            ipsmoyen=float(row["ipsmoyen"]) if pd.notna(row["ipsmoyen"]) else None,
        )
        db.add(acad)
        db.flush()  # force l'attribution de l'ID sans committer
        name_to_id[row["nomacademie"]] = acad.idacademie

    db.commit()
    print(f"[IMPORT] {len(name_to_id)} academies presentes en BDD")
    return name_to_id


# ============================================================
# IMPORT DES DATASETS
# ============================================================

def create_dataset(db: Session, nom: str, source: str) -> int:
    """Cree une entree Dataset et retourne son ID."""
    ds = Dataset(
        nomdataset=nom,
        source=source,
        etat="valide",
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    print(f"[IMPORT] Dataset cree : '{nom}' (id={ds.iddataset})")
    return ds.iddataset


# ============================================================
# IMPORT DES LYCEES
# ============================================================

def import_lycees(
    db: Session,
    lycees_df: pd.DataFrame,
    acad_name_to_id: dict,
    dataset_id: int,
) -> int:
    """
    Insere les lycees avec leur FK vers academie et dataset.
    Utilise bulk_insert_mappings pour aller vite (30k+ lignes).
    """
    print(f"[IMPORT] Preparation de {len(lycees_df)} lycees...")

    records = []
    for _, row in lycees_df.iterrows():
        acad_id = acad_name_to_id.get(row["nomacademie"])
        if acad_id is None:
            continue  # academie introuvable, on skip cette ligne

        records.append({
            "nomlycee": row["nomlycee"][:255],  # tronque si trop long
            "secteur": row["secteur"][:50] if pd.notna(row["secteur"]) else None,
            "typelycee": row["typelycee"][:100] if pd.notna(row["typelycee"]) else None,
            "departement": row["departement"][:5] if pd.notna(row["departement"]) else None,
            "ips": float(row["ips"]) if pd.notna(row["ips"]) else None,
            "idacademie": acad_id,
            "iddataset": dataset_id,
        })

    # Insertion en masse : bien plus rapide qu'un add() par ligne
    db.bulk_insert_mappings(Lycee, records)
    db.commit()
    print(f"[IMPORT] {len(records)} lycees inseres")
    return len(records)


# ============================================================
# IMPORT DES RESULTATS BAC
# ============================================================

def import_resultats_bac(
    db: Session,
    bac_df: pd.DataFrame,
    acad_name_to_id: dict,
) -> int:
    """
    Insere les resultats du bac (deja agreges par acad/annee/voie/sexe).
    """
    print(f"[IMPORT] Preparation de {len(bac_df)} resultats bac...")

    records = []
    for _, row in bac_df.iterrows():
        acad_id = acad_name_to_id.get(row["nomacademie"])
        if acad_id is None:
            continue

        records.append({
            "annee": int(row["annee"]),
            "voie": row["voie"][:50] if pd.notna(row["voie"]) else None,
            "nbinscrits": int(row["nbinscrits"]),
            "nbadmis": int(row["nbadmis"]),
            "nbmentiontb": int(row["nbmentiontb"]),
            "nbmentionb": int(row["nbmentionb"]),
            "nbmentionab": int(row["nbmentionab"]),
            "nbrefuses": int(row["nbrefuses"]),
            "sexe": row["sexe"][:1],
            "nbadmissansmention": int(row["nbadmissansmention"]),
            "idacademie": acad_id,
        })

    db.bulk_insert_mappings(ResultatBac, records)
    db.commit()
    print(f"[IMPORT] {len(records)} resultats bac inseres")
    return len(records)