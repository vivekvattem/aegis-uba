# Limitations

- The synthetic environment is configurable but still simplified compared with real SOC telemetry.
- Cross-entity campaign logic is represented in lightweight form rather than a full graph engine.
- The replay script simulates sequential scoring locally and documents the path to a real stream, but it does not connect to Kafka, Redpanda, Kinesis, Pub/Sub, or MQTT.
- The dashboard consumes generated artifacts rather than scoring live telemetry directly.
