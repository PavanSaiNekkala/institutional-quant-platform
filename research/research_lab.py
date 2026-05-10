from datetime import datetime
import pandas as pd

# =========================================================
# RESEARCH LAB
# =========================================================

class ResearchLab:

    def __init__(self):

        self.experiments = []

    # =====================================================
    # REGISTER EXPERIMENT
    # =====================================================

    def register_experiment(

        self,

        name,

        hypothesis,

        model,

        metric
    ):

        experiment = {

            "Experiment":

                name,

            "Hypothesis":

                hypothesis,

            "Model":

                model,

            "Metric":

                metric,

            "Timestamp":

                datetime.now(),

            "Status":

                "ACTIVE"
        }

        self.experiments.append(

            experiment
        )

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    def update_status(

        self,

        experiment_name,

        status
    ):

        for exp in self.experiments:

            if exp["Experiment"] == experiment_name:

                exp["Status"] = status

    # =====================================================
    # RESEARCH SUMMARY
    # =====================================================

    def research_summary(self):

        return pd.DataFrame(

            self.experiments
        )

    # =====================================================
    # ACTIVE EXPERIMENTS
    # =====================================================

    def active_experiments(self):

        active = [

            e

            for e in self.experiments

            if e["Status"] == "ACTIVE"
        ]

        return pd.DataFrame(active)