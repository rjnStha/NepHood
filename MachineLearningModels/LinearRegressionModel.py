from DataManager import DataManager
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class LinearRegressionModel(object):
    def __init__(self):
        return
    
    def _run(self, company):
        '''
        * Linear Regression Assumptions & Autocorrelation
        * NOTE: 
            Autocorrelation analysis is problematic when extrapolating values for price 
            prediction since dates are not suitable independent variable so we add 
            Technical Indicators as independent variables 
            ==> Multivariate linear regression
        * Drop all the rows where we have NaN values
        '''

        data_Controller = DataManager()

        # Create DataFrame object from fundamental_data dict
        fundamental_dataframe = pd.DataFrame.from_dict(
            data_Controller.collect_Fundamental_Data(company)
            )

        '''
        Fundamental Data and Technical Data Combined Dataframe
        '''
        # Set Date as the index of the DataFrame and sort for uniform data
        fundamental_dataframe.set_index('date',inplace=True)
        fundamental_dataframe.sort_values(by='date', ascending=True, inplace=True)
        # Keep only the 'Adj Close' Value
        fundamental_dataframe = fundamental_dataframe[['ltp']]

        # Get technical data
        technical_data = data_Controller.collect_Technical_Data(company)
        rsi = technical_data["RSI"]
        rsi_dataframe = pd.DataFrame.from_dict(rsi)
        rsi_dataframe.set_index('date',inplace=True)

        df = fundamental_dataframe.combine_first(rsi_dataframe)
        # Drop all NaN values
        df = df.dropna()
        # Get the last 200 datas 
        df = df.tail(200)

        '''
        *********
        '''

        '''
        Test-Train Split the Combined Dataframe
        '''
        # 80/20 Split data into testing and training sets 
        # Common values for test_size range from 0.2 to 0.3
        X = df[['ltp']]
        y = df[['RSI_14']]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        # Test set
        print(X_test.describe())
        # Train set
        print(X_train.describe())

        '''
        *********
        '''

        '''
        Training the Model
        '''
        # Create Regression Model
        model = LinearRegression()
        # Train the model
        model.fit(X_train, y_train)
        # Use model to make predictions
        y_pred = model.predict(X_test)

        '''
        *********
        '''

        '''
        Validating the Fit
        '''
        # Printout relevant metrics
        print("Model Coefficients:", model.coef_)
        print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
        print("Coefficient of Determination:", r2_score(y_test, y_pred))

        # Plot observed values vs predicted values
        plt.scatter(X_test, y_test, color='blue', alpha=0.3, label='Actual data')
        # Plot the linear regression line
        plt.plot(X_test, y_pred, color='black', linewidth=2, label='Linear regression')

        # Plot residuals
        # Calculate residuals
        # print(X_test)
        # print(y_test)
        # print(y_pred)
        count = 0
        for date in X_test.index:
            plt.vlines(X_test.loc[date], y_test.loc[date],y_pred[count] , color='red', linestyle='-', linewidth=1, label="")
            count+=1
            
        plt.xlabel('ltp')
        plt.ylabel('RSI')
        plt.title(f'Linear Regression LTP vs RSI last 200 days {company}')
        plt.legend()
        plt.show()
        '''
        *********
        '''
        return



