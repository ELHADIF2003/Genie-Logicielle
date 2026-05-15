"""
Service d'import pour les endpoints admin.
Wrappe le pipeline ETL existant pour accepter un fichier uploade.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Dataset
from app.services.data_cleaner import (
    clean_ips_data,
    clean_bac_data,
    extract_academies,
)
from app.services.data_importer import (
    import_academies,
    create_dataset,
    import_lycees,
    import_resultats_bac,
)


def detect_file_type(file_path: Path) -> str:
    """
    Detecte si un CSV est un fichier IPS ou bac.
    Retourne 'ips', 'bac' ou 'inconnu'.
    """
    try:
        df = pd.read_csv(file_path, nrows=1, sep=",", encoding="utf-8")
        cols = set(df.columns)
        if "IPS de l'établissement" in cols or "Nom de l'établissement" in cols:
            return "ips"
    except Exception:
        pass

    try:
        df = pd.read_csv(file_path, nrows=1, sep=";", encoding="utf-8")
        cols = set(df.columns)
        if "Session" in cols and "Académie" in cols and "Nombre d'inscrits" in cols:
            return "bac"
    except Exception:
        pass

    return "inconnu"


def import_uploaded_file(
    db: Session,
    file_path: Path,
    nom_dataset: str,
    source: str = "upload_admin",
) -> dict:
    """
    Importe un fichier CSV uploade en BDD.
    Detecte automatiquement le type IPS ou bac.
    """
    file_type = detect_file_type(file_path)
    if file_type == "inconnu":
        raise ValueError(
            "Type de fichier non reconnu. "
            "Doit etre un CSV IPS ou bac."
        )

    nb_lignes_brutes = 0
    nb_lignes_importees = 0
    nb_acad = 0
    nb_lycees = 0
    nb_bac = 0

    try:
        sep = "," if file_type == "ips" else ";"
        raw = pd.read_csv(file_path, sep=sep, encoding="utf-8")
        nb_lignes_brutes = len(raw)
        del raw
    except Exception:
        pass

    if file_type == "ips":
        ips_df = clean_ips_data(file_path)
        empty_bac = pd.DataFrame(columns=["nomacademie"])
        academies_df = extract_academies(ips_df, empty_bac)

        acad_map = import_academies(db, academies_df)
        nb_acad = len(acad_map)

        ds_id = create_dataset(db, nom_dataset, source)
        nb_lycees = import_lycees(db, ips_df, acad_map, ds_id)
        nb_lignes_importees = nb_lycees

    else:
        bac_df = clean_bac_data(file_path)
        empty_ips = pd.DataFrame(columns=["nomacademie", "regionacademie", "ips"])
        academies_df = extract_academies(empty_ips, bac_df)

        acad_map = import_academies(db, academies_df)
        nb_acad = len(acad_map)

        ds_id = create_dataset(db, nom_dataset, source)
        nb_bac = import_resultats_bac(db, bac_df, acad_map)
        nb_lignes_importees = nb_bac

    ds = db.query(Dataset).filter(Dataset.iddataset == ds_id).first()

    return {
        "dataset": ds,
        "type_detecte": file_type,
        "nb_lignes_brutes": nb_lignes_brutes,
        "nb_lignes_importees": nb_lignes_importees,
        "nb_academies": nb_acad,
        "nb_lycees": nb_lycees,
        "nb_resultats_bac": nb_bac,
        "message": f"Import {file_type} termine avec succes",
    }