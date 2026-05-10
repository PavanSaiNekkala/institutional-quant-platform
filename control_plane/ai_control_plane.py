from datetime import datetime
import pandas as pd

# =========================================================
# AI CONTROL PLANE
# =========================================================

class AIControlPlane:

    def __init__(self):

        self.systems = {}

        self.events = []

    # =====================================================
    # REGISTER SYSTEM
    # =====================================================

    def register_system(

        self,

        name,

        status="ACTIVE"
    ):

        self.systems[name] = {

            "status":

                status,

            "registered_at":

                datetime.now()
        }

        self.log_event(

            f"{name} registered"
        )

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    def update_status(

        self,

        name,

        status
    ):

        if name in self.systems:

            self.systems[name][

                "status"

            ] = status

            self.log_event(

                f"{name} status updated to {status}"
            )

    # =====================================================
    # LOG EVENT
    # =====================================================

    def log_event(

        self,

        message
    ):

        self.events.append({

            "timestamp":

                datetime.now(),

            "event":

                message
        })

    # =====================================================
    # SYSTEM SUMMARY
    # =====================================================

    def system_summary(self):

        return pd.DataFrame(

            self.systems
        ).T

    # =====================================================
    # EVENT LOG
    # =====================================================

    def event_log(self):

        return pd.DataFrame(

            self.events
        )