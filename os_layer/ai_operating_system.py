from datetime import datetime
import pandas as pd

# =========================================================
# AI OPERATING SYSTEM
# =========================================================

class AIOperatingSystem:

    def __init__(self):

        self.services = {}

        self.workflows = []

        self.system_health = "HEALTHY"

    # =====================================================
    # REGISTER SERVICE
    # =====================================================

    def register_service(

        self,

        service_name,

        category
    ):

        self.services[service_name] = {

            "Category":

                category,

            "Status":

                "ACTIVE",

            "Registered":

                datetime.now()
        }

    # =====================================================
    # START WORKFLOW
    # =====================================================

    def start_workflow(

        self,

        workflow_name
    ):

        workflow = {

            "Workflow":

                workflow_name,

            "Status":

                "RUNNING",

            "Timestamp":

                datetime.now()
        }

        self.workflows.append(

            workflow
        )

    # =====================================================
    # UPDATE SYSTEM HEALTH
    # =====================================================

    def update_health(

        self,

        status
    ):

        self.system_health = status

    # =====================================================
    # SERVICE SUMMARY
    # =====================================================

    def service_summary(self):

        return pd.DataFrame(

            self.services
        ).T

    # =====================================================
    # WORKFLOW SUMMARY
    # =====================================================

    def workflow_summary(self):

        return pd.DataFrame(

            self.workflows
        )

    # =====================================================
    # OS STATUS
    # =====================================================

    def os_status(self):

        return {

            "System Health":

                self.system_health,

            "Services":

                len(self.services),

            "Workflows":

                len(self.workflows)
        }