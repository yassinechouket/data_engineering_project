# Kafka Real-Time Data Streaming - Smart City Neo-Sousse

## Overview
This system allows real-time updates to the PostgreSQL database through Kafka messaging:
- Update sensor statuses (actif → maintenance, etc.)
- Add new sensors dynamically
- Stream measurements in real-time
- Create interventions automatically

## Architecture
```
CLI/Producer → Kafka Topics → Consumer → PostgreSQL
```

## Setup Instructions

### 1. Start Docker Services
```bash
cd c:\Users\medya\Desktop\project_DB
docker-compose up -d
```

### 2. Create Kafka Topics
```bash
# Create sensor updates topic
docker exec -it kafka kafka-topics --create --topic sensor_updates --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create sensor readings topic
docker exec -it kafka kafka-topics --create --topic sensor_readings --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create interventions topic
docker exec -it kafka kafka-topics --create --topic interventions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Verify topics created
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 3. Install Python Dependencies
```bash
pip install kafka-python pandas sqlalchemy psycopg2
```

### 4. Initialize Database Schema
```bash
cd c:\Users\medya\Desktop\project_DB\ETL2
python etl.py
```

## Usage

### Start the Consumer (Terminal 1)
The consumer listens to Kafka topics and writes to PostgreSQL in real-time:
```bash
cd c:\Users\medya\Desktop\project_DB\kafka
python consumer.py
```

You should see:
```
✅ Kafka Consumer initialized and listening...
✅ Connected to PostgreSQL
🎧 Listening for messages...
```

### Use the CLI Interface (Terminal 2)
```bash
cd c:\Users\medya\Desktop\project_DB\kafka
python cli.py
```

#### Example: Update Sensor Status
1. Choose option `1` (Update sensor status)
2. Enter sensor UUID: `29ebd779-abe5-4aa6-bcf2-4755115c421e`
3. Enter new status: `maintenance`
4. Enter reason: `Calibration required`

The consumer will automatically update the database!

#### Example: Add New Sensor
1. Choose option `2` (Add new sensor)
2. Generate new UUID: `y`
3. Fill in sensor details
4. The consumer will insert the sensor and you can immediately add measurements

#### Quick Test
Choose option `5` for a quick test that updates an existing sensor to maintenance.

### Use the Producer Programmatically
```python
from kafka.producer import SmartCityProducer

producer = SmartCityProducer()

# Update sensor status
producer.update_sensor_status(
    id_capteur='29ebd779-abe5-4aa6-bcf2-4755115c421e',
    new_status='maintenance',
    reason='Needs calibration'
)

# Add new measurement
producer.add_measurement({
    'id_capteur': '29ebd779-abe5-4aa6-bcf2-4755115c421e',
    'valeur_mesuree': 125.5,
    'unite_mesure': 'kWh',
    'qualite': 'bonne'
})

producer.close()
```

## Kafka Topics

### `sensor_updates`
- Actions: `update_status`, `add_sensor`
- Updates sensor information in real-time

### `sensor_readings`
- Action: `add_measurement`
- Streams sensor measurements continuously

### `interventions`
- Action: `add_intervention`
- Creates maintenance/intervention records

## Features

✅ **Real-time status updates** - Change sensor status instantly
✅ **Dynamic sensor addition** - Add new sensors without restarting
✅ **Automatic measurements** - Stream sensor data continuously
✅ **Intervention tracking** - Auto-create interventions on status change
✅ **Related table updates** - Updates propagate to connected tables

## Monitoring

### View Kafka Messages
```bash
# Monitor sensor_updates topic
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic sensor_updates --from-beginning

# Monitor sensor_readings topic
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic sensor_readings --from-beginning
```

### Check Database Updates
```bash
docker exec -it postgres_db psql -U chouket -d smart_city

# Check sensor status
SELECT id_capteur, type_capteur, statut, localisation_geographique 
FROM capteur 
WHERE id_capteur = '29ebd779-abe5-4aa6-bcf2-4755115c421e';

# Check recent measurements
SELECT * FROM mesure ORDER BY date_heure_mesure DESC LIMIT 10;
```

## Troubleshooting

### Kafka not connecting?
```bash
# Check if Kafka is running
docker ps

# Restart Kafka
docker-compose restart kafka zookeeper
```

### Database connection error?
```bash
# Check if PostgreSQL is running
docker exec -it postgres_db psql -U chouket -d smart_city -c "SELECT version();"
```

### Consumer not receiving messages?
- Make sure topics are created
- Check consumer is running
- Verify Kafka bootstrap server is `localhost:9092`

## Example Workflow

1. **Start consumer** (Terminal 1):
   ```bash
   python consumer.py
   ```

2. **Run CLI** (Terminal 2):
   ```bash
   python cli.py
   ```

3. **Update existing sensor**:
   - Option 1 → Enter UUID → Change status to "maintenance"
   - Watch consumer terminal for real-time update!

4. **Add new sensor**:
   - Option 2 → Generate UUID → Fill details
   - Watch it appear in database immediately

5. **Add measurements**:
   - Option 3 → Enter sensor UUID → Add measurement
   - Data streams in real-time!

## Project Structure
```
kafka/
├── producer.py      # Kafka producer - sends messages
├── consumer.py      # Kafka consumer - writes to database
├── cli.py          # Interactive CLI interface
└── README.md       # This file
```
