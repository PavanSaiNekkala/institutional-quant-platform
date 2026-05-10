import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from research.experiment_db import (

    initialize_db,
    insert_experiment,
    load_experiments,
    update_status
)

# =====================================================
# INITIALIZE
# =====================================================

initialize_db()

# =====================================================
# INSERT EXPERIMENTS
# =====================================================

insert_experiment(

    "TransformerAlpha",

    "TransformerAI",

    1.82
)

insert_experiment(

    "RLAllocation",

    "ReinforcementLearning",

    1.34
)

insert_experiment(

    "EnsembleMomentum",

    "EnsembleAI",

    1.56
)

# =====================================================
# UPDATE STATUS
# =====================================================

update_status(

    2,

    "COMPLETED"
)

# =====================================================
# LOAD
# =====================================================

df = load_experiments()

# =====================================================
# OUTPUT
# =====================================================

print("\nEXPERIMENT DATABASE\n")

print(df)