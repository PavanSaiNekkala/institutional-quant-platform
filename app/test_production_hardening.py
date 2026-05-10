import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.production_hardening import (

    safe_execution,
    InstitutionalLogger
)

# =====================================================
# TEST FUNCTION
# =====================================================

@safe_execution(

    retries=3,

    delay=1
)

def unstable_function():

    x = 1 / 0

    return x

# =====================================================
# RUN TEST
# =====================================================

result = unstable_function()

print(

    "\nRESULT\n"
)

print(result)

InstitutionalLogger.info(

    "Production hardening operational."
)
