from DataCollector import DataCollector
from MachineLearningModels.LinearRegressionModel import LinearRegressionModel 

company = "nica"
data_Controller = DataCollector()
data_Controller.collect_Financial_News_Data(company)
data_Controller.collect_Fundamental_Data(company)
data_Controller.collect_Technical_Data(company)
data_Controller.collect_Macroeconomic_Data()

linear_Regression = LinearRegressionModel()
linear_Regression._run(company)