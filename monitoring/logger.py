import logging
import os

# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = "logs"

os.makedirs(

    LOG_DIR,

    exist_ok=True
)

# =========================================================
# LOGGER CONFIG
# =========================================================

logging.basicConfig(

    filename=os.path.join(

        LOG_DIR,

        "institutional.log"
    ),

    level=logging.INFO,

    format=(

        "%(asctime)s | "

        "%(levelname)s | "

        "%(message)s"
    )
)

# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger(

    "institutional_quant"
)

# =========================================================
# LOG HELPERS
# =========================================================

def log_info(message):

    logger.info(message)

def log_warning(message):

    logger.warning(message)

def log_error(message):

    logger.error(message)