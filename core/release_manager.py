from datetime import datetime
from pathlib import Path

# =========================================================
# VERSION FILE
# =========================================================

VERSION_FILE = "VERSION"

# =========================================================
# READ VERSION
# =========================================================

def current_version():

    with open(

        VERSION_FILE,

        "r"
    ) as f:

        return f.read().strip()

# =========================================================
# RELEASE METADATA
# =========================================================

def release_metadata():

    return {

        "Version":

            current_version(),

        "Release Date":

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Platform":

            "Institutional Quant Platform",

        "Status":

            "Production"
    }

# =========================================================
# DISPLAY RELEASE
# =========================================================

def display_release():

    metadata = release_metadata()

    print("\nENTERPRISE RELEASE")

    for k, v in metadata.items():

        print(f"{k}: {v}")