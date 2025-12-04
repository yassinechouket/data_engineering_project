import csv
import random
from datetime import datetime, timedelta
import uuid

print("=== Smart City Neo-Sousse 2030 - CSV Data Generator ===\n")

# ============================================================================
# 1. ARRONDISSEMENT
# ============================================================================
def generate_arrondissements():
    arrondissements = [
        ('Sousse Médina', 3.2, 45000),
        ('Sousse Riadh', 8.5, 78000),
        ('Sousse Jawhara', 12.3, 95000),
        ('Sousse Sidi Abdelhamid', 6.8, 52000),
        ('Sousse Khezama', 15.7, 68000),
        ('Zone Industrielle', 22.4, 12000),
        ('Corniche Nord', 4.9, 38000),
        ('Port de Commerce', 5.3, 15000)
    ]
    
    with open('arrondissement.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nom_arrondissement', 'superficie_km2', 'population'])
        writer.writerows(arrondissements)
    print("✓ arrondissement.csv created")
    return arrondissements

# ============================================================================
# 2. PROPRIETAIRE
# ============================================================================
def generate_proprietaires():
    proprietaires = [
        ('Municipalité de Sousse', 'municipalité', '1 Avenue de la République, Sousse', '+216 73 224 700', 'contact@sousse.gov.tn'),
        ('STEG Smart Solutions', 'partenaire privé', '38 Rue Kamel Ataturk, Tunis', '+216 71 341 311', 'smart@steg.com.tn'),
        ('Tunisie Telecom IoT', 'partenaire privé', 'Rue 8601, Centre Urbain Nord, Tunis', '+216 71 108 000', 'iot@tt.com.tn'),
        ('Orange Business Services', 'partenaire privé', 'Lac 2, Tunis', '+216 71 856 000', 'business@orange.tn'),
        ('Municipalité - Environnement', 'municipalité', '1 Avenue de la République, Sousse', '+216 73 224 701', 'environnement@sousse.gov.tn')
    ]
    
    with open('proprietaire.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nom_proprietaire', 'type_proprietaire', 'adresse', 'telephone', 'email'])
        writer.writerows(proprietaires)
    print("✓ proprietaire.csv created")
    return proprietaires

# ============================================================================
# 3. CAPTEUR
# ============================================================================
def generate_capteurs(arrondissements, nb_proprietaires):
    types_capteur = ["qualité de l'air", 'trafic', 'énergie', 'déchets', 'éclairage']
    statuts = ['actif', 'en maintenance', 'hors service']
    
    locations = [
        ('Place Farhat Hached', 1),
        ('Port de Sousse', 8),
        ('Avenue Habib Bourguiba', 1),
        ('Médina de Sousse', 1),
        ('Zone Industrielle Sousse', 6),
        ('Stade Olympique', 5),
        ('Corniche de Sousse', 7),
        ('Centre Ville', 2),
        ('Quartier Khezama', 5),
        ('Bab Jdid', 1),
        ('Avenue Léopold Sédar Senghor', 3),
        ('Palais des Congrès', 7),
        ('Avenue Hedi Chaker', 2),
        ('Route de la Corniche', 7),
        ('Quartier Sidi Abdelhamid', 4),
        ('Campus Universitaire', 3),
        ('Hôpital Universitaire', 2),
        ('Marché Central', 1),
        ('Gare Ferroviaire', 2),
        ('Parc El Bousten', 3)
    ]
    
    capteurs = []
    
    for loc, arrond_idx in locations:
        # 2-3 capteurs par localisation
        num_sensors = random.randint(2, 3)
        types_used = random.sample(types_capteur, num_sensors)
        
        for type_cap in types_used:
            uuid_val = str(uuid.uuid4())
            statut = random.choices(statuts, weights=[0.85, 0.10, 0.05])[0]
            id_prop = random.randint(1, nb_proprietaires)
            date_install = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 600))).strftime('%Y-%m-%d')
            
            capteurs.append([uuid_val, type_cap, loc, statut, id_prop, arrond_idx, date_install])
    
    with open('capteur.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_capteur', 'type_capteur', 'localisation_geographique', 'statut', 
                        'id_proprietaire', 'id_arrondissement', 'date_installation'])
        writer.writerows(capteurs)
    print(f"✓ capteur.csv created ({len(capteurs)} capteurs)")
    return capteurs

