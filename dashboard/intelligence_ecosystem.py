import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Intelligence Ecosystem",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Institutional Intelligence Ecosystem"
)

# =========================================================
# SYSTEM METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(

    "AI Services",

    12
)

col2.metric(

    "Distributed Nodes",

    4
)

col3.metric(

    "Active Workflows",

    9
)

col4.metric(

    "System Health",

    "OPTIMAL"
)

# =========================================================
# AI SIGNALS
# =========================================================

st.subheader(

    "AI Forecast Signals"
)

signals = pd.DataFrame({

    "Model": [

        "EnsembleAI",
        "RegimeAI",
        "LSTM",
        "Transformer",
        "RL-Agent"
    ],

    "Signal": [

        0.14,
        0.09,
        0.18,
        0.11,
        0.05
    ]
})

fig = go.Figure()

fig.add_trace(

    go.Bar(

        x=signals["Model"],

        y=signals["Signal"]
    )
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# =========================================================
# CLOUD INFRASTRUCTURE
# =========================================================

st.subheader(

    "Cloud Infrastructure"
)

cloud = pd.DataFrame({

    "Node": [

        "GPU-Node-1",
        "GPU-Node-2",
        "CPU-Node-1",
        "CPU-Node-2"
    ],

    "CPU Utilization": [

        78,
        65,
        49,
        58
    ],

    "Memory Utilization": [

        81,
        70,
        42,
        55
    ]
})

st.dataframe(

    cloud,

    use_container_width=True
)

# =========================================================
# GOVERNANCE EVENTS
# =========================================================

st.subheader(

    "Governance Events"
)

events = pd.DataFrame({

    "Timestamp": [

        "09:00",
        "09:15",
        "09:30",
        "09:45"
    ],

    "Event": [

        "TransformerAI deployed",
        "Risk pipeline executed",
        "Audit record created",
        "Multi-agent orchestration updated"
    ]
})

st.dataframe(

    events,

    use_container_width=True
)

# =========================================================
# WORKFLOW STATUS
# =========================================================

st.subheader(

    "Workflow Status"
)

workflow = pd.DataFrame({

    "Workflow": [

        "DailyForecast",
        "RiskMonitoring",
        "PortfolioOptimization",
        "GovernanceAudit"
    ],

    "Status": [

        "RUNNING",
        "RUNNING",
        "ACTIVE",
        "ACTIVE"
    ]
})

st.dataframe(

    workflow,

    use_container_width=True
)

# =========================================================
# SYSTEM HEALTH
# =========================================================

st.success(

    "Institutional Intelligence Ecosystem Operational"
)