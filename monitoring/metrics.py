from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    start_http_server
)

import time

# =========================================================
# METRICS
# =========================================================

scan_counter = Counter(

    "institutional_scans_total",

    "Total institutional scans"
)

scan_latency = Histogram(

    "institutional_scan_latency_seconds",

    "Institutional scan latency"
)

active_positions = Gauge(

    "institutional_active_positions",

    "Active portfolio positions"
)

system_health = Gauge(

    "institutional_system_health",

    "System health score"
)

# =========================================================
# START METRICS SERVER
# =========================================================

def start_metrics_server(

    port=8000
):

    start_http_server(port)

    print(

        f"\nPROMETHEUS METRICS ACTIVE "

        f"ON PORT {port}"
    )

# =========================================================
# RECORD SCAN
# =========================================================

def record_scan():

    scan_counter.inc()

# =========================================================
# RECORD LATENCY
# =========================================================

def record_latency(

    duration
):

    scan_latency.observe(

        duration
    )

# =========================================================
# UPDATE POSITIONS
# =========================================================

def update_positions(

    positions
):

    active_positions.set(

        positions
    )

# =========================================================
# UPDATE HEALTH
# =========================================================

def update_health(

    score
):

    system_health.set(

        score
    )
