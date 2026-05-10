import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from config.platform_config import (
    PLATFORM_CONFIG
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nPLATFORM CONFIGURATION\n"
)

print(

    PLATFORM_CONFIG
)