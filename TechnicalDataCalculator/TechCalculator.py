
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
    # Default Fast and slow period 12 days and 26 days respectively while signal with 9 days
    def calculate_MACD(self, fundamental_dict, fast_period=12,slow_period=26, signal=9):
        df = self.preprocess_fundamental_data(fundamental_dict)

        # Calculate MACD values using the pandas_ta library
        # MACD Line = (12-day EMA - 26-day EMA)
        # Signal Line = 9-day EMA of MACD Line
        # MACD Histogram = MACD Line - Signal Line
        df.ta.macd(close='ltp', fast=fast_period, slow=slow_period, signal=signal, append=True)
        
        # Plot MACD graph
        self.plot_MACD_Graph(df)
        
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
    # Default period 14 days
    def calculate_RSI(self, fundamental_dict, period=14):
        df = self.preprocess_fundamental_data(fundamental_dict)

        # Calculate the RSI where length = lookback period in days
        df.ta.rsi(close='ltp', length=period, append=True)
        
        # Plot RSI graph
        self.plot_RSI_Graph(df)

        # Remove unwanted data columns
        # List of columns to remove
        columns_to_remove = ["high","low","ltp","open","volume"]
        df = df.drop(columns=columns_to_remove)

        # Reset the index to include Date as data and return as dictionary of list
        return df.reset_index().to_dict(orient='list')
   
    # Calculate Average True Range (ATR)
    # Default period 14 days
    def calculate_ATR(self, fundamental_dict, period=14):
        df = self.preprocess_fundamental_data(fundamental_dict)
        
        # Calculate the RSI where length = lookback period in days
        df.ta.atr(close=df['ltp'], length=period, append=True)

         # Plot ATR graph
        self.plot_ATR_Graph(df)

        # Remove unwanted data columns
        # List of columns to remove
        columns_to_remove = ["high","low","ltp","open","volume"]
        df = df.drop(columns=columns_to_remove)

        return df.reset_index().to_dict(orient='list')
   
    # Money Flow Index (MFI)
    def calculate_MFI(self):
        
        return
    
    # Visualize MACD with Plotly
    def plot_MACD_Graph(self, fundamental_dataframe):
        # Force lowercase (optional)
        fundamental_dataframe.columns = [x.lower() for x in fundamental_dataframe.columns]
        
        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
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
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )

        # Fast Signal (%k) / MACD Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macd_12_26_9'],
                line=dict(color='#ff9900', width=2),
                name='MACD',
                showlegend=True,
            ), row=3, col=1
        )
        
        # Slow signal (%d)/ Signal Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macds_12_26_9'],
                line=dict(color='#000000', width=2),
                showlegend=True,
                name='Signal'
            ), row=3, col=1
        )

        # Colorize the histogram values
        colors = np.where(fundamental_dataframe['macdh_12_26_9'] < 0, '#000', '#ff9900')
        # Plot the histogram
        fig.append_trace(
            go.Bar(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['macdh_12_26_9'],
                name='Histogram',
                marker_color=colors,
            ), row=3, col=1
        )

        # Make it pretty
        layout = go.Layout(
            plot_bgcolor='#efefef',
            # Font Families
            font_family='Monospace',
            font_color='#000000',
            font_size=14,
            # Axis
            xaxis=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            xaxis2=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            xaxis3=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            yaxis=dict(title='Stock Price and Volume', showgrid=True, griddash = 'dot'),
            yaxis2=dict(title='Volume', showgrid=True, griddash = 'dot'),
            yaxis3=dict(title='MACD', showgrid=True, griddash = 'dot'),
        )

        # Update options and show plot
        fig.update_layout(layout)
        fig.show()
    
    # Visualize RSI with Plotly
    def plot_RSI_Graph(self, fundamental_dataframe):
        # Force lowercase (optional)
        fundamental_dataframe.columns = [x.lower() for x in fundamental_dataframe.columns]

        # Create Figure
        fig = make_subplots(rows=2, cols=1, shared_xaxes=False, row_width=[0.25, 0.75])
        
        # price Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['open'],
                line=dict(color='#ff9900', width=1),
                name='open',
                showlegend=True,
                legendgroup='1',
            ), row=1, col=1
        )

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
            y=fundamental_dataframe['rsi_14'],
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
    
    def plot_ATR_Graph(self, fundamental_dataframe):
        # Force lowercase (optional)
        fundamental_dataframe.columns = [x.lower() for x in fundamental_dataframe.columns]

        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
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
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )

        # RSI
        fig.append_trace(
            go.Scatter(
                x=fundamental_dataframe.index,
                y=fundamental_dataframe['atrr_14'],
                line=dict(color='#ff9900', width=2),
                name='ATR(14)',
                showlegend=True,
            ), row=3, col=1
        )

        # Make it pretty
        layout = go.Layout(
            plot_bgcolor='#efefef',
            # Font Families
            font_family='Monospace',
            font_color='#000000',
            font_size=14,
            # Axis
            xaxis=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            xaxis2=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            xaxis3=dict(rangeslider=dict(visible=False), showgrid=True, griddash='dot'),
            yaxis=dict(title='Stock Price and Volume', showgrid=True, griddash = 'dot'),
            yaxis2=dict(title='Volume', showgrid=True, griddash = 'dot'),
            yaxis3=dict(title='ATR', showgrid=True, griddash = 'dot'),
        )

        # Update options and show plot
        fig.update_layout(layout)
        fig.show()

        return