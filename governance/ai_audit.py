import json
from pathlib import Path
from datetime import datetime

# =========================================================
# AUDIT DIRECTORY
# =========================================================

AUDIT_DIR = Path(

    "audit_logs"
)

AUDIT_DIR.mkdir(

    exist_ok=True
)

# =========================================================
# LOG AI DECISION
# =========================================================

def log_ai_decision(

    system_name,

    decision_data
):

    timestamp = datetime.now().strftime(

        "%Y%m%d_%H%M%S"
    )

    filename = (

        AUDIT_DIR

        / f"{system_name}_{timestamp}.json"
    )

    audit_record = {

        "timestamp":

            timestamp,

        "system":

            system_name,

        "decision":

            decision_data
    }

    with open(

        filename,

        "w"
    ) as f:

        json.dump(

            audit_record,

            f,

            indent=4,

            default=str
        )

    return filename

# =========================================================
# LOAD AUDIT FILE
# =========================================================

def load_audit(

    filepath
):

    with open(

        filepath,

        "r"
    ) as f:

        return json.load(f)

# =========================================================
# LIST AUDIT FILES
# =========================================================

def list_audits():

    return list(

        AUDIT_DIR.glob("*.json")
    )