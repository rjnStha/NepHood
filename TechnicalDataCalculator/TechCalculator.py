
import pandas as pd

# Graph with Plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

class TechCalculator(object):

    def __init__(self, fundamental_dict):
        self.df = self._preprocess_fundamental_data(fundamental_dict)
    
    # Convert dict to dataframe and make consumable to panda_ta lib
    @staticmethod
    def _preprocess_fundamental_data( fundamental_dict):

        # Create DataFrame object from Dict
        df = pd.DataFrame.from_dict(fundamental_dict)
        # column_dtype = fundamental_dataframe["ltp"].dtype
        # print("Data type of column '{}' is: {}".format(column_dtype))

        # Set Date as the index of the DataFrame
        df.set_index('date',inplace=True)
        
        # NOTE Sort Index with oldest date top of the order giving higher priority to newest data 
        #   when calculation technical indicators
        df = df.sort_index(ascending=True)
        # To filter the data with specific date --> fundamental_dataframe.loc['2013-07-14':'2019-02-22']

        return df
    
    def get_technical_indicators(self):
        # Calculate all the technical indicators
        self.calculate_MACD()
        self.calculate_RSI()
        self.calculate_MFI()
        self.calculate_ATR()
        
        # Plot graph
        # self.plot_MACD_Graph()
        # self.plot_RSI_Graph()
        # self.plot_ATR_Graph()
        # self.plot_MFI_Graph()
        
        # Drop columns except date and MACD for consise data 
        new_df = self.df.drop(["high","low","ltp","open","volume"],axis=1)
        print(new_df.head(30))
        # Convention: Descending order by date, remove date as index and convert df to dict
        dict_technical = new_df.sort_index(ascending = False).reset_index().to_dict(orient='list')

        return dict_technical
    
    # Moving Average Convergence Divergence (MACD)
    # Based on the convergence and divergence of two exponential moving averages
    def calculate_MACD(self, short_period=12,long_period=26, signal=9):
        try:
            # short-term exponential moving average (EMA)
            EMA_short = self.df['ltp'].ewm(span=short_period, min_periods=1, adjust=False).mean()
            # long-term exponential moving average (EMA)
            EMA_long = self.df['ltp'].ewm(span=long_period, min_periods=1, adjust=False).mean()
            # MACD line
            MACD_Line = EMA_short - EMA_long
            # Signal line (9-day EMA of MACD)
            signal_line = MACD_Line.ewm(span=signal, min_periods=1, adjust=False).mean()
            # MACD histogram
            macd_histogram = MACD_Line - signal_line

            # Add MACD components to DataFrame
            self.df[f'macd_{short_period}_{long_period}_{signal}'] = MACD_Line
            self.df[f'macds_{short_period}_{long_period}_{signal}'] = signal_line
            self.df[f'macdh_{short_period}_{long_period}_{signal}'] = macd_histogram

        except Exception as e: raise Exception("Technical indicator: MACD", e)
     
    # Relative Strength Index (RSI)
    # momentum oscillator that measures the speed and change of price movements
    # Calculated using Exponentially Weighted Moving Average (EWM) instead of
    #   Wilder-approved Simple Moving Average (SMA), EWM gives higher weight to recent data
    def calculate_RSI(self, window=14, ema=True):
        try:
            
            # Calculate price changes
            delta = self.df['ltp'].diff()
            # Define up and down movements
            up = delta.where(delta > 0, 0)
            down = abs(delta.where(delta < 0, 0))
            # Calculate average gain and loss
            if ema:
                # Use Exponential Moving average
                avg_gain = up.ewm(com=window-1, adjust=False, min_periods=1).mean()
                avg_loss = down.ewm(com=window-1, adjust=False, min_periods=1).mean()
            else:
                # Use Simple moving averages
                avg_gain = up.rolling(window=window, min_periods=1).mean()
                avg_loss = down.rolling(window=window, min_periods=1).mean()
            # Calculate relative strength
            rs = avg_gain / avg_loss
            # Calculate RSI
            rsi = 100 - (100 / (1 + rs))
            self.df["rsi_14"] = rsi
        
        except Exception as e: raise Exception("Technical indicator: RSI", e)
   
    # Average True Range (ATR)
    # measures market volatility with the average range between the highest and lowest prices
    def calculate_ATR(self, window=14):
        try:
            # Current high - current low
            high_low = self.df['high'] - self.df['low']
            # Absolute value of Curent High - Prev ltp
            high_close = abs(self.df['high'] - self.df['ltp'].shift())
            # Absolute value of Curent low - Prev ltp
            low_close = abs(self.df['low'] - self.df['ltp'].shift())
            # Max of the high_low, high_close and low_close
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            # ATR with EMA using com 
            atr = true_range.ewm(com=window-1, adjust=False).mean()
            self.df["atr_14"] = atr
        
        except Exception as e: raise Exception("Technical indicator: ATR", e)
   
    # Money Flow Index (MFI)
    # strength of money flowing into and out of a security
    def calculate_MFI(self, window=14):
        try:

            # Typical Price
            TP = (self.df['high'] + self.df['low'] + self.df['ltp']) / 3
            # Money Flow (MF)
            MF = TP * self.df['volume']
            # Positive Money Flow (PMF) and Negative Money Flow (NMF)
            PMF = MF.where(TP > TP.shift(1), 0)
            NMF = MF.where(TP < TP.shift(1), 0)
            # Money Flow Ratio (MFR) 
            MFR = PMF.rolling(window=window).sum() / NMF.rolling(window=window).sum()
            # Money Flow Index (MFI)
            self.df['mfi_14'] = 100 - (100 / (1 + MFR))
        
        except Exception as e: raise Exception("Technical indicator: MFI", e)

    # Visualize Technical indicators with Plotly
    def plot_MACD_Graph(self):                
        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
            ), row=1, col=1
        )

        # Candlestick chart for pricing
        fig.append_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['ltp'],
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )

        # Fast Signal (%k) / MACD Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['macd_12_26_9'],
                line=dict(color='#ff9900', width=2),
                name='MACD',
                showlegend=True,
            ), row=3, col=1
        )
        
        # Slow signal (%d)/ Signal Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['macds_12_26_9'],
                line=dict(color='#000000', width=2),
                showlegend=True,
                name='Signal'
            ), row=3, col=1
        )

        # Colorize the histogram values
        colors = np.where(self.df['macdh_12_26_9'] < 0, '#000', '#ff9900')
        # Plot the histogram
        fig.append_trace(
            go.Bar(
                x=self.df.index,
                y=self.df['macdh_12_26_9'],
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
    
    def plot_RSI_Graph(self):
        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
            ), row=1, col=1
        )

        # Candlestick chart for pricing
        fig.append_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['ltp'],
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )        
        
        # Make RSI Plot
        fig.add_trace(go.Scatter(
            x=self.df.index,
            y=self.df['rsi_14'],
            line=dict(color='#ff9900', width=2),
            showlegend=True,
            name='RSI(14)'
        ), row=3, col=1)

        # Add upper/lower bounds
        fig.update_yaxes(range=[-10, 110], row=3, col=1)
        fig.add_hline(y=0, col=1, row=3, line_color="#666", line_width=2)
        fig.add_hline(y=100, col=1, row=3, line_color="#666", line_width=2)

        # Add overbought/oversold
        fig.add_hline(y=30, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash')
        fig.add_hline(y=70, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash')

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
            yaxis3=dict(title='RSI', showgrid=True, griddash = 'dot'),
        )
        # update and display
        fig.update_layout(layout)
        fig.show()

        return
    
    def plot_ATR_Graph(self):
       # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
            ), row=1, col=1
        )

        # Candlestick chart for pricing
        fig.append_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['ltp'],
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )

        # ATR
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['atr_14'],
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

    def plot_MFI_Graph(self):
        # Force lowercase (optional)
        self.df.columns = [x.lower() for x in self.df.columns]

        # Construct a 2 x 1 Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0, horizontal_spacing=1, row_heights=[0.6, 0.2, 0.2])

        # price Line
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['open'],
                line=dict(color='#ff9900', width=1),
                name='Open',
                showlegend=True
            ), row=1, col=1
        )

        # Candlestick chart for pricing
        fig.append_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['ltp'],
                increasing_line_color='Green',
                decreasing_line_color='Red',
                name='Candlestick Open Price',
                showlegend=True
            ), row=1, col=1
        )

        # Volume
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['volume'],
                name = 'Volume',
                fill='tozeroy',
                marker=dict(color='rgba(0, 0, 255, 0.5)'),
                showlegend=True
            ), row=2,col=1
        )

        # MFI
        fig.append_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df['mfi_14'],
                line=dict(color='#ff9900', width=2),
                name='MFI(14)',
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
            yaxis3=dict(title='MFI', showgrid=True, griddash = 'dot'),
        )

        # Update options and show plot
        fig.update_layout(layout)
        fig.show()

        return
