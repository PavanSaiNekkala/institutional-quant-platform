from datetime import datetime

import pandas as pd

from research.alpha_decay import alpha_decay_analysis
from research.alpha_mining import alpha_report
from research.bayesian_optimization import optimize_strategy
from research.walk_forward import validation_summary, walk_forward_validation

# =========================================================
# RESEARCH PIPELINE
# =========================================================


class ResearchPipeline:
    def __init__(self):

        self.results = []

    # =====================================================
    # RUN PIPELINE
    # =====================================================

    def run_pipeline(self, prices):

        timestamp = datetime.now()

        # =================================================
        # ALPHA MINING
        # =================================================

        alpha = alpha_report(prices)

        # =================================================
        # WALK FORWARD
        # =================================================

        wf_results = walk_forward_validation(prices)

        wf_summary = validation_summary(wf_results)

        # =================================================
        # ALPHA DECAY
        # =================================================

        decay_report, _ = alpha_decay_analysis(prices)

        # =================================================
        # OPTIMIZATION
        # =================================================

        returns = prices.pct_change().dropna()

        optimization = optimize_strategy(returns)

        pipeline_result = {
            "Timestamp": timestamp,
            "Top Alpha Factor": alpha.iloc[0]["Factor"],
            "Top Alpha Score": round(alpha.iloc[0]["Alpha Score"], 4),
            "Average Validation MSE": wf_summary["Average MSE"],
            "Recent IC": decay_report["Recent IC"],
            "Optimization Score": optimization["Best Score"],
        }

        self.results.append(pipeline_result)

        return pipeline_result

    # =====================================================
    # PIPELINE HISTORY
    # =====================================================

    def pipeline_history(self):

        return pd.DataFrame(self.results)
