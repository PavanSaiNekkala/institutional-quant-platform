# Institutional Quant Platform

Version: 1.0
Last Updated: YYYY-MM-DD
Owner: Quant Platform

# Data Contract

This document defines:

- Data Producers
- Data Consumers
- Mandatory Columns
- Generated Columns

Any change to a file schema must be updated here.

---

## updated_stocks.xlsx

Producer

analytics/utilities/updated_stocks.py

Consumers

analytics/utilities/generate_metadata.py

Mandatory Columns

- Symbol
- Close
- VOLATILITY_PCT
- History_Days
- Market_Cap

---

## stock_metadata.csv

Producer

analytics/utilities/generate_metadata.py

Consumers

analytics/ranking/factor_model.py
analytics/utilities/updated_stocks.py

Mandatory Columns

- Symbol
- Sector
- Industry
- Market_Cap

---

## factor_model_rankings.csv

Producer

analytics/ranking/factor_model.py

Consumers

analytics/alpha/conviction_engine.py
analytics/alpha/expected_return_engine.py
analytics/attribution/factor_attribution_engine.py

Mandatory Columns

- Symbol
- FACTOR_MOMENTUM
- FACTOR_SHARPE
- FACTOR_ALPHA
- FACTOR_RS
- FACTOR_SECTOR
- FACTOR_ENTRY
- FACTOR_LIQUIDITY
- MULTI_FACTOR_SCORE

---

## conviction_scores.csv

Producer

analytics/alpha/conviction_engine.py

Consumers

analytics/research/correlation_engine.py

Mandatory Columns

- Symbol
- CONVICTION
- CONVICTION_SCORE

---

## expected_returns.csv

Producer

analytics/alpha/expected_return_engine.py

Consumers

analytics/portfolio/risk_parity_engine.py
analytics/portfolio/portfolio_optimiser.py
analytics/attribution/factor_attribution_engine.py

Mandatory Columns

- Symbol
- EXPECTED_RETURN_30D

---

## position_sized_portfolio.csv

Producer

analytics/portfolio/position_sizing_engine.py

Consumers

analytics/portfolio/risk_parity_engine.py

Mandatory Columns

- Symbol
- MULTI_FACTOR_SCORE
- ENTRY_SCORE
- TARGET_WEIGHT

---

## risk_parity_portfolio.csv

Producer

analytics/portfolio/risk_parity_engine.py

Consumers

analytics/portfolio/portfolio_optimiser.py
analytics/attribution/factor_attribution_engine.py

Mandatory Columns

- Symbol
- VOLATILITY
- FINAL_WEIGHT
- MULTI_FACTOR_SCORE
- ENTRY_SCORE

Planned Columns
- CONVICTION_SCORE
- EXPECTED_RETURN_30D

---

## optimised_portfolio.csv

Producer

analytics/portfolio/portfolio_optimiser.py

Consumers

analytics/attribution/factor_attribution_engine.py

Mandatory Columns

- Symbol
- OPT_WEIGHT
- OPT_WEIGHT_%

## risk_metrics.csv

Producer

analytics/portfolio/risk_metrics_engine.py

Consumers

analytics/portfolio/portfolio_monitor_engine.py
analytics/portfolio/portfolio_intelligence.py
analytics/monitoring/performance_analytics_engine.py
analytics/utilities/monthly_factsheet_generator.py

Mandatory Columns

- Metric
- Value

## liquidity_scores.csv

Producer

analytics/research/liquidity_engine.py

Consumers

analytics/ranking/factor_model.py
analytics/research/capacity_analysis_engine.py

Mandatory Columns

- Symbol
- Close
- AVG_VOLUME_30D
- ADV
- LIQUIDITY_SCORE

## sector_controlled_portfolio.csv
Producer
analytics/portfolio/sector_exposure_engine.py

Consumers
analytics/portfolio/position_sizing_engine.py

## portfolio_allocation.csv
Producer
analytics/portfolio/portfolio_constructor.py

Consumers
analytics/portfolio/rebalance_engine.py

updated_stocks
    ↓
generate_metadata
    ↓
factor_model
    ↓
conviction_engine
    ↓
expected_return_engine
    ↓
position_sizing_engine
    ↓
risk_parity_engine
    ↓
portfolio_optimiser
    ↓
portfolio_var
    ↓
beta_engine
    ↓
concentration_risk
    ↓
risk_metrics_engine
    ↓
factor_attribution_engine
    ↓
portfolio_monitor_engine
    ↓
portfolio_intelligence
    ↓
monthly_factsheet_generator
