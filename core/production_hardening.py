import time
import logging
from functools import wraps

# =========================================================
# LOGGING CONFIG
# =========================================================

logging.basicConfig(

    filename="institutional_platform.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# SAFE EXECUTION DECORATOR
# =========================================================

def safe_execution(

    retries=3,

    delay=2
):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(retries):

                try:

                    result = func(

                        *args,

                        **kwargs
                    )

                    logging.info(

                        f"{func.__name__} SUCCESS"
                    )

                    return result

                except Exception as e:

                    last_exception = e

                    logging.error(

                        f"{func.__name__} FAILED "

                        f"Attempt {attempt+1} "

                        f"| Error: {e}"
                    )

                    time.sleep(delay)

            logging.critical(

                f"{func.__name__} TOTAL FAILURE"
            )

            return None

        return wrapper

    return decorator

# =========================================================
# CENTRALIZED LOGGER
# =========================================================

class InstitutionalLogger:

    @staticmethod
    def info(message):

        logging.info(message)

    @staticmethod
    def warning(message):

        logging.warning(message)

    @staticmethod
    def error(message):

        logging.error(message)

    @staticmethod
    def critical(message):

        logging.critical(message)