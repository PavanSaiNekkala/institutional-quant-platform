import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from risk.regime_detection import (
    RegimeDetector
)

# =====================================================
# ENGINE
# =====================================================

engine = RegimeDetector(

    volatility_threshold=0.25
)

# =====================================================
# DETECT
# =====================================================

result = engine.detect(

    symbol="^NSEI"
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nMARKET REGIME\n"
)

print(result)