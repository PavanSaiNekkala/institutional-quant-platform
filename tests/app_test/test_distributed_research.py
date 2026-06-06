import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from research.distributed_research import (
    DistributedResearch
)

# =====================================================
# SYMBOLS
# =====================================================

from core.universe_loader import (
    load_ranked_universe
)

symbols = load_ranked_universe(

    top_n=25
)

# =====================================================
# RESEARCH
# =====================================================

engine = DistributedResearch()

results = engine.run_research(

    symbols,

    workers=4
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nDISTRIBUTED RESEARCH RESULTS\n"
)

print(results)
