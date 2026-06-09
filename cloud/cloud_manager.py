from datetime import datetime

import pandas as pd

# =========================================================
# CLOUD MANAGER
# =========================================================


class CloudManager:
    def __init__(self):

        self.nodes = {}

        self.deployments = []

    # =====================================================
    # REGISTER NODE
    # =====================================================

    def register_node(self, node_name, cpu, memory):

        self.nodes[node_name] = {
            "CPU": cpu,
            "Memory": memory,
            "Status": "ACTIVE",
            "Registered": datetime.now(),
        }

    # =====================================================
    # DEPLOY WORKLOAD
    # =====================================================

    def deploy_workload(self, workload_name, node_name):

        deployment = {
            "Workload": workload_name,
            "Node": node_name,
            "Timestamp": datetime.now(),
            "Status": "RUNNING",
        }

        self.deployments.append(deployment)

    # =====================================================
    # NODE SUMMARY
    # =====================================================

    def node_summary(self):

        return pd.DataFrame(self.nodes).T

    # =====================================================
    # DEPLOYMENT SUMMARY
    # =====================================================

    def deployment_summary(self):

        return pd.DataFrame(self.deployments)
