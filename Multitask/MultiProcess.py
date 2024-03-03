import multiprocessing

class MultiProcess(object):

    def __init__(self, func):
        self.func = func

    # Function to create and start threads for each task
    def process_tasks(self, list):
        
        bootstrap_event = multiprocessing.Event()
        #Start the bootstrap process in a separate process
        bootstrap_process_p = multiprocessing.Process(target=bootstrap_event.set(), args=(bootstrap_event,))
        bootstrap_process_p.start()
        # Wait for the process to bootstrap
        bootstrap_event.wait()

        # Create a multiprocessing Pool with a specified number of processes
        with multiprocessing.Pool() as pool:
            # Map the heavy_calculation function to the chunks of data for parallel processing
            results = pool.map(self.func, list)
        return results
