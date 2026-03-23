CREATE TABLE Academie (
    idAcademie SERIAL PRIMARY KEY,
    nomAcademie VARCHAR(100),
    regionAcademie VARCHAR(100),
    ipsMoyen DECIMAL(5,2)
);

CREATE TABLE Dataset (
    idDataset SERIAL PRIMARY KEY,
    nomDataset VARCHAR(255),
    source VARCHAR(255),
    dateImportation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etat VARCHAR(50)
);

CREATE TABLE Lycee (
    idLycee SERIAL PRIMARY KEY,
    nomLycee VARCHAR(255),
    secteur VARCHAR(50),
    typeLycee VARCHAR(100),
    departement VARCHAR(5),
    ips DECIMAL(5,2),
    idAcademie INT REFERENCES Academie(idAcademie),
    idDataset INT REFERENCES Dataset(idDataset)
);

CREATE TABLE ResultatBac (
    idResultat SERIAL PRIMARY KEY,
    annee INT,
    voie VARCHAR(50),
    nbInscrits INT,
    nbAdmis INT,
    nbMentionTB INT,
    nbMentionB INT,
    nbMentionAB INT,
    nbRefuses INT,
    sexe VARCHAR(1),
    nbAdmisSansMention INT,
    idAcademie INT REFERENCES Academie(idAcademie)
);

CREATE TABLE Indicateur (
    idIndicateur SERIAL PRIMARY KEY,
    nomIndicateur VARCHAR(100),
    valeurIndicateur DECIMAL(10,2),
    annee INT,
    typeIndicateur VARCHAR(100),
    idLycee INT REFERENCES Lycee(idLycee),
    idAcademie INT REFERENCES Academie(idAcademie),
    idDataset INT REFERENCES Dataset(idDataset)
);

CREATE TABLE Utilisateur (
    idUtilisateur SERIAL PRIMARY KEY,
    nomUtilisateur VARCHAR(100),
    emailUtilisateur VARCHAR(150) UNIQUE,
    role VARCHAR(20) DEFAULT 'utilisateur'
);