import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from cache.research_cache import (

    initialize_cache,
    save_cache,
    load_cache
)

# =====================================================
# INITIALIZE
# =====================================================

initialize_cache()

# =====================================================
# SAMPLE DATA
# =====================================================

sample_signal = {

    "symbol": "RELIANCE.NS",

    "signal": "BUY",

    "score": 0.87
}

# =====================================================
# SAVE
# =====================================================

save_cache(

    "live_signal_reliance",

    sample_signal
)

# =====================================================
# LOAD
# =====================================================

loaded = load_cache(

    "live_signal_reliance"
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nCACHED RESULT\n"
)

print(loaded)
