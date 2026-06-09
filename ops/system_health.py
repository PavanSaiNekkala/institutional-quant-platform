import os
import platform
from datetime import datetime

import pandas as pd
import psutil

# =========================================================
# SYSTEM INFO
# =========================================================


def system_info():

    info = {
        "Platform": platform.system(),
        "Platform Version": platform.version(),
        "Python Version": platform.python_version(),
        "CPU Cores": psutil.cpu_count(),
        "Memory GB": round(psutil.virtual_memory().total / (1024**3), 2),
    }

    return info


# =========================================================
# CPU & MEMORY
# =========================================================


def runtime_metrics():

    metrics = {
        "CPU Usage %": psutil.cpu_percent(),
        "Memory Usage %": psutil.virtual_memory().percent,
        "Disk Usage %": psutil.disk_usage("/").percent,
    }

    return metrics


# =========================================================
# CHECK FILES
# =========================================================


def required_files():

    files = [
        "requirements.txt",
        "dashboard/master_dashboard.py",
        "signals/live_signals.py",
        "portfolio/live_monitor.py",
        "monitoring/alerts.py",
    ]

    results = {}

    for file in files:
        results[file] = os.path.exists(file)

    return results


# =========================================================
# HEALTH REPORT
# =========================================================


def health_report():

    report = {
        "Timestamp": datetime.now(),
        "System Info": system_info(),
        "Runtime Metrics": runtime_metrics(),
        "Required Files": required_files(),
    }

    return report


# =========================================================
# SUMMARY DATAFRAME
# =========================================================


def summary_dataframe():

    metrics = runtime_metrics()

    return pd.DataFrame({"Metric": metrics.keys(), "Value": metrics.values()})
