from DataManager import DataManager
from concurrent.futures import ThreadPoolExecutor

class MultiThreadScrape(object):
    def __init__(self):
        # Define the number of threads to use
        self.num_threads = 4
        self.data_Controller = DataManager()
            
    # Function to perform a task
    def process_task(self, company):
       return self.data_Controller.collect_Fundamental_Data(company)

    # Function to create and start threads for each task
    def process_tasks_with_threads(self):
        comp_dict = self.data_Controller.company_list()
        company_list_flattened = [item for sublist in comp_dict.values() for item in sublist]

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            results = executor.map(self.process_task, company_list_flattened)