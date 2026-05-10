import logging
from pathlib import Path

# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = Path(

    "logs"
)

LOG_DIR.mkdir(

    exist_ok=True
)

LOG_FILE = LOG_DIR / "institutional_quant.log"

# =========================================================
# LOGGER CONFIG
# =========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(

        "%(asctime)s | "

        "%(levelname)s | "

        "%(message)s"
    ),

    handlers=[

        logging.FileHandler(LOG_FILE),

        logging.StreamHandler()
    ]
)

logger = logging.getLogger(

    "InstitutionalQuant"
)

# =========================================================
# INFO LOG
# =========================================================

def log_info(

    message
):

    logger.info(message)

# =========================================================
# WARNING LOG
# =========================================================

def log_warning(

    message
):

    logger.warning(message)

# =========================================================
# ERROR LOG
# =========================================================

def log_error(

    message
):

    logger.error(message)

# =========================================================
# CRITICAL LOG
# =========================================================

def log_critical(

    message
):

    logger.critical(message)