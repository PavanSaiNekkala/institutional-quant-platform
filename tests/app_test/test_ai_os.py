import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from os_layer.ai_operating_system import (
    AIOperatingSystem
)

# =====================================================
# AI OS
# =====================================================

ai_os = AIOperatingSystem()

# =====================================================
# REGISTER SERVICES
# =====================================================

ai_os.register_service(

    "EnsembleAI",

    "Forecasting"
)

ai_os.register_service(

    "TransformerAI",

    "DeepLearning"
)

ai_os.register_service(

    "MultiAgentAI",

    "Coordination"
)

ai_os.register_service(

    "GovernanceAI",

    "Governance"
)

ai_os.register_service(

    "CloudManager",

    "Infrastructure"
)

# =====================================================
# START WORKFLOWS
# =====================================================

ai_os.start_workflow(

    "DailyForecastPipeline"
)

ai_os.start_workflow(

    "RiskMonitoringPipeline"
)

# =====================================================
# HEALTH
# =====================================================

ai_os.update_health(

    "OPTIMAL"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nAI OPERATING SYSTEM STATUS\n")

print(

    ai_os.os_status()
)

print("\nSERVICE SUMMARY\n")

print(

    ai_os.service_summary()
)

print("\nWORKFLOW SUMMARY\n")

print(

    ai_os.workflow_summary()
)
