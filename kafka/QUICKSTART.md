# Quick Start Guide - Real-Time Kafka Streaming

## ✅ System Ready!

All Kafka topics have been created:
- `sensor_updates` (3 partitions)
- `sensor_readings` (3 partitions)  
- `interventions` (1 partition)

## How to Use

### Step 1: Start the Consumer (Terminal 1)
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

**Keep this terminal running!** It listens for Kafka messages and updates the database.

### Step 2: Use the CLI (Terminal 2)
```bash
cd c:\Users\medya\Desktop\project_DB\kafka
python cli.py
```

### Quick Test Example

1. In the CLI, choose option **5** (Quick test)
   - This updates sensor `29ebd779-abe5-4aa6-bcf2-4755115c421e` to "maintenance"

2. Watch Terminal 1 (consumer) - you'll see:
   ```
   📥 Received message from topic 'sensor_updates'
   ✅ Updated sensor 29ebd779-abe5-4aa6-bcf2-4755115c421e status to 'maintenance'
   ✅ Auto-created maintenance intervention for 29ebd779-abe5-4aa6-bcf2-4755115c421e
   ```

3. Verify in database:
   ```bash
   docker exec -it postgres_db psql -U chouket -d smart_city
   ```
   ```sql
   SELECT id_capteur, type_capteur, statut, localisation_geographique 
   FROM capteur 
   WHERE id_capteur = '29ebd779-abe5-4aa6-bcf2-4755115c421e';
   ```

## Real-World Examples

### Example 1: Change Sensor Status
```
CLI Menu → 1 (Update sensor status)
Enter UUID: 29ebd779-abe5-4aa6-bcf2-4755115c421e
Status: maintenance
Reason: Requires calibration
```

Result: Database updated instantly + intervention created automatically!

### Example 2: Add New Sensor
```
CLI Menu → 2 (Add new sensor)
Generate UUID: y
Type: pollution
Location: Avenue Habib Bourguiba
Status: actif
Owner ID: 1
Arrondissement: 3
Date: (press Enter for today)
```

Result: New sensor appears in database immediately!

### Example 3: Stream Measurements
```
CLI Menu → 3 (Add measurement)
Sensor UUID: 29ebd779-abe5-4aa6-bcf2-4755115c421e
Value: 125.5
Unit: kWh
Quality: bonne
```

Result: Measurement inserted in real-time!

## Benefits of This System

✅ **Real-time updates** - Changes reflect instantly
✅ **Decoupled architecture** - Producer and consumer are independent
✅ **Scalable** - Can handle high-volume sensor data
✅ **Automatic propagation** - Related tables update automatically
✅ **Event-driven** - Status changes trigger interventions
✅ **Persistent** - Kafka retains messages if consumer is down

## Monitoring

### Watch Kafka Messages Live
```bash
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic sensor_updates --from-beginning
```

### Check Consumer Group
```bash
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group smart_city_consumer_group
```

## Troubleshooting

### Consumer not receiving messages?
- Check if consumer is running (Terminal 1)
- Verify Kafka is running: `docker ps`
- Check topics exist: `docker exec kafka kafka-topics --list --bootstrap-server localhost:9092`

### Database not updating?
- Check PostgreSQL is running: `docker ps`
- Verify connection in consumer output
- Check for error messages in consumer terminal

## Next Steps

1. ✅ Start consumer (Terminal 1): `python consumer.py`
2. ✅ Run CLI (Terminal 2): `python cli.py`
3. ✅ Try option 5 for quick test
4. ✅ Update sensor statuses in real-time
5. ✅ Add new sensors dynamically
6. ✅ Stream measurements continuously

Enjoy your real-time Smart City system! 🚀
