"""
Nettoyage des CSV avant insertion en BDD.
Responsabilite : Extract + Transform du pipeline ETL.
"""
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np


# ============================================================
# NETTOYAGE IPS-LYCEES
# ============================================================

def _parse_french_decimal(value):
    """
    Convertit une valeur textuelle francaise ('119,6') en float (119.6).
    Gere les NaN, les chaines vides et les valeurs deja numeriques.
    """
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Valeur texte : enlever guillemets, remplacer virgule par point
    cleaned = str(value).strip().strip('"').replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def clean_ips_data(file_path: Path) -> pd.DataFrame:
    """
    Nettoie le CSV IPS-Lycees :
    - Convertit les virgules decimales FR en points
    - Ne garde que les colonnes utiles
    - Renomme les colonnes pour matcher la BDD
    """
    print(f"[IPS] Lecture de {file_path.name}...")
    df = pd.read_csv(file_path, sep=",", encoding="utf-8")
    print(f"[IPS] {len(df)} lignes chargees")

    # Colonnes qu'on garde (on extrait le strict necessaire)
    cols_mapping = {
        "Nom de l'établissement": "nomlycee",
        "Secteur": "secteur",
        "Type de lycée": "typelycee",
        "Code du département": "departement",
        "IPS de l'établissement": "ips",
        "Académie": "nomacademie",
        "Région académique": "regionacademie",
    }

    df = df[list(cols_mapping.keys())].copy()
    df = df.rename(columns=cols_mapping)

    # Nettoyage des types
    df["nomlycee"] = df["nomlycee"].astype(str).str.strip()
    df["nomacademie"] = df["nomacademie"].astype(str).str.strip().str.upper()
    df["regionacademie"] = df["regionacademie"].astype(str).str.strip().str.upper()
    df["departement"] = df["departement"].astype(str).str.strip()
    df["ips"] = df["ips"].apply(_parse_french_decimal)

    # On supprime les lignes sans IPS (inutilisables pour les analyses)
    df = df.dropna(subset=["ips"])
    print(f"[IPS] {len(df)} lignes apres suppression des IPS manquants")

    # Doublons exacts
    before = len(df)
    df = df.drop_duplicates()
    print(f"[IPS] {before - len(df)} doublons supprimes")

    return df


# ============================================================
# NETTOYAGE RESULTATS BAC
# ============================================================

def clean_bac_data(file_path: Path) -> pd.DataFrame:
    """
    Nettoie et agrege le CSV des resultats du bac :
    - Mappe Sexe FEMININ/MASCULIN -> F/M
    - Somme les 2 colonnes de mention TB
    - Agrege par academie + annee + voie + sexe
      (le CSV est par specialite, mais la BDD est par academie)
    """
    print(f"[BAC] Lecture de {file_path.name}...")
    df = pd.read_csv(file_path, sep=";", encoding="utf-8")
    print(f"[BAC] {len(df)} lignes chargees")

    # Mapping sexe (le CSV a plusieurs variantes)
    sexe_map = {
        "FEMININ": "F", "FILLES": "F", "FEMME": "F",
        "MASCULIN": "M", "GARCONS": "M", "HOMME": "M",
    }
    df["sexe"] = df["Sexe"].str.upper().map(sexe_map)

    # Mention TB = somme des 2 colonnes
    col_tb_felic = "Nombre d'admis avec mention TB avec les félicitations du jury"
    col_tb_sans = "Nombre d'admis avec mention TB sans les félicitations du jury"
    df["nbmentiontb"] = df[col_tb_felic].fillna(0) + df[col_tb_sans].fillna(0)

    # Renommage pour matcher la BDD
    df = df.rename(columns={
        "Session": "annee",
        "Voie": "voie",
        "Académie": "nomacademie",
        "Nombre d'inscrits": "nbinscrits",
        "Nombre d'admis totaux": "nbadmis",
        "Nombre d'admis avec mention B": "nbmentionb",
        "Nombre d'admis avec mention AB": "nbmentionab",
        "Nombre de refusés totaux": "nbrefuses",
        "Nombre d'admis sans mention": "nbadmissansmention",
    })

    # Nettoyage des noms d'academie
    df["nomacademie"] = df["nomacademie"].astype(str).str.strip().str.upper()

    # Agregation : on somme tout par academie + annee + voie + sexe
    group_cols = ["annee", "voie", "sexe", "nomacademie"]
    sum_cols = ["nbinscrits", "nbadmis", "nbmentiontb", "nbmentionb",
                "nbmentionab", "nbrefuses", "nbadmissansmention"]

    # Remplacer NaN par 0 pour l'agregation
    df[sum_cols] = df[sum_cols].fillna(0).astype(int)

    df_agg = df.groupby(group_cols)[sum_cols].sum().reset_index()

    # Type correct pour l'annee
    df_agg["annee"] = df_agg["annee"].astype(int)

    # On supprime les lignes avec sexe manquant (= ligne inexploitable)
    df_agg = df_agg.dropna(subset=["sexe"])

    print(f"[BAC] {len(df_agg)} lignes apres agregation")
    return df_agg


# ============================================================
# ACADEMIES UNIQUES (a inserer avant tout le reste)
# ============================================================

def extract_academies(ips_df: pd.DataFrame, bac_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait la liste unique des academies a partir des 2 DataFrames.
    On prend l'IPS du fichier IPS-Lycees comme source principale.
    """
    # On recupere nom + region depuis le fichier IPS
    ips_acad = ips_df[["nomacademie", "regionacademie"]].drop_duplicates()

    # Calcul de l'IPS moyen par academie
    ips_moyens = ips_df.groupby("nomacademie")["ips"].mean().round(2).reset_index()
    ips_moyens = ips_moyens.rename(columns={"ips": "ipsmoyen"})

    # Merge nom + region + IPS moyen
    academies = ips_acad.merge(ips_moyens, on="nomacademie", how="left")

    # On ajoute les academies qui ne sont QUE dans le fichier bac
    bac_academies = set(bac_df["nomacademie"].unique())
    ips_academies = set(academies["nomacademie"].unique())
    missing = bac_academies - ips_academies

    if missing:
        extra_df = pd.DataFrame({
            "nomacademie": list(missing),
            "regionacademie": [None] * len(missing),
            "ipsmoyen": [None] * len(missing),
        })
        academies = pd.concat([academies, extra_df], ignore_index=True)

    print(f"[ACAD] {len(academies)} academies uniques extraites")
    return academies