# ============================================================================
# 4. MESURE
# ============================================================================
def generate_mesures(capteurs):
    mesures = []
    mesure_id = 1
    
    # Générer mesures pour les 7 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Limiter aux 30 premiers capteurs actifs
    capteurs_actifs = [c for c in capteurs if c[3] == 'actif'][:30]
    
    for capteur in capteurs_actifs:
        uuid_capteur = capteur[0]
        type_capteur = capteur[1]
        
        # Générer mesures toutes les 30 minutes
        current = start_date
        while current <= end_date:
            # Valeurs selon le type de capteur
            if type_capteur == "qualité de l'air":
                valeur = round(random.uniform(15, 85), 2)
                unite = 'µg/m³'
                qualite = 'bonne' if valeur < 35 else 'moyenne' if valeur < 55 else 'mauvaise'
            elif type_capteur == 'trafic':
                valeur = round(random.uniform(50, 500), 0)
                unite = 'véhicules/h'
                qualite = None
            elif type_capteur == 'énergie':
                valeur = round(random.uniform(100, 1500), 2)
                unite = 'kWh'
                qualite = None
            elif type_capteur == 'déchets':
                valeur = round(random.uniform(10, 95), 1)
                unite = '%'
                qualite = 'bonne' if valeur < 50 else 'moyenne' if valeur < 80 else 'critique'
            else:  # éclairage
                valeur = round(random.uniform(0, 100), 1)
                unite = '%'
                qualite = None
            
            mesures.append([mesure_id, uuid_capteur, current.strftime('%Y-%m-%d %H:%M:%S'), 
                          valeur, unite, qualite])
            mesure_id += 1
            current += timedelta(minutes=30)
    
    with open('mesure.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_mesure', 'id_capteur', 'date_heure_mesure', 'valeur_mesuree', 
                        'unite_mesure', 'qualite'])
        writer.writerows(mesures)
    print(f"✓ mesure.csv created ({len(mesures)} mesures)")

# ============================================================================
# 5. TECHNICIEN
# ============================================================================
def generate_techniciens():
    techniciens = [
        ('Ben Ahmed', 'Karim', 'Certification IoT Expert Niveau 3', '+216 98 123 456', 
         'karim.benahmed@sousse.tn', '2021-03-15'),
        ('Trabelsi', 'Samira', 'Certification Réseaux et Télécommunications', '+216 22 234 567',
         'samira.trabelsi@sousse.tn', '2020-11-20'),
        ('Jebali', 'Mohamed', 'Certification Maintenance Industrielle Avancée', '+216 55 345 678',
         'mohamed.jebali@sousse.tn', '2022-01-10'),
        ('Gharbi', 'Fatma', 'Certification Électronique et Systèmes Embarqués', '+216 26 456 789',
         'fatma.gharbi@sousse.tn', '2021-07-22'),
        ('Bouazizi', 'Hichem', 'Certification Sécurité IoT et Cybersécurité', '+216 94 567 890',
         'hichem.bouazizi@sousse.tn', '2022-05-18'),
        ('Slimani', 'Nadia', 'Certification Gestion Énergétique', '+216 21 678 901',
         'nadia.slimani@sousse.tn', '2020-09-30'),
        ('Hamdi', 'Youssef', 'Certification Capteurs Environnementaux', '+216 52 789 012',
         'youssef.hamdi@sousse.tn', '2021-12-05'),
        ('Maalej', 'Leila', 'Certification Systèmes Intelligents', '+216 27 890 123',
         'leila.maalej@sousse.tn', '2022-08-14')
    ]
    
    with open('technicien.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nom_technicien', 'prenom_technicien', 'certification', 'telephone', 
                        'email', 'date_certification'])
        writer.writerows(techniciens)
    print("✓ technicien.csv created")
    return techniciens

