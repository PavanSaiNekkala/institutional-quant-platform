import sys
import time

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.task_queue import (
    TaskQueue
)

# =====================================================
# SAMPLE TASK
# =====================================================

def sample_task(x):

    time.sleep(1)

    return x * 2

# =====================================================
# QUEUE
# =====================================================

queue = TaskQueue()

queue.start_workers(

    num_workers=4
)

# =====================================================
# ADD TASKS
# =====================================================

for i in range(10):

    queue.add_task(

        sample_task,

        i
    )

# =====================================================
# WAIT
# =====================================================

queue.wait_completion()

queue.stop_workers()

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nTASK RESULTS\n"
)

print(

    queue.results
)
