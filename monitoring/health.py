import psutil
import platform
from datetime import datetime

# =========================================================
# CPU USAGE
# =========================================================

def cpu_usage():

    return psutil.cpu_percent()

# =========================================================
# MEMORY USAGE
# =========================================================

def memory_usage():

    memory = psutil.virtual_memory()

    return memory.percent

# =========================================================
# DISK USAGE
# =========================================================

def disk_usage():

    disk = psutil.disk_usage("/")

    return disk.percent

# =========================================================
# SYSTEM INFO
# =========================================================

def system_info():

    return {

        "OS":
            platform.system(),

        "Release":
            platform.release(),

        "Machine":
            platform.machine()
    }

# =========================================================
# HEALTH SNAPSHOT
# =========================================================

def health_snapshot():

    return {

        "Timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "CPU":
            cpu_usage(),

        "Memory":
            memory_usage(),

        "Disk":
            disk_usage(),

        "System":
            system_info()
    }