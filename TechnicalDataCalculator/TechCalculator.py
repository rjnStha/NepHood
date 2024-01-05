
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Graph with Plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

import yfinance as yf

class TechCalculator(object):
    def __init__(self):
        return
    
    # Convert dict to dataframe and make consumable to panda_ta lib 
    def preprocess_fundamental_data(self, fundamental_dict):

        # Create DataFrame object from Dict
        fundamental_dataframe = pd.DataFrame.from_dict(fundamental_dict)
        # Set Date as the index of the DataFrame
        fundamental_dataframe.set_index('date',inplace=True)
        
        # NOTE Sort Index with oldest date top of the order since
        #       pandas_ta uses exponential moving average (EMA) that gives higher weighting to recent prices
        fundamental_dataframe = fundamental_dataframe.sort_index(ascending=True)
        # To filter the data with specific date --> fundamental_dataframe.loc['2013-07-14':'2019-02-22']

        return fundamental_dataframe
    
    # Calculate Moving Average Convergence Divergence (MACD)
    def calculate_MACD(self, fundamental_dict):
        df = self.preprocess_fundamental_data(fundamental_dict)

        # Calculate MACD values using the pandas_ta library
        # MACD Line = (12-day EMA - 26-day EMA)
        # Signal Line = 9-day EMA of MACD Line
        # MACD Histogram = MACD Line - Signal Line
        df.ta.macd(close='ltp', fast=12, slow=26, signal=9, append=True)
        
        # Plot MACD graph
        # self.plot_MACD_Graph(fundamental_dataframe)
        
        # Remove unwanted data columns
        # List of columns to remove
        columns_to_remove = ["high","low","ltp","open","volume"]
        df = df.drop(columns=columns_to_remove)

        # Reset the index to include Date as data and return as dictionary of list
        return df.reset_index().to_dict(orient='list')
     
    # Relative Strength Index (RSI)
    # Sliding window algorithm
    # NOTE panda_ta calculates RSI using  Exponentially Weighted Moving Average (EWM) instead of
    #   Wilder-approved Simple Moving Average (SMA), EWM gives higher weight to recent data  
    def calculate_RSI(self, fundamental_dict):
        df = self.preprocess_fundamental_data(fundamental_dict)

        # Calculate the RSI where length = lookback period in days
        df.ta.rsi(close='ltp', length=14, append=True)

        # Plot RSI graph
        self.plot_RSI_Graph(df)

        # Remove unwanted data columns
        # List of columns to remove
        columns_to_remove = ["high","low","ltp","open","volume"]
        df = df.drop(columns=columns_to_remove)

        # Reset the index to include Date as data and return as dictionary of list
        return df.reset_index().to_dict(orient='list')
   
    # Calculate Average True Range (ATR)
    def calculate_ATR(self):
        return
   
    # Money Flow Index (MFI)
    def calculate_MFI(self):
        return
    
    # Visualize MACD with Plotly
    def plot_MACD_Graph(self, fundamental_dataframe):
        # Visualize MACD with Plotly
        # Force lowercase (optional)
        fundamental_dataframe.columns = [x.lower() for x in fundamental_dataframe.columns]
        
        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=2, cols=1)

        # price Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['open'],
                line=dict(color='#ff9900', width=1),
                name='open',
                # showlegend=False,
                legendgroup='1',
            ), row=1, col=1
        )

        # Candlestick chart for pricing
        fig.append_trace(
            go.Candlestick(
                x=fundamental_dataframe.index,
                open=fundamental_dataframe['open'],
                high=fundamental_dataframe['high'],
                low=fundamental_dataframe['low'],
                close=fundamental_dataframe['ltp'],
                increasing_line_color='#ff9900',
                decreasing_line_color='black',
                showlegend=False
            ), row=1, col=1
        )

        # Fast Signal (%k)
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macd_12_26_9'],
                line=dict(color='#ff9900', width=2),
                name='macd',
                # showlegend=False,
                legendgroup='2',
            ), row=2, col=1
        )
        
        # Slow signal (%d)
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macds_12_26_9'],
                line=dict(color='#000000', width=2),
                # showlegend=False,
                legendgroup='2',
                name='signal'
            ), row=2, col=1
        )
        # Colorize the histogram values
        colors = np.where(fundamental_dataframe['macdh_12_26_9'] < 0, '#000', '#ff9900')
        # Plot the histogram
        fig.append_trace(
            go.Bar(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macdh_12_26_9'],
                name='histogram',
                marker_color=colors,
            ), row=2, col=1
        )

        # Make it pretty
        layout = go.Layout(
            plot_bgcolor='#efefef',
            # Font Families
            font_family='Monospace',
            font_color='#000000',
            font_size=20,
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                )
            )
        )

        # Update options and show plot
        fig.update_layout(layout)
        fig.show()
    
    # Visualize RSI with Plotly
    def plot_RSI_Graph(self, fundamental_dataframe):

        # Create Figure
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.25, 0.75])
        
        # Create Candlestick chart for price data
        fig.add_trace(go.Candlestick(
            x = fundamental_dataframe.index,
            open = fundamental_dataframe['open'],
            high = fundamental_dataframe['high'],
            low = fundamental_dataframe['low'],
            close = fundamental_dataframe['ltp'],
            increasing_line_color = '#ff9900',
            decreasing_line_color = 'black',
            showlegend = False
        ), row=1, col=1)
        
        
        # Make RSI Plot
        fig.add_trace(go.Scatter(
            x=fundamental_dataframe.index,
            y=fundamental_dataframe['RSI_14'],
            line=dict(color='#ff9900', width=2),
            showlegend=False,
        ), row=2, col=1)

        # Add upper/lower bounds
        fig.update_yaxes(range=[-10, 110], row=2, col=1)
        fig.add_hline(y=0, col=1, row=2, line_color="#666", line_width=2)
        fig.add_hline(y=100, col=1, row=2, line_color="#666", line_width=2)

        # Add overbought/oversold
        fig.add_hline(y=30, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash')
        fig.add_hline(y=70, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash')

        # Customize font, colors, hide range slider
        layout = go.Layout(
            plot_bgcolor='#efefef',
            # Font Families
            font_family='Monospace',
            font_color='#000000',
            font_size=20,
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                )
            )
        )
        # update and display
        fig.update_layout(layout)
        fig.show()

        return