# Remaining Tasks

## Backend Tasks
- [ ] Implement WebSocket broadcast for anomaly detection in `backend/app/automation/celery_tasks.py`.
- [ ] Implement email reporting or database storage for daily anomaly reports in `backend/app/automation/celery_tasks.py`.
- [ ] Implement historical risk tracking and `risk_history` table as mentioned in `backend/app/api/routes/risk.py`.
- [ ] Enhance feature extraction in `backend/app/ai_engine/feature_engineering.py` to use historical data and temporal patterns.
- [ ] Implement proper TTL-based cleanup for the rate limiter in `backend/app/ethics/compliance.py`.
- [ ] Fix Neo4j connection pool management to prevent exhaustion.
- [ ] Implement database-level uniqueness constraints to prevent race conditions during concurrent collections.

## Frontend Tasks
- [ ] Optimize graph rendering using virtualization or WebGL for large datasets (1000+ nodes).
- [ ] Implement automatic WebSocket reconnection logic.
- [ ] Complete the "Ethics & Compliance" UI sections if any sub-features are missing.

## Infrastructure & DevOps
- [ ] Secure production configuration: set strong passwords for Redis, PostgreSQL, and Neo4j.
- [ ] Configure SSL/TLS for Nginx reverse proxy.
- [ ] Set up monitoring and alerting for service health and resource usage.
