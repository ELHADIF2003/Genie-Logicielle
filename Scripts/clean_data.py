import pandas as pd
import numpy as np

def clean_ips_data(file_path):
    """Nettoie le fichier IPS-Lycees.csv"""
    print(f"Nettoyage de {file_path}...")
    
    # Lecture du fichier (vérifie le séparateur, ici ',' par défaut pour ton fichier)
    df = pd.read_csv(file_path, sep=',')
    
    # Nettoyage de la colonne IPS (remplacer virgule par point et convertir en float)
    if df['IPS de l\'établissement'].dtype == 'object':
        df['IPS de l\'établissement'] = df['IPS de l\'établissement'].str.replace(',', '.').astype(float)
    
    # Sélection des colonnes utiles pour la table Lycee
    lycee_df = df[[
        "Nom de l'établissement", "Secteur", "Type de lycée", 
        "Code du département", "IPS de l'établissement", "Académie", "Région académique"
    ]].copy()
    
    lycee_df.columns = ['nomLycee', 'secteur', 'typeLycee', 'departement', 'ips', 'nomAcademie', 'regionAcademie']
    
    return lycee_df

def clean_bac_data(file_path):
    """Nettoie et agrège le fichier Résultat-Bac-Par-Academie.csv"""
    print(f"Nettoyage de {file_path}...")
    
    # Lecture avec le séparateur ';'
    df = pd.read_csv(file_path, sep=';')
    
    # Mapping du sexe vers VARCHAR(1)
    sexe_map = {
        'FEMININ': 'F', 'FILLES': 'F',
        'MASCULIN': 'M', 'GARCONS': 'M'
    }
    df['sexe'] = df['Sexe'].map(sexe_map)
    
    # Calcul de la mention TB (somme des deux colonnes du CSV)
    df['nbMentionTB'] = (
        df["Nombre d'admis avec mention TB avec les félicitations du jury"].fillna(0) + 
        df["Nombre d'admis avec mention TB sans les félicitations du jury"].fillna(0)
    )
    
    # Renommage pour correspondre à la BDD
    df_mapped = df.rename(columns={
        'Session': 'annee',
        'Voie': 'voie',
        'Nombre d\'inscrits': 'nbInscrits',
        'Nombre d\'admis totaux': 'nbAdmis',
        'Nombre d\'admis avec mention B': 'nbMentionB',
        'Nombre d\'admis avec mention AB': 'nbMentionAB',
        'Nombre de refusés totaux': 'nbRefuses',
        'Nombre d\'admis sans mention': 'nbAdmisSansMention',
        'Académie': 'nomAcademie'
    })
    
    # Agrégation des données (car le CSV est par spécialité, mais ta BDD est par académie/voie/annee)
    group_cols = ['annee', 'voie', 'sexe', 'nomAcademie']
    sum_cols = ['nbInscrits', 'nbAdmis', 'nbMentionTB', 'nbMentionB', 'nbMentionAB', 'nbRefuses', 'nbAdmisSansMention']
    
    bac_aggregated = df_mapped.groupby(group_cols)[sum_cols].sum().reset_index()
    
    return bac_aggregated

if __name__ == "__main__":
    # Test rapide des fonctions
    try:
        ips_cleaned = clean_ips_data('data/IPS-Lycees.csv')
        bac_cleaned = clean_bac_data('data/Résultat-Bac-Par-Academie.csv')
        
        print("\n--- Aperçu IPS ---")
        print(ips_cleaned.head())
        
        print("\n--- Aperçu Bac ---")
        print(bac_cleaned.head())
        
        print("\nSuccès : Les données sont prêtes pour l'insertion.")
    except Exception as e:
        print(f"Erreur lors du nettoyage : {e}")