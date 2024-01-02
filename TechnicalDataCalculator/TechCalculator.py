
import pandas as pd
import pandas_ta as ta

# Graph with Plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

import yfinance as yf

class TechCalculator(object):
    def __init__(self):
        return
    
    # Calculate Moving Average Convergence Divergence (MACD)
    def calculate_MACD(self, fundamental_dict):
        # Create DataFrame object from Dict
        fundamental_dataframe = pd.DataFrame.from_dict(fundamental_dict)
        # Set Date as the index of the DataFrame
        fundamental_dataframe.set_index('date',inplace=True)
        
        # Filter the data with specific date with fundamental_dataframe.loc['2013-07-14':'2019-02-22']
        # NOTE Sort Index with oldest date top of the order since MACD reacts to recent price
        fundamental_dataframe = fundamental_dataframe.sort_index(ascending=True)
        # Remove duplicate Date indices --> Was giving Duplicate Index Error ?????
        fundamental_dataframe = fundamental_dataframe[~fundamental_dataframe.index.duplicated()]

        # Calculate MACD values using the pandas_ta library
        # MACD Line = (12-day EMA - 26-day EMA)
        # Signal Line = 9-day EMA of MACD Line
        # MACD Histogram = MACD Line - Signal Line
        fundamental_dataframe.ta.macd(close='ltp', fast=12, slow=26, signal=9, append=True)
        
        # Plot MACD graph
        # self.plot_MACD_Graph(fundamental_dataframe)
        
        # reset the index to include Date as data and return as dictionary of list
        return fundamental_dataframe.reset_index().to_dict(orient='list')
    
    # Calculate Average True Range (ATR)
    def calculate_ATR(self):
        return
    
    #Relative Strength Index (RSI)
    def calculate_RSI(self):
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