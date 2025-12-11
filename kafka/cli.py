"""
Smart City Real-Time Update CLI
Simple interface to update sensors, add measurements, and manage interventions
"""

import sys
import uuid
from producer import SmartCityProducer
from datetime import datetime

class SmartCityCLI:
    def __init__(self):
        self.producer = SmartCityProducer()
        print("\n" + "="*70)
        print("SMART CITY NEO-SOUSSE - Real-Time Update Interface")
        print("="*70 + "\n")
    
    def show_menu(self):
        """Display the main menu"""
        print("\n📋 OPTIONS:")
        print("1. Update sensor status (actif → maintenance, etc.)")
        print("2. Add new sensor")
        print("3. Add measurement for existing sensor")
        print("4. Create intervention")
        print("5. Quick test - Update existing sensor to maintenance")
        print("0. Exit")
        print()
    
    def update_sensor_status(self):
        """Update sensor status"""
        print("\n=== UPDATE SENSOR STATUS ===")
        id_capteur = input("Enter sensor UUID (e.g., 29ebd779-abe5-4aa6-bcf2-4755115c421e): ").strip()
        
        print("\nAvailable statuses: actif, maintenance, hors_service")
        new_status = input("Enter new status: ").strip()
        
        reason = input("Reason for change (optional): ").strip() or None
        
        try:
            self.producer.update_sensor_status(id_capteur, new_status, reason)
            print("\n✅ Status update sent to Kafka!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def add_new_sensor(self):
        """Add a new sensor"""
        print("\n=== ADD NEW SENSOR ===")
        
        # Generate new UUID or use provided one
        use_new_uuid = input("Generate new UUID? (y/n): ").strip().lower()
        if use_new_uuid == 'y':
            id_capteur = str(uuid.uuid4())
            print(f"Generated UUID: {id_capteur}")
        else:
            id_capteur = input("Enter sensor UUID: ").strip()
        
        type_capteur = input("Sensor type (e.g., énergie, pollution, éclairage): ").strip()
        localisation = input("Location (e.g., Avenue Bourguiba): ").strip()
        
        print("\nAvailable statuses: actif, maintenance, hors_service")
        statut = input("Status: ").strip()
        
        id_proprietaire = int(input("Owner ID (1-5): ").strip())
        id_arrondissement = int(input("Arrondissement ID (1-8): ").strip())
        date_installation = input("Installation date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if not date_installation:
            date_installation = datetime.now().strftime('%Y-%m-%d')
        
        sensor_data = {
            'id_capteur': id_capteur,
            'type_capteur': type_capteur,
            'localisation_geographique': localisation,
            'statut': statut,
            'id_proprietaire': id_proprietaire,
            'id_arrondissement': id_arrondissement,
            'date_installation': date_installation
        }
        
        try:
            self.producer.add_new_sensor(sensor_data)
            print("\n✅ New sensor sent to Kafka!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def add_measurement(self):
        """Add a measurement"""
        print("\n=== ADD MEASUREMENT ===")
        
        id_capteur = input("Enter sensor UUID: ").strip()
        valeur_mesuree = float(input("Measured value: ").strip())
        unite_mesure = input("Unit (e.g., kWh, µg/m³, lux): ").strip()
        
        print("\nQuality levels: bonne, moyenne, mauvaise, critique")
        qualite = input("Quality (or press Enter for 'bonne'): ").strip() or 'bonne'
        
        measurement_data = {
            'id_capteur': id_capteur,
            'valeur_mesuree': valeur_mesuree,
            'unite_mesure': unite_mesure,
            'qualite': qualite
        }
        
        try:
            self.producer.add_measurement(measurement_data)
            print("\n✅ Measurement sent to Kafka!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def create_intervention(self):
        """Create an intervention"""
        print("\n=== CREATE INTERVENTION ===")
        
        id_capteur = input("Enter sensor UUID: ").strip()
        
        print("\nIntervention types: predictive, corrective, curative")
        nature = input("Intervention type: ").strip()
        
        duree = int(input("Duration (minutes): ").strip())
        cout = float(input("Cost (euros): ").strip())
        co2 = float(input("CO2 impact (kg, optional): ").strip() or 0)
        id_tech = input("Technician ID (optional): ").strip() or None
        
        if id_tech:
            id_tech = int(id_tech)
        
        intervention_data = {
            'id_capteur': id_capteur,
            'nature_intervention': nature,
            'duree_minutes': duree,
            'cout_euros': cout,
            'impact_environnemental_co2_kg': co2,
            'id_technicien': id_tech
        }
        
        try:
            self.producer.add_intervention(intervention_data)
            print("\n✅ Intervention sent to Kafka!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def quick_test(self):
        """Quick test with existing sensor"""
        print("\n=== QUICK TEST ===")
        print("Updating sensor 29ebd779-abe5-4aa6-bcf2-4755115c421e to 'maintenance'")
        
        try:
            self.producer.update_sensor_status(
                id_capteur='29ebd779-abe5-4aa6-bcf2-4755115c421e',
                new_status='maintenance',
                reason='Test from CLI - requires calibration'
            )
            print("\n✅ Test update sent!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def run(self):
        """Run the CLI interface"""
        try:
            while True:
                self.show_menu()
                choice = input("Select an option: ").strip()
                
                if choice == '1':
                    self.update_sensor_status()
                elif choice == '2':
                    self.add_new_sensor()
                elif choice == '3':
                    self.add_measurement()
                elif choice == '4':
                    self.create_intervention()
                elif choice == '5':
                    self.quick_test()
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n⚠️  Invalid option. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        finally:
            self.producer.close()


if __name__ == '__main__':
    cli = SmartCityCLI()
    cli.run()
