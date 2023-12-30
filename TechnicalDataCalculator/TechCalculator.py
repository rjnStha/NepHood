import pandas_ta as ta
import pandas as pd

class TechCalculator(object):
    def __init__(self):
        return
    
    # Calculate Moving Average Convergence Divergence (MACD)
    def calculate_MACD(self, dict):
        breakpoint()
        df = pd.DataFrame(dict)
        print(df)
        # Calculate MACD values using the pandas_ta library
        df.ta.macd(close='ltp', fast=12, slow=26, signal=9, append=True)
        # View result
        pd.set_option("display.max_columns", None)  # show all columns
        breakpoint()
    
        return
    
    # Calculate Average True Range (ATR)
    def calculate_ATR(self):
        return
    
    #Relative Strength Index (RSI)
    def calculate_RSI(self):
        return
    
    # Money Flow Index (MFI)
    def calculate_MFI(self):
        return