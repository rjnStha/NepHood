from ShareSansar.ShareSansarScraper import ShareSansarScraper
from Firebase.Firebase import FirestoreManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from TechnicalDataCalculator.TechCalculator import TechCalculator

class DataController(object):
    def __init__(self):
        # TODO create flags fo DB read/write
        self.load_DB_flag = False
        self.save_scraped_data_flag = True
        # Single instance initialization
        self.firestore_manager = FirestoreManager(env="dev")
        return
    
    # TODO Error Handling and return success/error
    # Save the dict of a company in Database
    def __save_DB(self, company, dict, collection_Name):
        db = self.firestore_manager.db
        # Save the Dict to the database 
        doc_ref = db.collection(collection_Name).document(company).set(dict)
        return

    # TODO Error Handling and return success/error
    def __get_DB(self, company, collection_Name):
        db = self.firestore_manager.db
        docref = db.collection(collection_Name).document(company)
        doc = docref.get()
        if doc.exists:
            return doc._data
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
                dict_News_Sentiment_Score = self.__get_DB(company,"FinancialNewsData")
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
                    self.__save_DB(company, dict_News_Sentiment_Score, "FinancialNewsData" )

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
                dict_fundamental_data = self.__get_DB(company,"FundamentalData")
            else:
                dict_fundamental_data = share_Sansar_Scraper.scrape_Price_History(company)
                if self.save_scraped_data_flag:
                    self.__save_DB(company, dict_fundamental_data, "FundamentalData" )

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
            if self.load_DB_flag:
                dict_technical_data = self.__get_DB(company,"TechnicalData")
            else:
                # TODO Error Handle empty list
                macd = tech_calculator.calculate_MACD(dict_fundamental_data)
                dict_technical_data = {
                    "MACD": macd
                    # "ATR" : tech_calculator.calculate_ATR(),
                    # "RSI" : tech_calculator.calculate_RSI(),
                    # "MFI" : tech_calculator.calculate_MFI()
                }
                
                # Save Technical data
                if self.save_scraped_data_flag:
                    self.__save_DB(company, dict_technical_data, "TechnicalData" )
        # TODO 
        except BaseException as e:
                print(e)
                return
        
        return dict_technical_data
   
    # Remittance, Inflation Rate, Exchange Rate, Consumer Price Index
    # Treasury Bill and Commercial Bank Interest Rate
    # TODO Look into Reserve Requirements including RR, RRR, CRR, and SLR indispensable tools 
    #   for Nepal Rastra Bank in regulating the country's financial system
    # TODO Find trustable data source || Problem with ShareSansar
    def collect_Macroeconomic_Data(self):
        return
    
    