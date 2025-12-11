"""
Kafka Producer - Smart City Neo-Sousse
Sends real-time updates for sensors and measurements
"""

from kafka import KafkaProducer
import json
import time
from datetime import datetime

class SmartCityProducer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        print("✅ Kafka Producer initialized")
    
    def update_sensor_status(self, id_capteur, new_status, reason=None):
        """
        Update sensor status in real-time
        
        Args:
            id_capteur: UUID of the sensor
            new_status: 'actif', 'maintenance', or 'hors_service'
            reason: Optional reason for the status change
        """
        message = {
            'action': 'update_status',
            'id_capteur': id_capteur,
            'new_status': new_status,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('sensor_updates', key=id_capteur, value=message)
        self.producer.flush()
        print(f"📤 Status update sent: {id_capteur} → {new_status}")
        return message
    
    def add_new_sensor(self, sensor_data):
        """
        Add a new sensor and related data
        
        Args:
            sensor_data: dict with keys:
                - id_capteur (UUID)
                - type_capteur
                - localisation_geographique
                - statut
                - id_proprietaire
                - id_arrondissement
                - date_installation
        """
        message = {
            'action': 'add_sensor',
            'sensor': sensor_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('sensor_updates', key=sensor_data['id_capteur'], value=message)
        self.producer.flush()
        print(f"📤 New sensor added: {sensor_data['id_capteur']}")
        return message
    
    def add_measurement(self, measurement_data):
        """
        Add a new measurement from a sensor
        
        Args:
            measurement_data: dict with keys:
                - id_capteur (UUID)
                - valeur_mesuree
                - unite_mesure
                - qualite (optional)
        """
        message = {
            'action': 'add_measurement',
            'measurement': {
                'id_capteur': measurement_data['id_capteur'],
                'date_heure_mesure': datetime.now().isoformat(),
                'valeur_mesuree': measurement_data['valeur_mesuree'],
                'unite_mesure': measurement_data['unite_mesure'],
                'qualite': measurement_data.get('qualite', 'bonne')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('sensor_readings', key=measurement_data['id_capteur'], value=message)
        self.producer.flush()
        print(f"📤 Measurement sent: {measurement_data['id_capteur']} = {measurement_data['valeur_mesuree']}")
        return message
    
    def add_intervention(self, intervention_data):
        """
        Add a new intervention for a sensor
        
        Args:
            intervention_data: dict with keys:
                - id_capteur (UUID)
                - nature_intervention ('predictive', 'corrective', 'curative')
                - duree_minutes
                - cout_euros
                - impact_environnemental_co2_kg
                - id_technicien (optional)
        """
        message = {
            'action': 'add_intervention',
            'intervention': {
                'id_capteur': intervention_data['id_capteur'],
                'date_heure_intervention': datetime.now().isoformat(),
                'nature_intervention': intervention_data['nature_intervention'],
                'duree_minutes': intervention_data['duree_minutes'],
                'cout_euros': intervention_data['cout_euros'],
                'impact_environnemental_co2_kg': intervention_data.get('impact_environnemental_co2_kg', 0),
                'id_technicien': intervention_data.get('id_technicien')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.producer.send('interventions', key=intervention_data['id_capteur'], value=message)
        self.producer.flush()
        print(f"📤 Intervention sent: {intervention_data['id_capteur']}")
        return message
    
    def close(self):
        self.producer.close()
        print("✅ Producer closed")


# Example usage
if __name__ == '__main__':
    producer = SmartCityProducer()
    
    try:
        # Example 1: Change sensor status from 'actif' to 'maintenance'
        print("\n=== Example 1: Update sensor status ===")
        producer.update_sensor_status(
            id_capteur='29ebd779-abe5-4aa6-bcf2-4755115c421e',
            new_status='maintenance',
            reason='Calibration périodique requise'
        )
        time.sleep(1)
        
        # Example 2: Add a new sensor
        print("\n=== Example 2: Add new sensor ===")
        new_sensor = {
            'id_capteur': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            'type_capteur': 'pollution',
            'localisation_geographique': 'Avenue Bourguiba',
            'statut': 'actif',
            'id_proprietaire': 1,
            'id_arrondissement': 3,
            'date_installation': '2025-12-10'
        }
        producer.add_new_sensor(new_sensor)
        time.sleep(1)
        
        # Example 3: Add measurement for the new sensor
        print("\n=== Example 3: Add measurement ===")
        producer.add_measurement({
            'id_capteur': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            'valeur_mesuree': 42.5,
            'unite_mesure': 'µg/m³',
            'qualite': 'bonne'
        })
        time.sleep(1)
        
        # Example 4: Add intervention
        print("\n=== Example 4: Add intervention ===")
        producer.add_intervention({
            'id_capteur': '29ebd779-abe5-4aa6-bcf2-4755115c421e',
            'nature_intervention': 'predictive',
            'duree_minutes': 45,
            'cout_euros': 150.00,
            'impact_environnemental_co2_kg': 5.2,
            'id_technicien': 1
        })
        
        print("\n✅ All examples sent successfully!")
        
    finally:
        producer.close()
