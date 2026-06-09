# Architecture Boundaries

## Allowed Dependencies

Dashboard
    ↓
Services
    ↓
Analytics
    ↓
Repositories
    ↓
Data

Dashboard
    ↓
Services
    ↓
Risk

Dashboard
    ↓
Services
    ↓
Execution

---

## Forbidden Dependencies

Dashboard → Analytics

Dashboard → Risk

Dashboard → Execution

Dashboard → Data

Analytics → Dashboard

Risk → Dashboard

Execution → Dashboard

Analytics → Streamlit

Risk → Streamlit

Execution → Streamlit

---

## Service Ownership

Market Data
    services/market_data_service.py

Signals
    services/signal_service.py

Portfolio
    services/portfolio_service.py

Risk
    services/risk_service.py

Execution
    services/execution_service.py

Monitoring
    services/monitoring_service.py

---

## Data Ownership

Raw Data
    data/raw

Processed Data
    data/processed

Portfolio Outputs
    data/portfolio

Models
    data/models

Reports
    data/reports

Logs
    data/logs

Cache
    data/cache

Database
    data/duckdb

---

## Future Target

Dashboard
    ↓
Services
    ↓
Analytics
    ↓
Repositories
    ↓
DuckDB

No direct CSV access outside repositories.
