"""
ETL Script Simplifié - Neo-Sousse 2030
Extrait les données des CSV existants et les charge dans PostgreSQL
"""

import psycopg2
import csv
import os



DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'neosousse',
    'user': 'postgres',
    'password': 'neosousse2030'  # Changez selon votre mot de passe
}

DATA_FOLDER = './data'  # Dossier contenant vos fichiers CSV



def connect_db():
    """Se connecter à PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connexion réussie à PostgreSQL\n")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

=

def import_csv(conn, csv_filename, table_name, columns, transform_row=None):
    """
    Importe un fichier CSV dans une table PostgreSQL
    
    Args:
        conn: Connexion PostgreSQL
        csv_filename: Nom du fichier CSV
        table_name: Nom de la table
        columns: Liste des colonnes
        transform_row: Fonction optionnelle pour transformer les données
    """
    cursor = conn.cursor()
    csv_path = os.path.join(DATA_FOLDER, csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Fichier introuvable: {csv_filename}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            batch = []
            
            for row in reader:
                # Transformer la ligne si nécessaire
                if transform_row:
                    values = transform_row(row)
                else:
                    values = [row.get(col, None) or None for col in columns]
                
                batch.append(values)
                
                # Insertion par batch de 1000 pour performance
                if len(batch) >= 1000:
                    placeholders = ','.join(['%s'] * len(columns))
                    query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    cursor.executemany(query, batch)
                    count += len(batch)
                    batch = []
            
            # Insérer le reste
            if batch:
                placeholders = ','.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                cursor.executemany(query, batch)
                count += len(batch)
        
        conn.commit()
        print(f"✅ {table_name:30s} : {count:>6} lignes importées")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur {table_name}: {e}")
    finally:
        cursor.close()



def import_all_data(conn):
    """Importe toutes les données dans l'ordre des dépendances"""
    
    print("=" * 70)
    print("IMPORTATION DES DONNÉES")
    print("=" * 70 + "\n")
    
   
    import_csv(
        conn, 
        'arrondissement.csv',
        'Arrondissement',
        ['nom_arrondissement', 'superficie_km2', 'population']
    )
    

    import_csv(
        conn,
        'proprietaire.csv',
        'Proprietaire',
        ['nom_proprietaire', 'type_proprietaire', 'adresse', 'telephone', 'email']
    )
    

    import_csv(
        conn,
        'capteur.csv',
        'Capteur',
        ['id_capteur', 'type_capteur', 'localisation_geographique', 'statut', 
         'id_proprietaire', 'id_arrondissement', 'date_installation']
    )
    

    import_csv(
        conn,
        'mesure.csv',
        'Mesure',
        ['id_mesure', 'id_capteur', 'date_heure_mesure', 'valeur_mesuree', 
         'unite_mesure', 'qualite']
    )
    

    import_csv(
        conn,
        'technicien.csv',
        'Technicien',
        ['nom_technicien', 'prenom_technicien', 'certification', 'telephone', 
         'email', 'date_certification']
    )
    
    
    import_csv(
        conn,
        'intervention.csv',
        'Intervention',
        ['id_intervention', 'id_capteur', 'date_heure_intervention', 
         'nature_intervention', 'duree_minutes', 'cout_euros', 
         'impact_environnemental_co2_kg']
    )
    

    import_csv(
        conn,
        'validation_ia.csv',
        'Validation_IA',
        ['id_intervention', 'date_heure_validation', 'score_validation', 
         'statut_validation', 'commentaire_ia']
    )
    

    import_csv(
        conn,
        'intervention_technicien.csv',
        'Intervention_Technicien',
        ['id_intervention', 'id_technicien', 'role_technicien']
    )
    

    import_csv(
        conn,
        'citoyen.csv',
        'Citoyen',
        ['nom_citoyen', 'prenom_citoyen', 'adresse', 'telephone', 'email', 
         'score_engagement_ecologique', 'preferences_mobilite']
    )
    

    import_csv(
        conn,
        'consultation_citoyenne.csv',
        'Consultation_Citoyenne',
        ['titre_consultation', 'description', 'date_debut', 'date_fin', 'theme']
    )
    

    import_csv(
        conn,
        'participation_citoyenne.csv',
        'Participation_Citoyenne',
        ['id_citoyen', 'id_consultation', 'date_participation', 'avis', 'vote']
    )
    
   
    import_csv(
        conn,
        'vehicule_autonome.csv',
        'Vehicule_Autonome',
        ['plaque_immatriculation', 'type_vehicule', 'energie_utilisee']
    )
    
   
    import_csv(
        conn,
        'trajet.csv',
        'Trajet',
        ['plaque_immatriculation', 'origine', 'destination', 'date_heure_depart', 
         'duree_minutes', 'economie_co2_kg']
    )


def verify_data(conn):
    """Vérifie le nombre d'enregistrements dans chaque table"""
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("VÉRIFICATION DES DONNÉES CHARGÉES")
    print("=" * 70 + "\n")
    
    tables = [
        'Arrondissement', 'Proprietaire', 'Capteur', 'Mesure', 'Technicien',
        'Intervention', 'Validation_IA', 'Intervention_Technicien', 'Citoyen',
        'Consultation_Citoyenne', 'Participation_Citoyenne', 
        'Vehicule_Autonome', 'Trajet'
    ]
    
    total = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:30s} : {count:>10,} lignes")
            total += count
        except Exception as e:
            print(f"{table:30s} : ❌ Erreur")
    
    print("-" * 70)
    print(f"{'TOTAL':30s} : {total:>10,} lignes")
    
    cursor.close()



def main():
    """Fonction principale ETL"""
    print("=" * 70)
    print("ETL NEO-SOUSSE 2030 - Extract, Transform, Load")
    print("=" * 70 + "\n")
    
    # Vérifier que le dossier data existe
    if not os.path.exists(DATA_FOLDER):
        print(f"❌ Le dossier '{DATA_FOLDER}' n'existe pas!")
        print(f"   Créez-le et placez-y vos fichiers CSV.")
        return
    
    # Se connecter à la base
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Importer toutes les données
        import_all_data(conn)
        
        # Vérifier les données
        verify_data(conn)
        
        print("\n" + "=" * 70)
        print("✅ ETL TERMINÉ AVEC SUCCÈS!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        conn.close()
        print("\n✓ Connexion fermée\n")



if __name__ == "__main__":
    main()