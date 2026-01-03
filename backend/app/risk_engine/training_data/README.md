# Risk Engine Training Data

This directory contains training data for the XGBoost risk classification model.

## Data Format

Training data should be in CSV format with the following structure:

### Features (Columns)
1. `entity_type_encoded` - Entity type (0-16)
2. `data_source_count` - Number of data sources
3. `collection_frequency` - Times entity was collected
4. `relationship_density` - Number of relationships
5. `is_anomaly` - Anomaly flag (0/1)
6. `anomaly_score` - Anomaly score (-1 to 1)
7. `breaches_found` - Number of data breaches
8. `dark_web_mentions` - Dark web presence (0/1)
9. `malware_detected` - Malware detected (0/1)
10. `phishing_indicator` - Phishing flag (0/1)
11. `high_risk_country` - High-risk geolocation (0/1)
12. `domain_age_days` - Domain age in days
13. `ssl_expiry_days` - Days until SSL expiry
14. `has_ssl` - SSL present (0/1)
15. `open_ports_count` - Number of open ports
16. `high_risk_ports_exposed` - High-risk ports exposed
17. `confidence` - Data confidence (0-1)
18. `existing_risk_score` - Previous risk score (0-100)
19. `data_quality` - Data quality score (0-1)

### Label
- `risk_class` - Risk classification (0=low, 1=medium, 2=high, 3=critical)

## Generating Training Data

You can generate synthetic training data using the provided function:

```python
from app.risk_engine.ml_models import generate_synthetic_training_data

# Generate 1000 samples
entities, labels = generate_synthetic_training_data(1000)

# Train model
from app.risk_engine.ml_models import RiskMLModel
model = RiskMLModel()
results = model.train_model(entities, labels)
model.save_model()
```

## Model Training

To train the model with real data:

1. Collect historical OSINT data from the database
2. Export entities with risk scores to CSV
3. Use the `train_model()` method of `RiskMLModel`
4. Save the trained model using `save_model()`

## Data Requirements

- **Minimum samples**: 1000+ entities
- **Feature coverage**: All 19 features should be populated
- **Label balance**: Try to maintain balanced distribution across risk classes
- **Data quality**: Ensure data is normalized and validated

## Example CSV Structure

```csv
entity_type_encoded,data_source_count,collection_frequency,relationship_density,is_anomaly,anomaly_score,breaches_found,dark_web_mentions,malware_detected,phishing_indicator,high_risk_country,domain_age_days,ssl_expiry_days,has_ssl,open_ports_count,high_risk_ports_exposed,confidence,existing_risk_score,data_quality,risk_class
2,3,5,12,0,0.0,0,0,0,0,0,730,90,1,2,0,0.85,15.5,0.75,0
1,5,8,25,1,0.6,2,1,0,1,1,45,10,0,8,3,0.65,75.2,0.60,3
```

## Notes

- The model uses XGBoost for classification
- Cross-validation is performed with 80/20 split
- Features are standardized using StandardScaler
- Model and scaler are saved in the `models/` directory
