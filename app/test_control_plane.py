import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from control_plane.ai_control_plane import (
    AIControlPlane
)

# =====================================================
# CONTROL PLANE
# =====================================================

cp = AIControlPlane()

# =====================================================
# REGISTER SYSTEMS
# =====================================================

cp.register_system(

    "EnsembleAI"
)

cp.register_system(

    "RegimeAI"
)

cp.register_system(

    "LSTMForecast"
)

cp.register_system(

    "TransformerAI"
)

cp.register_system(

    "MultiAgentAI"
)

# =====================================================
# UPDATE STATUS
# =====================================================

cp.update_status(

    "TransformerAI",

    "MONITORING"
)

# =====================================================
# SUMMARY
# =====================================================

print("\nAI SYSTEM SUMMARY\n")

print(

    cp.system_summary()
)

# =====================================================
# EVENTS
# =====================================================

print("\nCONTROL PLANE EVENTS\n")

print(

    cp.event_log()
)