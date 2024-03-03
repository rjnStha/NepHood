from concurrent.futures import ThreadPoolExecutor

class MultiThread(object):
    _NUM_THREADS = 6

    def __init__(self, func):
        self.func = func

    # Function to create and start threads for each task
    def process_tasks_with_threads(self, list):
        with ThreadPoolExecutor(max_workers = self._NUM_THREADS) as executor:
            results = executor.map(self.func, list)
        return results