import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

from portfolio.exposure_heatmap import (
    ExposureHeatmap
)

# =====================================================
# LOAD POSITIONS
# =====================================================

engine = PaperTradingEngine()

report = engine.report()

# =====================================================
# EXPOSURE ENGINE
# =====================================================

heatmap = ExposureHeatmap(

    report["Positions"]
)

df = heatmap.position_values()

metrics = heatmap.concentration_metrics(

    df
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nPORTFOLIO EXPOSURE\n"
)

print(df)

print(

    "\nCONCENTRATION METRICS\n"
)

print(metrics)