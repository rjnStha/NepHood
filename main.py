from DataController import DataController

company = "nica"
data_Controller = DataController()
# print(data_Controller.collect_Financial_News_Data(company))
data_Controller.collect_Fundamental_Data(company)