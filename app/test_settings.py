import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from config.settings import (
    config_summary
)

# =====================================================
# OUTPUT
# =====================================================

print("\nCONFIGURATION SETTINGS\n")

for k, v in config_summary().items():

    print(f"{k}: {v}")