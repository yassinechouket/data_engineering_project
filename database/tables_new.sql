-- Create Arrondissement table
CREATE TABLE Arrondissement (
    id_arrondissement SERIAL PRIMARY KEY,
    nom_arrondissement VARCHAR(100) NOT NULL,
    superficie_km2 DECIMAL(10,2),
    population INTEGER
);

-- Create Proprietaire table
CREATE TABLE Proprietaire (
    id_proprietaire SERIAL PRIMARY KEY,
    nom_proprietaire VARCHAR(100) NOT NULL,
    type_proprietaire VARCHAR(50),
    adresse VARCHAR(255),
    telephone VARCHAR(20),
    email VARCHAR(100)
);

-- Create Capteur table (with UUID)
CREATE TABLE Capteur (
    id_capteur UUID PRIMARY KEY,
    type_capteur VARCHAR(100),
    localisation_geographique VARCHAR(255),
    statut VARCHAR(50),
    id_proprietaire INTEGER,
    id_arrondissement INTEGER,
    date_installation DATE,
    FOREIGN KEY (id_proprietaire) REFERENCES Proprietaire(id_proprietaire),
    FOREIGN KEY (id_arrondissement) REFERENCES Arrondissement(id_arrondissement)
);

-- Create Mesure table
CREATE TABLE Mesure (
    id_mesure SERIAL PRIMARY KEY,
    id_capteur UUID NOT NULL,
    date_heure_mesure TIMESTAMP,
    valeur_mesuree DECIMAL(15,4),
    unite_mesure VARCHAR(20),
    qualite VARCHAR(20),
    FOREIGN KEY (id_capteur) REFERENCES Capteur(id_capteur)
);

-- Create Technicien table
CREATE TABLE Technicien (
    id_technicien SERIAL PRIMARY KEY,
    nom_technicien VARCHAR(100),
    prenom_technicien VARCHAR(100),
    certification VARCHAR(100),
    telephone VARCHAR(20),
    email VARCHAR(100),
    date_certification DATE
);

-- Create Intervention table
CREATE TABLE Intervention (
    id_intervention SERIAL PRIMARY KEY,
    id_capteur UUID NOT NULL,
    date_heure_intervention TIMESTAMP,
    nature_intervention VARCHAR(50),
    duree_minutes INTEGER,
    cout_euros DECIMAL(10,2),
    impact_environnemental_co2_kg DECIMAL(10,2),
    FOREIGN KEY (id_capteur) REFERENCES Capteur(id_capteur)
);

-- Create Validation_IA table
CREATE TABLE Validation_IA (
    id_validation SERIAL PRIMARY KEY,
    id_intervention INTEGER NOT NULL,
    date_heure_validation TIMESTAMP,
    score_validation DECIMAL(5,2),
    statut_validation VARCHAR(50),
    commentaire_ia TEXT,
    FOREIGN KEY (id_intervention) REFERENCES Intervention(id_intervention)
);

-- Create Intervention_Technicien table
CREATE TABLE Intervention_Technicien (
    id_intervention INTEGER NOT NULL,
    id_technicien INTEGER NOT NULL,
    role_technicien VARCHAR(50),
    PRIMARY KEY (id_intervention, id_technicien),
    FOREIGN KEY (id_intervention) REFERENCES Intervention(id_intervention),
    FOREIGN KEY (id_technicien) REFERENCES Technicien(id_technicien)
);

-- Create Citoyen table
CREATE TABLE Citoyen (
    id_citoyen SERIAL PRIMARY KEY,
    nom_citoyen VARCHAR(100),
    prenom_citoyen VARCHAR(100),
    adresse VARCHAR(255),
    telephone VARCHAR(20),
    email VARCHAR(100),
    score_engagement_ecologique INTEGER,
    preferences_mobilite TEXT
);

-- Create Consultation_Citoyenne table
CREATE TABLE Consultation_Citoyenne (
    id_consultation SERIAL PRIMARY KEY,
    titre_consultation VARCHAR(255),
    description TEXT,
    date_debut DATE,
    date_fin DATE,
    theme VARCHAR(100)
);

-- Create Participation_Citoyenne table
CREATE TABLE Participation_Citoyenne (
    id_citoyen INTEGER NOT NULL,
    id_consultation INTEGER NOT NULL,
    date_participation TIMESTAMP,
    avis TEXT,
    vote VARCHAR(20),
    PRIMARY KEY (id_citoyen, id_consultation),
    FOREIGN KEY (id_citoyen) REFERENCES Citoyen(id_citoyen),
    FOREIGN KEY (id_consultation) REFERENCES Consultation_Citoyenne(id_consultation)
);

-- Create Vehicule_Autonome table
CREATE TABLE Vehicule_Autonome (
    plaque_immatriculation VARCHAR(20) PRIMARY KEY,
    type_vehicule VARCHAR(50),
    energie_utilisee VARCHAR(50)
);

-- Create Trajet table
CREATE TABLE Trajet (
    id_trajet SERIAL PRIMARY KEY,
    plaque_immatriculation VARCHAR(20),
    origine VARCHAR(255),
    destination VARCHAR(255),
    date_heure_depart TIMESTAMP,
    duree_minutes INTEGER,
    economie_co2_kg DECIMAL(10,2),
    FOREIGN KEY (plaque_immatriculation) REFERENCES Vehicule_Autonome(plaque_immatriculation)
);
