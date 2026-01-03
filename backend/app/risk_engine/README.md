# Risk Assessment Engine

Production-ready risk assessment engine for ReconVault that scores entities and relationships based on exposure, threat level, and behavioral indicators using XGBoost and machine learning.

## Architecture

### Components

1. **Risk Analyzer** (`risk_analyzer.py`)
   - Core risk assessment engine
   - Combines ML models with rule-based analysis
   - Calculates entity and relationship risks
   - Detects risk patterns across the intelligence graph
   - Generates comprehensive risk reports

2. **ML Models** (`ml_models.py`)
   - XGBoost-based risk classification
   - Feature extraction from entity metadata
   - Model training with cross-validation
   - Batch prediction capabilities
   - Model persistence and versioning

3. **Exposure Models** (`exposure_models.py`)
   - Data Exposure: Sensitive data leaks and breaches
   - Network Exposure: Network topology and connectivity risks
   - Identity Exposure: PII and identity-related risks
   - Infrastructure Exposure: Infrastructure vulnerabilities

4. **API Routes** (`/api/routes/risk.py`)
   - POST `/api/risk/analyze` - Analyze single entity
   - POST `/api/risk/analyze-batch` - Batch analysis
   - GET `/api/risk/report/{target_id}` - Generate risk report
   - GET `/api/risk/patterns` - Get pattern library
   - POST `/api/risk/recalculate` - Force recalculation
   - GET `/api/risk/metrics/{entity_id}` - Get entity metrics

## Risk Scoring Formula

```
Base Risk = (Exposure × 0.4) + (Threat_Level × 0.3) + (Behavioral_Indicators × 0.3)

Confidence = 0.7 + (Data_Quality × 0.3)

Final Risk = Base Risk (blended with ML prediction if model is trained)
```

### Risk Levels

- **0-25**: Low Risk (Green)
- **26-50**: Medium Risk (Yellow)
- **51-75**: High Risk (Orange)
- **76-100**: Critical Risk (Red)

## Machine Learning

### Features (19 total)

1. Entity type encoded
2. Data source count
3. Collection frequency
4. Relationship density
5. Is anomaly
6. Anomaly score
7. Breaches found
8. Dark web mentions
9. Malware detected
10. Phishing indicator
11. High-risk country
12. Domain age (days)
13. SSL expiry (days)
14. Has SSL
15. Open ports count
16. High-risk ports exposed
17. Confidence score
18. Existing risk score
19. Data quality

### Model Training

```python
from app.risk_engine.ml_models import RiskMLModel, generate_synthetic_training_data

# Generate training data
entities, labels = generate_synthetic_training_data(1000)

# Train model
model = RiskMLModel()
results = model.train_model(entities, labels)

# Save model
model.save_model()
```

### Using Trained Model

```python
from app.risk_engine.risk_analyzer import RiskAnalyzer

analyzer = RiskAnalyzer(db=db_session)
risk_assessment = analyzer.calculate_entity_risk(entity_dict)
```

## API Usage Examples

### Analyze Single Entity

```bash
curl -X POST "http://localhost:8000/api/risk/analyze" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": 123}'
```

### Batch Analysis

```bash
curl -X POST "http://localhost:8000/api/risk/analyze-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": [1, 2, 3, 4, 5],
    "include_relationships": true
  }'
```

### Generate Risk Report

```bash
curl -X GET "http://localhost:8000/api/risk/report/1"
```

### Recalculate Risks (Async)

```bash
curl -X POST "http://localhost:8000/api/risk/recalculate" \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "force": true
  }'
```

## Risk Patterns

The engine detects the following risk patterns:

1. **Breach Cluster** - Multiple entities found in data breaches
2. **Dark Web Exposure** - Entities found on dark web
3. **High Connectivity** - Entities with many connections (pivot points)
4. **Malware Infrastructure** - Malware-related infrastructure
5. **Vulnerability Chain** - Chain of vulnerable entities
6. **Anomaly Cluster** - Cluster of anomalous entities

## Celery Integration

### Async Risk Calculation

```python
from app.automation.celery_tasks import calculate_risks_async

# Queue async task
task = calculate_risks_async.delay(entity_ids=[1, 2, 3, 4, 5])
```

### Periodic Risk Updates

The `periodic_risk_update` task can be scheduled to run periodically:

```python
# In celery beat schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'periodic-risk-update': {
        'task': 'app.automation.celery_tasks.periodic_risk_update',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

## Exposure Analysis

### Data Exposure

Measures:
- Data breach history
- Dark web mentions
- PII exposure
- Credentials leaked
- Database dumps
- Paste site mentions

### Network Exposure

Measures:
- Open ports
- High-risk port exposure
- Public accessibility
- Firewall detection
- Weak encryption
- Relationship density

### Identity Exposure

Measures:
- Email/phone exposure
- Social media visibility
- PII fields exposed
- Identity theft indicators
- Multiple online identities

### Infrastructure Exposure

Measures:
- SSL/TLS status
- Software vulnerabilities
- CVE count
- Outdated software
- Misconfigurations
- Unpatched systems
- Weak authentication
- Default credentials

## Testing

Run the test suite:

```bash
cd /home/engine/project/backend
python -m pytest app/risk_engine/test_risk_engine.py -v
```

## Training Initial Model

Generate and train an initial model with synthetic data:

```bash
cd /home/engine/project/backend
python -m app.risk_engine.train_initial_model --samples 1000
```

## Database Integration

Risk scores are automatically stored in the `entities` table:
- `risk_score` field is updated on each calculation
- Historical tracking can be implemented via risk_history table

## Performance Considerations

- **Caching**: Implement Redis caching for frequently accessed risk scores
- **Batch Processing**: Use batch endpoints for analyzing multiple entities
- **Async Processing**: Use Celery tasks for large-scale risk calculations
- **Model Updates**: Retrain ML model periodically with real data

## Future Enhancements

1. Risk score history tracking (risk_history table)
2. Risk trend analysis and forecasting
3. Advanced pattern detection using graph algorithms
4. Real-time risk score updates via WebSocket
5. Customizable risk scoring weights
6. Industry-specific risk models
7. Threat intelligence feed integration
8. Automated remediation recommendations

## Dependencies

- XGBoost 2.0.3
- scikit-learn 1.3.2
- lightgbm 4.1.1
- numpy 1.26.2
- joblib 1.3.2

All dependencies are included in `backend/requirements.txt`.
