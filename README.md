# Institutional Quant Platform

Institutional-grade quantitative research, portfolio analytics, paper trading, risk intelligence, and operational monitoring platform built using Python, Streamlit, and open-source infrastructure.

---

# Features

## Quantitative Research
- Institutional stock ranking engine
- Factor-based analytics
- Adaptive allocation
- Portfolio optimization
- Regime detection
- Dynamic strategy switching

## Portfolio Infrastructure
- Persistent paper trading engine
- Portfolio analytics
- Exposure intelligence
- Realized & unrealized PnL
- Trade performance analytics
- Portfolio monitoring dashboard

## Risk & Monitoring
- System health monitoring
- Institutional alerts
- Exposure heatmaps
- Concentration analytics
- Operational observability

## Infrastructure
- Market data cache layer
- Automated refresh systems
- Backup & recovery
- Configuration governance
- CI/CD integration
- Dockerized deployment

## Dashboard System
- Multi-page Streamlit dashboard
- Institutional monitoring terminal
- Portfolio control center
- Analytics dashboard
- Regime intelligence dashboard

---

# Architecture

institutional_quant/
│
├── app/
├── automation/
├── backtesting/
├── cache/
├── config/
├── core/
├── dashboard/
├── monitoring/
├── paper_trading/
├── portfolio/
├── reporting/
├── risk/
├── strategy/
├── signals/
├── requirements.txt
├── Dockerfile
└── README.md

---

# Installation

## Clone Repository

```bash
git clone https://github.com/PavanSaiNekkala/institutional-quant-platform.git
```

## Navigate

```bash
cd institutional-quant-platform
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

## Main Platform

```bash
streamlit run dashboard/Home.py
```

## Paper Trading Dashboard

```bash
streamlit run dashboard/paper_trading_dashboard.py
```

---

# Docker Deployment

## Build Image

```bash
docker build -t institutional-quant .
```

## Run Container

```bash
docker run -p 8501:8501 institutional-quant
```

---

# Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- SQLite
- yFinance
- Docker
- GitHub Actions

---

# Future Roadmap

- Real-time execution simulation
- Broker API integration
- Advanced factor models
- ML forecasting enhancements
- Institutional reporting suite
- Cloud deployment infrastructure

---

# Author

Pavan Sai Nekkala

SAP PM Consultant | Quantitative Research & Portfolio Systems Developer