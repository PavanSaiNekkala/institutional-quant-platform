import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import random
import time

from monitoring.metrics import (
    start_metrics_server,
    record_scan,
    record_latency,
    update_positions,
    update_health
)

# =====================================================
# START SERVER
# =====================================================

start_metrics_server(

    port=8000
)

# =====================================================
# SIMULATION LOOP
# =====================================================

print("\nINSTITUTIONAL METRICS ACTIVE")

while True:

    start = time.time()

    # =============================================
    # SIMULATED WORK
    # =============================================

    time.sleep(2)

    duration = time.time() - start

    # =============================================
    # UPDATE METRICS
    # =============================================

    record_scan()

    record_latency(duration)

    update_positions(

        random.randint(5, 25)
    )

    update_health(

        random.uniform(0.80, 1.00)
    )

    print(

        f"Scan completed | "

        f"Latency: {duration:.2f}s"
    )