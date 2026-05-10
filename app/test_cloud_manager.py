import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from cloud.cloud_manager import (
    CloudManager
)

# =====================================================
# CLOUD MANAGER
# =====================================================

cloud = CloudManager()

# =====================================================
# REGISTER NODES
# =====================================================

cloud.register_node(

    "GPU-Node-1",

    cpu=32,

    memory="128GB"
)

cloud.register_node(

    "CPU-Node-1",

    cpu=16,

    memory="64GB"
)

# =====================================================
# DEPLOY WORKLOADS
# =====================================================

cloud.deploy_workload(

    "TransformerForecasting",

    "GPU-Node-1"
)

cloud.deploy_workload(

    "DistributedAI",

    "CPU-Node-1"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nCLOUD NODE SUMMARY\n")

print(

    cloud.node_summary()
)

print("\nDEPLOYMENT SUMMARY\n")

print(

    cloud.deployment_summary()
)