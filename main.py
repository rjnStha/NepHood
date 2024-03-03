from DataManager import DataManager
from MachineLearningModels.LinearRegressionModel import LinearRegressionModel 
from itertools import chain
from Multitask.MultiThread import MultiThread
from Log.LogHandler import LogHandler
from Firebase.Firebase import FirestoreManager

if __name__ == '__main__':

    # multiThreadScrape = MultiThreadScrape()
    # multiThreadScrape.process_tasks_with_threads()

    data_Controller = DataManager()
    # data_Controller.collect_Financial_News_Data()
    # data_Controller.collect_Fundamental_Data()
    data_Controller.collect_Technical_Data("ACEDPO")
    # ['SHL', 'TRH', 'OHL', 'CGH', 'KDL', 'CITY']
    # log = LogHandler()
    # log.remove_duplicates("InfoLog.log")

    # data_Controller.company_list()
    # data_Controller.deleteCollection("FundamentalData")
    # data_Controller.deleteCollection("FinancialNewsData")

    # data_Controller.collect_Macroeconomic_Data()

    # linear_Regression = LinearRegressionModel()
    # linear_Regression._run(company)

    # comp_dict = data_Controller.company_list()
    # company_list_flattened = [item for sublist in comp_dict.values() for item in sublist]
    # for company in company_list_flattened:
    #     data_Controller.collect_Fundamental_Data(company)