# ============================================================================
# 6. INTERVENTION
# ============================================================================
def generate_interventions(capteurs, nb_techniciens):
    interventions = []
    intervention_id = 1
    
    # Générer interventions pour les 60 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    # Sélectionner 25 capteurs aléatoires
    capteurs_sample = random.sample(capteurs, min(25, len(capteurs)))
    
    for capteur in capteurs_sample:
        uuid_capteur = capteur[0]
        num_interventions = random.randint(1, 4)
        
        for _ in range(num_interventions):
            date_inter = start_date + timedelta(
                days=random.randint(0, 60), 
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59)
            )
            nature = random.choices(['prédictive', 'corrective', 'curative'], 
                                   weights=[0.5, 0.3, 0.2])[0]
            duree = random.randint(30, 240)
            cout = round(random.uniform(50, 500), 2)
            impact_co2 = round(random.uniform(0, 15), 2) if nature == 'prédictive' else None
            
            interventions.append([intervention_id, uuid_capteur, 
                                date_inter.strftime('%Y-%m-%d %H:%M:%S'),
                                nature, duree, cout, impact_co2])
            intervention_id += 1
    
    with open('intervention.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_intervention', 'id_capteur', 'date_heure_intervention', 
                        'nature_intervention', 'duree_minutes', 'cout_euros', 
                        'impact_environnemental_co2_kg'])
        writer.writerows(interventions)
    print(f"✓ intervention.csv created ({len(interventions)} interventions)")
    return interventions

# ============================================================================
# 7. VALIDATION_IA
# ============================================================================
def generate_validations_ia(interventions):
    validations = []
    
    for inter in interventions:
        id_inter = inter[0]
        date_inter = datetime.strptime(inter[2], '%Y-%m-%d %H:%M:%S')
        date_valid = date_inter + timedelta(hours=random.randint(1, 24))
        score = round(random.uniform(75, 100), 2)
        statut = random.choices(['validée', 'rejetée', 'en attente'], 
                               weights=[0.90, 0.05, 0.05])[0]
        
        commentaires = {
            'validée': 'Intervention conforme aux standards de qualité',
            'rejetée': 'Intervention nécessite une révision des procédures',
            'en attente': 'En cours d\'analyse par le système IA'
        }
        
        validations.append([id_inter, date_valid.strftime('%Y-%m-%d %H:%M:%S'), 
                          score, statut, commentaires[statut]])
    
    with open('validation_ia.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_intervention', 'date_heure_validation', 'score_validation', 
                        'statut_validation', 'commentaire_ia'])
        writer.writerows(validations)
    print(f"✓ validation_ia.csv created ({len(validations)} validations)")

# ============================================================================
# 8. INTERVENTION_TECHNICIEN
# ============================================================================
def generate_intervention_technicien(interventions, nb_techniciens):
    participe = []
    
    for inter in interventions:
        id_inter = inter[0]
        
        # Sélectionner 2 techniciens différents
        tech_sample = random.sample(range(1, nb_techniciens + 1), 2)
        
        # Un intervenant et un validateur
        participe.append([id_inter, tech_sample[0], 'intervenant'])
        participe.append([id_inter, tech_sample[1], 'validateur'])
    
    with open('intervention_technicien.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_intervention', 'id_technicien', 'role_technicien'])
        writer.writerows(participe)
    print(f"✓ intervention_technicien.csv created ({len(participe)} participations)")

# ============================================================================
# 9. CITOYEN
# ============================================================================
def generate_citoyens():
    prenom_hommes = ['Mohamed', 'Ahmed', 'Ali', 'Karim', 'Mehdi', 'Youssef', 'Hichem', 
                     'Samir', 'Rami', 'Fares', 'Tarek', 'Nabil']
    prenom_femmes = ['Fatma', 'Samira', 'Leila', 'Nadia', 'Amira', 'Sirine', 'Ines', 
                     'Marwa', 'Sonia', 'Rim', 'Olfa', 'Hana']
    noms = ['Ben Ahmed', 'Trabelsi', 'Jebali', 'Gharbi', 'Bouazizi', 'Slimani', 'Hamdi', 
            'Maalej', 'Sassi', 'Rezgui', 'Chaabane', 'Dhaoui', 'Ferchichi', 'Karoui', 'Mejri']
    
    rues = ['Avenue Habib Bourguiba', 'Rue de la République', 'Avenue Hedi Chaker', 
            'Rue du 2 Mars', 'Avenue Léopold Senghor', 'Rue Tahar Sfar', 
            'Avenue de la Corniche', 'Rue Amilcar', 'Boulevard du 7 Novembre']
    
    preferences = [
        'vélo, transport en commun',
        'marche, vélo',
        'transport en commun uniquement',
        'voiture électrique, vélo',
        'trottinette électrique, bus',
        'covoiturage, transport en commun',
        'marche, transport en commun',
        'vélo électrique, métro'
    ]
    
    citoyens = []
    for i in range(1, 51):
        prenom = random.choice(prenom_hommes + prenom_femmes)
        nom = random.choice(noms)
        adresse = f"{random.randint(1, 150)} {random.choice(rues)}, Sousse"
        telephone = f"+216 {random.randint(20, 99)} {random.randint(100, 999)} {random.randint(100, 999)}"
        email = f"{prenom.lower()}.{nom.lower().replace(' ', '')}@email.tn"
        score = random.randint(50, 300)
        pref = random.choice(preferences)
        
        citoyens.append([nom, prenom, adresse, telephone, email, score, pref])
    
    with open('citoyen.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nom_citoyen', 'prenom_citoyen', 'adresse', 'telephone', 'email', 
                        'score_engagement_ecologique', 'preferences_mobilite'])
        writer.writerows(citoyens)
    print(f"✓ citoyen.csv created ({len(citoyens)} citoyens)")
    return citoyens

