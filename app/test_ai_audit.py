import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from governance.ai_audit import (

    log_ai_decision,
    load_audit,
    list_audits
)

# =====================================================
# SAMPLE AI OUTPUT
# =====================================================

decision = {

    "Symbol":

        "RELIANCE.NS",

    "Decision":

        "BUY",

    "Confidence":

        0.84,

    "Regime":

        "BULL"
}

# =====================================================
# LOG DECISION
# =====================================================

filepath = log_ai_decision(

    "InstitutionalAI",

    decision
)

print("\nAUDIT FILE CREATED\n")

print(filepath)

# =====================================================
# LOAD AUDIT
# =====================================================

audit = load_audit(

    filepath
)

print("\nLOADED AUDIT\n")

print(audit)

# =====================================================
# LIST AUDITS
# =====================================================

print("\nAVAILABLE AUDITS\n")

for file in list_audits():

    print(file)