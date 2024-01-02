from DataController import DataController


company = "nica"
data_Controller = DataController()
data_Controller.collect_Financial_News_Data(company)
data_Controller.collect_Technical_Data(company)