# ============================================================================
# 10. CONSULTATION_CITOYENNE
# ============================================================================
def generate_consultations():
    consultations = [
        ('Plan Climat Neo-Sousse 2030', 
         'Consultation publique sur les actions climatiques prioritaires pour la décennie',
         '2024-01-15', '2024-02-15', 'Environnement'),
        ('Mobilité Douce et Pistes Cyclables', 
         'Développement du réseau de pistes cyclables et zones piétonnes',
         '2024-03-01', '2024-03-31', 'Mobilité'),
        ('Gestion Intelligente des Déchets', 
         'Optimisation du tri sélectif et de la collecte des déchets',
         '2024-04-10', '2024-05-10', 'Environnement'),
        ('Éclairage Public LED', 
         'Passage aux LED et horaires intelligents pour économie énergie',
         '2024-06-01', '2024-06-30', 'Énergie'),
        ('Qualité de l\'Air et Santé', 
         'Mesures pour réduire la pollution atmosphérique urbaine',
         '2024-08-15', '2024-09-15', 'Santé'),
        ('Extension des Espaces Verts', 
         'Création de nouveaux parcs et jardins publics',
         '2024-10-01', '2024-10-31', 'Urbanisme'),
        ('Transport en Commun Autonome',
         'Développement de la flotte de véhicules autonomes',
         '2024-11-01', '2024-11-30', 'Mobilité')
    ]
    
    with open('consultation_citoyenne.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['titre_consultation', 'description', 'date_debut', 'date_fin', 'theme'])
        writer.writerows(consultations)
    print("✓ consultation_citoyenne.csv created")
    return consultations

# ============================================================================
# 11. PARTICIPATION_CITOYENNE
# ============================================================================
def generate_participations(consultations, nb_citoyens):
    participations = []
    votes = ['pour', 'contre', 'abstention', 'neutre']
    
    avis_exemples = [
        'Excellente initiative pour notre ville',
        'Je soutiens pleinement ce projet',
        'Quelques réserves sur la mise en œuvre',
        'Nécessite plus de concertation',
        'Très bonne idée, à développer davantage',
        'Important pour notre avenir écologique'
    ]
    
    for idx, consult in enumerate(consultations, 1):
        date_debut = datetime.strptime(consult[2], '%Y-%m-%d')
        date_fin = datetime.strptime(consult[3], '%Y-%m-%d')
        
        # 30-60% des citoyens participent
        num_participants = random.randint(int(nb_citoyens * 0.3), int(nb_citoyens * 0.6))
        participants = random.sample(range(1, nb_citoyens + 1), num_participants)
        
        for id_citoyen in participants:
            date_part = date_debut + timedelta(days=random.randint(0, (date_fin - date_debut).days))
            avis = random.choice(avis_exemples)
            vote = random.choice(votes)
            
            participations.append([id_citoyen, idx, date_part.strftime('%Y-%m-%d %H:%M:%S'), 
                                 avis, vote])
    
    with open('participation_citoyenne.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_citoyen', 'id_consultation', 'date_participation', 'avis', 'vote'])
        writer.writerows(participations)
    print(f"✓ participation_citoyenne.csv created ({len(participations)} participations)")

