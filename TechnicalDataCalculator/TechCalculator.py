import pandas_ta as ta
import pandas as pd

class TechCalculator(object):
    def __init__(self):
        return
    
    # Calculate Moving Average Convergence Divergence (MACD)
    def calculate_MACD(self, fundamental_dict):
        # Create DataFrame object from Dict
        fundamental_dataframe = pd.DataFrame.from_dict(fundamental_dict)
        # Calculate MACD values using the pandas_ta library
        fundamental_dataframe.ta.macd(close='ltp', fast=12, slow=26, signal=9, append=True)
        # View result show all columns
        pd.set_option("display.max_columns", None)
        return fundamental_dataframe
    
    # Calculate Average True Range (ATR)
    def calculate_ATR(self):
        return
    
    #Relative Strength Index (RSI)
    def calculate_RSI(self):
        return
    
    # Money Flow Index (MFI)
    def calculate_MFI(self):
        return