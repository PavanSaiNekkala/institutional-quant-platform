import queue
import threading
import time

# =========================================================
# TASK QUEUE
# =========================================================

class TaskQueue:

    def __init__(self):

        self.queue = queue.Queue()

        self.results = []

        self.running = False

    # =====================================================
    # ADD TASK
    # =====================================================

    def add_task(

        self,

        func,

        *args,

        **kwargs
    ):

        self.queue.put(

            (

                func,
                args,
                kwargs
            )
        )

    # =====================================================
    # WORKER
    # =====================================================

    def worker(self):

        while self.running:

            try:

                func, args, kwargs = self.queue.get(

                    timeout=1
                )

                result = func(

                    *args,

                    **kwargs
                )

                self.results.append(

                    result
                )

                self.queue.task_done()

            except queue.Empty:

                continue

            except Exception as e:

                print(

                    f"TASK ERROR: {e}"
                )

    # =====================================================
    # START WORKERS
    # =====================================================

    def start_workers(

        self,

        num_workers=4
    ):

        self.running = True

        self.threads = []

        for _ in range(num_workers):

            thread = threading.Thread(

                target=self.worker,

                daemon=True
            )

            thread.start()

            self.threads.append(thread)

    # =====================================================
    # STOP WORKERS
    # =====================================================

    def stop_workers(self):

        self.running = False

    # =====================================================
    # WAIT
    # =====================================================

    def wait_completion(self):

        self.queue.join()