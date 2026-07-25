# Architecture

AegisUEBA uses a hybrid stack:

1. Synthetic generator creates stable entity baselines and chronological events.
2. Attack injectors overlay controlled adversarial behaviors.
3. Leakage-safe feature engineering derives temporal, geo, device, and session features.
4. Entity and peer profiles score behavioral deviation.
5. Isolation Forest and a GRU autoencoder add unsupervised anomaly evidence.
6. Contextual rules add security-specific evidence such as impossible travel and brute force.
7. A supervised classifier assigns likely attack labels for suspicious behavior.
8. The risk engine fuses normalized components into a 0-100 analyst-facing score.
