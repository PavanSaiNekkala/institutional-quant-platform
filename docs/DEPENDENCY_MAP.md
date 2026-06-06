# Dependency Map

## Purpose

This document defines allowed dependencies between modules.

The goal is to maintain:

- Clear architecture
- Separation of concerns
- Low coupling
- High maintainability

---

# High-Level Architecture

```text
Market Data
      │
      ▼
Features
      │
      ▼
Research
      │
      ▼
Signals
      │
      ▼
Portfolio
      │
      ▼
Risk
      │
      ▼
Execution
      │
      ▼
Paper Trading
      │
      ▼
Monitoring
      │
      ▼
Dashboard
```

---

# Dependency Rules

## Layer 1

### core

Lowest-level shared infrastructure.

Everything may depend on:

```text
core/
```

core must depend on nothing except:

```text
Python libraries
External APIs
```

---

## Layer 2

### features

Allowed imports:

```text
core
```

Forbidden imports:

```text
portfolio
risk
execution
dashboard
```

---

## Layer 3

### research

Allowed imports:

```text
core
features
```

Forbidden imports:

```text
dashboard
execution
monitoring
```

---

## Layer 4

### signals

Allowed imports:

```text
core
research
features
```

Forbidden imports:

```text
dashboard
execution
```

---

## Layer 5

### portfolio

Allowed imports:

```text
signals
research
core
```

Forbidden imports:

```text
dashboard
monitoring
```

---

## Layer 6

### risk

Allowed imports:

```text
portfolio
signals
core
```

Forbidden imports:

```text
dashboard
monitoring
```

---

## Layer 7

### execution

Allowed imports:

```text
portfolio
risk
core
```

Forbidden imports:

```text
dashboard
research
```

---

## Layer 8

### paper_trading

Allowed imports:

```text
execution
portfolio
risk
```

Forbidden imports:

```text
dashboard
research
```

---

## Layer 9

### monitoring

Allowed imports:

```text
core
execution
risk
paper_trading
```

Forbidden imports:

```text
research
signals
```

---

## Layer 10

### reporting

Allowed imports:

```text
portfolio
risk
paper_trading
monitoring
```

Forbidden imports:

```text
execution
research
```

---

## Layer 11

### dashboard

Allowed imports:

```text
services
```

Preferred:

```python
from services.portfolio_service import PortfolioService
```

Not:

```python
from risk.risk_engine import RiskEngine
```

Dashboard should never call engines directly.

---

# Target Service Layer

```text
dashboard
    │
    ▼
services
    │
    ▼
portfolio
risk
execution
signals
research
```

---

# Forbidden Dependencies

The following dependencies are prohibited.

```text
risk → dashboard
portfolio → dashboard
execution → dashboard
monitoring → dashboard
```

```text
dashboard → risk_engine
dashboard → execution_engine
dashboard → portfolio_engine
```

```text
execution → research
execution → dashboard
```

```text
risk → monitoring
```

---

# Circular Dependency Prevention

Never create:

```text
A → B
B → A
```

Examples:

Bad:

```text
portfolio
    ↓
risk

risk
    ↓
portfolio
```

Good:

```text
portfolio
    ↓
risk
```

One direction only.

---

# Dependency Validation Checklist

Before merging code:

- Does this create a new dependency?
- Is that dependency allowed?
- Does it introduce circular references?
- Can it be moved into services instead?
- Does it violate module ownership?

If any answer is yes, refactor before merging.

---

# Long-Term Architecture

```text
Dashboard
     │
     ▼
Service Layer
     │
     ▼
Research
Signals
Portfolio
Risk
Execution
Monitoring
     │
     ▼
Core Infrastructure
     │
     ▼
Data Layer
```

This architecture is the target state for Institutional Quant Platform.
