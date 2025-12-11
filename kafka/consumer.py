"""
Kafka Consumer - Smart City Neo-Sousse
Consumes real-time updates and writes to PostgreSQL
"""

from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5339,
    'database': 'smart_city',
    'user': 'chouket',
    'password': '2003'
}

class SmartCityConsumer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.consumer = KafkaConsumer(
            'sensor_updates',
            'sensor_readings',
            'interventions',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='smart_city_consumer_group'
        )
        
        self.db_conn = None
        self.connect_db()
        print("✅ Kafka Consumer initialized and listening...")
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(**DB_CONFIG)
            self.db_conn.autocommit = False
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def update_sensor_status(self, message):
        """Update sensor status in the database"""
        try:
            cursor = self.db_conn.cursor()
            
            id_capteur = message['id_capteur']
            new_status = message['new_status']
            
            cursor.execute("""
                UPDATE Capteur 
                SET statut = %s
                WHERE id_capteur = %s
            """, (new_status, id_capteur))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Updated sensor {id_capteur} status to '{new_status}'")
            
            # If status changed to 'maintenance', create an intervention
            if new_status == 'maintenance' and message.get('reason'):
                self.create_maintenance_intervention(id_capteur, message['reason'])
                
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Error updating sensor status: {e}")
    
    def add_new_sensor(self, message):
        """Add a new sensor to the database"""
        try:
            cursor = self.db_conn.cursor()
            
            sensor = message['sensor']
            
            cursor.execute("""
                INSERT INTO Capteur 
                (id_capteur, type_capteur, localisation_geographique, statut, 
                 id_proprietaire, id_arrondissement, date_installation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_capteur) DO UPDATE SET
                    statut = EXCLUDED.statut,
                    localisation_geographique = EXCLUDED.localisation_geographique
            """, (
                sensor['id_capteur'],
                sensor['type_capteur'],
                sensor['localisation_geographique'],
                sensor['statut'],
                sensor['id_proprietaire'],
                sensor['id_arrondissement'],
                sensor['date_installation']
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Added new sensor {sensor['id_capteur']} at {sensor['localisation_geographique']}")
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Error adding sensor: {e}")
    
    def add_measurement(self, message):
        """Add a new measurement to the database"""
        try:
            cursor = self.db_conn.cursor()
            
            measurement = message['measurement']
            
            cursor.execute("""
                INSERT INTO Mesure 
                (id_capteur, date_heure_mesure, valeur_mesuree, unite_mesure, qualite)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                measurement['id_capteur'],
                measurement['date_heure_mesure'],
                measurement['valeur_mesuree'],
                measurement['unite_mesure'],
                measurement.get('qualite', 'bonne')
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Added measurement for sensor {measurement['id_capteur']}: {measurement['valeur_mesuree']} {measurement['unite_mesure']}")
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Error adding measurement: {e}")
    
    def add_intervention(self, message):
        """Add a new intervention to the database"""
        try:
            cursor = self.db_conn.cursor()
            
            intervention = message['intervention']
            
            # Insert intervention
            cursor.execute("""
                INSERT INTO Intervention 
                (id_capteur, date_heure_intervention, nature_intervention, 
                 duree_minutes, cout_euros, impact_environnemental_co2_kg)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_intervention
            """, (
                intervention['id_capteur'],
                intervention['date_heure_intervention'],
                intervention['nature_intervention'],
                intervention['duree_minutes'],
                intervention['cout_euros'],
                intervention['impact_environnemental_co2_kg']
            ))
            
            id_intervention = cursor.fetchone()[0]
            
            # If technician is specified, link them to the intervention
            if intervention.get('id_technicien'):
                cursor.execute("""
                    INSERT INTO Intervention_Technicien 
                    (id_intervention, id_technicien, role_technicien)
                    VALUES (%s, %s, %s)
                """, (id_intervention, intervention['id_technicien'], 'intervenant'))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Added intervention {id_intervention} for sensor {intervention['id_capteur']}")
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Error adding intervention: {e}")
    
    def create_maintenance_intervention(self, id_capteur, reason):
        """Automatically create a maintenance intervention"""
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("""
                INSERT INTO Intervention 
                (id_capteur, date_heure_intervention, nature_intervention, 
                 duree_minutes, cout_euros, impact_environnemental_co2_kg)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_capteur,
                datetime.now(),
                'corrective',
                30,  # Default 30 minutes
                100.00,  # Default cost
                0.0  # No CO2 impact yet
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Auto-created maintenance intervention for {id_capteur}")
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Error creating intervention: {e}")
    
    def process_message(self, message):
        """Process incoming Kafka message"""
        action = message.get('action')
        
        if action == 'update_status':
            self.update_sensor_status(message)
        elif action == 'add_sensor':
            self.add_new_sensor(message)
        elif action == 'add_measurement':
            self.add_measurement(message)
        elif action == 'add_intervention':
            self.add_intervention(message)
        else:
            print(f"⚠️  Unknown action: {action}")
    
    def consume(self):
        """Start consuming messages"""
        print("\n🎧 Listening for messages...\n")
        
        try:
            for message in self.consumer:
                print(f"\n📥 Received message from topic '{message.topic}'")
                print(f"   Timestamp: {datetime.fromtimestamp(message.timestamp / 1000)}")
                
                self.process_message(message.value)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Consumer stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close connections"""
        if self.consumer:
            self.consumer.close()
        if self.db_conn:
            self.db_conn.close()
        print("✅ Consumer closed")


# Run the consumer
if __name__ == '__main__':
    consumer = SmartCityConsumer()
    consumer.consume()
