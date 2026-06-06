# Module Ownership

## Purpose

This document defines the authoritative owner for each business domain in the Institutional Quant Platform.

Rule:

> Every capability must have exactly one source of truth.

No duplicate implementations should exist across modules.

---

# Ownership Matrix

| Domain | Authoritative Module |
|----------|----------|
| AI & Forecasting | ai/ |
| Research | research/ |
| Feature Engineering | features/ |
| Signals | signals/ |
| Portfolio Construction | portfolio/ |
| Risk Management | risk/ |
| Trade Execution | execution/ |
| Paper Trading | paper_trading/ |
| Monitoring | monitoring/ |
| Automation | automation/ |
| Reporting | reporting/ |
| Dashboard/UI | dashboard/ |
| Configuration | configs/ |
| Infrastructure | core/ |
| Governance | governance/ |
| Cloud Services | cloud/ |

---

# Domain Responsibilities

## core/

Platform-wide shared services.

### Owns

- Orchestration
- Configuration loading
- Logging
- Common utilities
- Market data interfaces
- Backup and recovery

### Must NOT contain

- Portfolio logic
- Risk calculations
- Dashboard code

---

## research/

Research and experimentation environment.

### Owns

- Alpha research
- Walk-forward testing
- Factor clustering
- Bayesian optimization
- Experiment tracking

### Must NOT contain

- Production execution logic

---

## signals/

Signal generation layer.

### Owns

- Buy signals
- Sell signals
- Signal scoring
- Signal ranking

### Inputs

```text
Research
Factors
Features
```

### Outputs

```text
Signal Objects
```

---

## portfolio/

Portfolio construction layer.

### Owns

- Allocation models
- Risk parity
- Position sizing
- Portfolio analytics
- Performance attribution

### Inputs

```text
Signals
```

### Outputs

```text
Target Weights
```

---

## risk/

Risk management layer.

### Owns

- VaR
- CVaR
- Drawdown
- Stress testing
- Exposure monitoring
- Factor exposure

### Inputs

```text
Portfolio
Market Data
```

### Outputs

```text
Risk Metrics
Risk Scores
```

---

## execution/

Execution simulation and broker connectivity.

### Owns

- Execution simulation
- Broker interfaces
- Transaction costs
- Slippage
- Order management

### Inputs

```text
Portfolio Orders
```

### Outputs

```text
Trades
```

---

## paper_trading/

Paper trading environment.

### Owns

- Positions
- Orders
- PnL
- Trade ledger

---

## monitoring/

Operational observability.

### Owns

- System health
- Metrics
- Alerts
- Logging dashboards

---

## automation/

Scheduled platform operations.

### Owns

- Data refresh
- Notifications
- Batch jobs
- Scheduled reporting

---

## dashboard/

Presentation layer only.

### Owns

- Streamlit pages
- Charts
- Tables
- User interaction

### Must NOT contain

- Business logic
- Risk calculations
- Portfolio calculations

Dashboards should consume services only.

---

## reporting/

Reporting engine.

### Owns

- Factsheets
- Excel exports
- PDF reports
- Institutional reports

---

## ai/

Machine learning and forecasting.

### Owns

- Alpha forecasting
- Reinforcement learning
- Deep learning
- Transformer models
- Ensemble models

---

# Deprecation Policy

Duplicate implementations are not allowed.

Examples:

Current:

analytics/risk_engine.py
risk/risk_engine.py

Target:

risk/risk_engine.py

analytics/risk_engine.py

```python
from risk.risk_engine import *
```

---

# Future Service Layer

All dashboards should communicate through:

```text
services/
│
├── market_data_service.py
├── signal_service.py
├── portfolio_service.py
├── risk_service.py
└── execution_service.py
```

Instead of directly importing low-level engines.

---

# Ownership Review

This document must be reviewed before:

- Creating new modules
- Moving modules
- Refactoring architecture
- Major releases