# ============================================================================
# 12. VEHICULE_AUTONOME
# ============================================================================
def generate_vehicules():
    vehicules = [
        ('VA-2024-001', 'Navette électrique 12 places', 'électrique'),
        ('VA-2024-002', 'Bus autonome 30 places', 'hydrogène'),
        ('VA-2024-003', 'Véhicule de livraison compact', 'électrique'),
        ('VA-2024-004', 'Minibus 18 places', 'électrique'),
        ('VA-2024-005', 'Camion de collecte déchets', 'hybride'),
        ('VA-2024-006', 'Navette rapide 8 places', 'électrique'),
        ('VA-2024-007', 'Bus articulé 60 places', 'hydrogène'),
        ('VA-2024-008', 'Véhicule utilitaire municipal', 'électrique'),
        ('VA-2024-009', 'Navette aéroport 20 places', 'hydrogène'),
        ('VA-2024-010', 'Bus scolaire autonome', 'électrique')
    ]
    
    with open('vehicule_autonome.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['plaque_immatriculation', 'type_vehicule', 'energie_utilisee'])
        writer.writerows(vehicules)
    print("✓ vehicule_autonome.csv created")
    return vehicules

# ============================================================================
# 13. TRAJET
# ============================================================================
def generate_trajets(vehicules):
    locations = [
        'Place Farhat Hached', 'Port de Sousse', 'Médina', 'Stade Olympique',
        'Zone Industrielle', 'Palais des Congrès', 'Gare Ferroviaire', 'Centre Ville',
        'Quartier Khezama', 'Corniche', 'Hôpital Universitaire', 'Campus Universitaire',
        'Aéroport Monastir', 'Sousse Nord', 'Sousse Sud'
    ]
    
    trajets = []
    
    # Générer trajets pour les 30 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for vehicule in vehicules:
        plaque = vehicule[0]
        
        current_date = start_date
        while current_date <= end_date:
            # 5-12 trajets par jour par véhicule
            num_trajets = random.randint(5, 12)
            
            for _ in range(num_trajets):
                origine = random.choice(locations)
                destination = random.choice([l for l in locations if l != origine])
                
                heure_depart = current_date.replace(
                    hour=random.randint(6, 22), 
                    minute=random.randint(0, 59)
                )
                duree = random.randint(10, 50)
                
                # Économie CO2 basée sur la distance
                distance = random.uniform(2, 30)
                economie_co2 = round(distance * random.uniform(0.10, 0.15), 2)
                
                trajets.append([plaque, origine, destination,
                              heure_depart.strftime('%Y-%m-%d %H:%M:%S'),
                              duree, economie_co2])
            
            current_date += timedelta(days=1)
    
    with open('trajet.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['plaque_immatriculation', 'origine', 'destination', 
                        'date_heure_depart', 'duree_minutes', 'economie_co2_kg'])
        writer.writerows(trajets)
    print(f"✓ trajet.csv created ({len(trajets)} trajets)")

# ============================================================================
# EXÉCUTION PRINCIPALE
# ============================================================================

print("Génération des fichiers CSV...\n")

arrondissements = generate_arrondissements()
proprietaires = generate_proprietaires()
capteurs = generate_capteurs(arrondissements, len(proprietaires))
generate_mesures(capteurs)
techniciens = generate_techniciens()
interventions = generate_interventions(capteurs, len(techniciens))
generate_validations_ia(interventions)
generate_intervention_technicien(interventions, len(techniciens))
citoyens = generate_citoyens()
consultations = generate_consultations()
generate_participations(consultations, len(citoyens))
vehicules = generate_vehicules()
generate_trajets(vehicules)

print("\n" + "="*70)
print("✅ TOUS LES FICHIERS CSV ONT ÉTÉ GÉNÉRÉS AVEC SUCCÈS!")
print("="*70)
print("\nFichiers créés:")
print("  1. arrondissement.csv")
print("  2. proprietaire.csv")
print("  3. capteur.csv")
print("  4. mesure.csv")
print("  5. technicien.csv")
print("  6. intervention.csv")
print("  7. validation_ia.csv")
print("  8. intervention_technicien.csv")
print("  9. citoyen.csv")
print(" 10. consultation_citoyenne.csv")
print(" 11. participation_citoyenne.csv")
print(" 12. vehicule_autonome.csv")
print(" 13. trajet.csv")
print("\n" + "="*70)
print("INSTRUCTIONS D'IMPORTATION:")
print("="*70)
