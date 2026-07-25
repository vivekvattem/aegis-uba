# Deployment Notes

The local demo is file-based and CPU-only. A production-oriented extension path would:

1. Emit normalized events onto Kafka, Redpanda, Kinesis, Pub/Sub, or MQTT.
2. Maintain entity/profile state in a low-latency state store.
3. Score events in a stateless worker tier with periodic model refresh.
4. Publish alerts to SIEM/SOAR queues and analyst dashboards.
