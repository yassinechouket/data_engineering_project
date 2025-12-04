-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE Proprietaire (
    id_proprietaire SERIAL PRIMARY KEY,
    nom_proprietaire VARCHAR(100) NOT NULL,
    type_proprietaire VARCHAR(20) NOT NULL CHECK (type_proprietaire IN ('municipalité', 'partenaire privé')),
    adresse VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT chk_prop_email CHECK (email LIKE '%@%')
);


CREATE TABLE Type (
    id_type SERIAL PRIMARY KEY,
    nom_type VARCHAR(100) NOT NULL
);


CREATE TABLE Capteur (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    localisation VARCHAR(300) NOT NULL,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('actif', 'maintenance', 'hors_service')),
    date_installation DATE NOT NULL,
    id_proprietaire INTEGER NOT NULL,
    id_type INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_proprietaire) REFERENCES Proprietaire(id_proprietaire),
    FOREIGN KEY (id_type) REFERENCES Type(id_type)
);


CREATE TABLE Technicien (
    id_tech VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20)
);


CREATE TABLE Intervention (
    id_intervention SERIAL PRIMARY KEY,
    uuid_capteur UUID NOT NULL,
    date_heure_intervention TIMESTAMP NOT NULL,
    nature VARCHAR(20) NOT NULL CHECK(nature IN ('predictive', 'corrective', 'curative')),
    duree_minutes INTEGER NOT NULL CHECK (duree_minutes > 0),
    cout DECIMAL(10,2) NOT NULL CHECK (cout >= 0),
    impact_CO2_reduit_kg DECIMAL(8,2) CHECK (impact_CO2_reduit_kg >= 0),
    FOREIGN KEY (uuid_capteur) REFERENCES Capteur(uuid) ON DELETE CASCADE
);


CREATE TABLE Intervention_Technicien (
    id_intervention INTEGER NOT NULL,
    id_technicien VARCHAR(50) NOT NULL,
    role_technicien VARCHAR(20) NOT NULL CHECK(role_technicien IN ('intervenant', 'validateur')),
    PRIMARY KEY (id_intervention, id_technicien),
    FOREIGN KEY (id_intervention) REFERENCES Intervention(id_intervention) ON DELETE CASCADE,
    FOREIGN KEY (id_technicien) REFERENCES Technicien(id_tech) ON DELETE RESTRICT
);


CREATE TABLE Citoyen (
    id_citoyen SERIAL PRIMARY KEY,
    nom_citoyen VARCHAR(100) NOT NULL,
    prenom_citoyen VARCHAR(100) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    score_engagement_ecologique INTEGER DEFAULT 0 CHECK (score_engagement_ecologique >= 0),
    preferences_mobilite TEXT,
    historique_participation TEXT,
    CONSTRAINT chk_citoyen_email CHECK (email LIKE '%@%')
);


CREATE TABLE Consultation_Citoyenne (
    id_consultation SERIAL PRIMARY KEY,
    titre_consultation VARCHAR(255) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    theme VARCHAR(100),
    CONSTRAINT chk_dates_consultation CHECK (date_fin >= date_debut)
);


CREATE TABLE Participation_Citoyenne (
    id_citoyen INTEGER NOT NULL,
    id_consultation INTEGER NOT NULL,
    date_participation TIMESTAMP NOT NULL,
    avis TEXT,
    vote VARCHAR(20) CHECK (vote IN ('pour','contre','abstention','neutre')),
    PRIMARY KEY (id_citoyen, id_consultation),
    FOREIGN KEY (id_citoyen) REFERENCES Citoyen(id_citoyen) ON DELETE CASCADE,
    FOREIGN KEY (id_consultation) REFERENCES Consultation_Citoyenne(id_consultation) ON DELETE CASCADE
);


CREATE TABLE Vehicule_Autonome (
    plaque_immatriculation VARCHAR(20) PRIMARY KEY,
    type_vehicule VARCHAR(50) NOT NULL,
    energie_utilisee VARCHAR(30) NOT NULL CHECK(energie_utilisee IN ('électrique', 'hybride', 'hydrogène', 'autre'))
);


CREATE TABLE Trajet (
    id_trajet SERIAL PRIMARY KEY,
    plaque_immatriculation VARCHAR(20) NOT NULL,
    origine VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    date_heure_depart TIMESTAMP NOT NULL,
    duree_minutes INTEGER NOT NULL CHECK(duree_minutes > 0),
    economie_co2_kg DECIMAL(10,2) CHECK (economie_co2_kg >= 0),
    FOREIGN KEY(plaque_immatriculation) REFERENCES Vehicule_Autonome(plaque_immatriculation) ON DELETE CASCADE
);


CREATE TABLE Mesure (
    id_mesure SERIAL PRIMARY KEY,
    uuid_capteur UUID NOT NULL,
    date_heure_mesure TIMESTAMP NOT NULL,
    valeur_mesuree DECIMAL(15,4) NOT NULL,
    unite_mesure VARCHAR(20) NOT NULL,
    qualite VARCHAR(20) CHECK(qualite IN ('bonne','moyenne','mauvaise','critique')),
    FOREIGN KEY (uuid_capteur) REFERENCES Capteur(uuid) ON DELETE CASCADE
);


CREATE TABLE Validation_IA (
    id_validation SERIAL PRIMARY KEY,
    id_intervention INTEGER NOT NULL UNIQUE,
    date_heure_validation TIMESTAMP NOT NULL,
    score_validation DECIMAL(5,2) CHECK(score_validation BETWEEN 0 AND 100),
    statut_validation VARCHAR(20) NOT NULL CHECK(statut_validation IN ('validée','rejetée','en attente')),
    commentaire_ia TEXT,
    FOREIGN KEY (id_intervention) REFERENCES Intervention(id_intervention) ON DELETE CASCADE
);
