import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from research.research_lab import (
    ResearchLab
)

# =====================================================
# RESEARCH LAB
# =====================================================

lab = ResearchLab()

# =====================================================
# REGISTER EXPERIMENTS
# =====================================================

lab.register_experiment(

    name="TransformerMomentum",

    hypothesis="Transformer attention improves momentum forecasting",

    model="TransformerAI",

    metric="Sharpe Ratio"
)

lab.register_experiment(

    name="RLAllocation",

    hypothesis="RL improves adaptive allocation efficiency",

    model="ReinforcementLearning",

    metric="Max Drawdown"
)

lab.register_experiment(

    name="EnsembleAlpha",

    hypothesis="Ensemble models improve signal robustness",

    model="EnsembleAI",

    metric="Information Ratio"
)

# =====================================================
# UPDATE STATUS
# =====================================================

lab.update_status(

    "RLAllocation",

    "COMPLETED"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nRESEARCH SUMMARY\n")

print(

    lab.research_summary()
)

print("\nACTIVE EXPERIMENTS\n")

print(

    lab.active_experiments()
)