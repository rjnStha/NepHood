from ShareSansar.ShareSansarScraper import ShareSansarScraper
from Firebase.Firebase import FirestoreManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from TechnicalDataCalculator.TechCalculator import TechCalculator
from ApiRequest.NRBForexAPI import NRBForexAPI

class DataCollector(object):
    def __init__(self):
        # TODO create flags fo DB read/write
        self.load_DB_flag = True
        self.save_scraped_data_flag = True
        # Single instance initialization
        self.data_manager = FirestoreManager(env="dev")
        return
           
    # Returns the Compound Sentiment Score
    def __sentiment_scores(self, sentence):

        # Create a SentimentIntensityAnalyzer object.
        sid_obj = SentimentIntensityAnalyzer()

        # returns a sentiment dictionary with pos, neg, neu, and compound scores.
        sentiment_dict = sid_obj.polarity_scores(sentence)
        # Return the compound score as the news sentiment score
        return sentiment_dict['compound']

    # Calculate Average Sentiment Score from Dict News
    # average_Sentiment_Score_Daily
    def collect_Financial_News_Data(self, company):
        dict_News_Sentiment_Score = {}
        share_Sansar_Scraper = ShareSansarScraper()
        # TODO Data Prepossessing
        try:
            if self.load_DB_flag:
                dict_News_Sentiment_Score = self.data_manager.get_DB(company,"FinancialNewsData")
            else:
                news = share_Sansar_Scraper.scrape_News(company)
                # Error handle empty data
                if not news:
                  raise Exception("Error News Fetch for Financial Data")
                else: 
                    # Iterate Dict News
                    for key in news:
                        daily_News_Array = news[key]
                        sumSentiment_Score = 0.0
                        for daily_News in daily_News_Array:
                            sentiment_Score = self.__sentiment_scores(daily_News)
                            # print (key + ": " + str(sentiment_Score))
                            sumSentiment_Score += sentiment_Score
                        averageSentimentScore = sumSentiment_Score / len(daily_News_Array)
                        dict_News_Sentiment_Score[key] = averageSentimentScore

                if self.save_scraped_data_flag:
                    self.data_manager.save_DB(company, dict_News_Sentiment_Score, "FinancialNewsData" )

            # Error handle empty data
            if not dict_News_Sentiment_Score:
                  raise Exception("Data Fetch Error")

        # TODO    
        except BaseException as e:
            print(e)
            return
        
        return dict_News_Sentiment_Score
    
    # Open, High, Low, Close and Volume of the company
    def collect_Fundamental_Data(self, company):
        dict_fundamental_data = {}
        share_Sansar_Scraper = ShareSansarScraper()
        try:
            if self.load_DB_flag:
                dict_fundamental_data = self.data_manager.get_DB(company,"FundamentalData")
            else:
                dict_fundamental_data = share_Sansar_Scraper.scrape_Price_History(company)
                if self.save_scraped_data_flag:
                    self.data_manager.save_DB(company, dict_fundamental_data, "FundamentalData" )

            # Error handle empty data
            if not dict_fundamental_data:
                  raise Exception("Data Fetch Error")

        # TODO    
        except BaseException as e:
                print(e)
                return
        return dict_fundamental_data
 
    # Moving Average Convergence Divergence (MACD), Average True Range (ATR), 
    # Relative Strength Index (RSI) and Money Flow Index (MFI)
    def collect_Technical_Data(self, company):
        dict_technical_data = {}
        tech_calculator = TechCalculator()
        dict_fundamental_data = self.collect_Fundamental_Data(company)
        
        try:
            # TODO Solve circular logic for Flag 
            # Possible Solution: Remove flag and always get data from DB first else scrape
            if False:
                dict_technical_data =  self.data_manager.get_DB(company,"TechnicalData")
            else:
                # TODO Error Handle empty list
                macd = tech_calculator.calculate_MACD(dict_fundamental_data)
                rsi = tech_calculator.calculate_RSI(dict_fundamental_data)
                atr = tech_calculator.calculate_ATR(dict_fundamental_data)
                mfi = tech_calculator.calculate_MFI(dict_fundamental_data)
                
                dict_technical_data = {
                    "MACD": macd,
                    "RSI" : rsi,
                    "ATR" : atr,
                    "MFI" : mfi
                }
                
                # Save Technical data
                if self.save_scraped_data_flag:
                     self.data_manager.save_DB(company, dict_technical_data, "TechnicalData" )

        except BaseException as e:
                print(e)
                return
        
        return dict_technical_data
   
    # Remittance, Inflation Rate, Exchange Rate, Consumer Price Index
    # Treasury Bill and Commercial Bank Interest Rate
    # TODO Look into Reserve Requirements including RR, RRR, CRR, and SLR indispensable tools 
    #   for Nepal Rastra Bank in regulating the country's financial system
    #   Price to Earning Ratio, Asset Liability (Balance Sheet) and Operating Margin
    def collect_Macroeconomic_Data(self):
        dict_macro_data = {}
        share_Sansar_Scraper = ShareSansarScraper()
        nrb_forex_api = NRBForexAPI()

        try:
            remittance = share_Sansar_Scraper.scarpe_Remittance()
            inflation = share_Sansar_Scraper.scarpe_Inflation()
            # Specify from and to date to get specific data
            exchange_rate_US = nrb_forex_api.get_US_Rate()

            dict_macro_data = {
                    "remittance": remittance,
                    "inflation" : inflation,
                    "exchangeRateUS" : exchange_rate_US
            }

            # Save Technical data
            if self.save_scraped_data_flag:
                    self.data_manager.save_DB(dict_macro_data, "MacroEconomicData" )

        except BaseException as e:
            return
        
        return
    
    