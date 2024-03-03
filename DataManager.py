from ShareSansar.ShareSansarScraper import ShareSansarScraper
from Firebase.Firebase import FirestoreManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from TechnicalDataCalculator.TechCalculator import TechCalculator
from ApiRequest.NRBForexAPI import NRBForexAPI
from Log.LogHandler import LogHandler
from Multitask.MultiThread import MultiThread
from Multitask.MultiProcess import MultiProcess
import datetime

class DataManager(object):

    # Flags and Constants
    _SAVE_SCRAPED_DATA_FLAG = True
    _UPDATE_SCRAPED_DATA_FLAG  = False
    _STALE_MIN_DAYS = 7

    # List of companies based on the sector
    @classmethod
    def company_list(cls):
        try:
            dict_companies = FirestoreManager.get_doc_DB("list","CompanyList")
            
            # Scrape fundamental data
            if not dict_companies:
                dict_companies = ShareSansarScraper.scrape_Company_List()
                # Error handle empty data
                if not dict_companies:
                    raise Exception("func: DataManager.company_list() CompanyList Fetch Error")
                # Save to DB
                if cls._SAVE_SCRAPED_DATA_FLAG:
                   FirestoreManager.save_doc_DB("list", dict_companies, "CompanyList" )
        
        # Top Level Upward Propagation Exception
        # Log the exception and errors
        except Exception as e:
            print("Error: Check Error Log for more details")
            LogHandler.log_error(e)
        return dict_companies
    
    # Open, High, Low, Close and Volume of the company
    # Default company value -> get all companies Fundamental Data
    @classmethod
    def collect_Fundamental_Data(cls, company = None):
        dict_fundamental_data = {}
        try:

            # collect Fundamental data for all the companies from the list in DB
            if company is None:
                comp_dict = cls.company_list()
                company_list_flattened = [item for sublist in comp_dict.values() for item in sublist]
                # Recursive function, passed as parameter in Multithread object
                multithread = MultiThread(cls.collect_Fundamental_Data)
                results = multithread.process_tasks_with_threads(company_list_flattened)
                return results
            
            # Else collect data for specific company
            dict_fundamental_data = FirestoreManager.get_doc_DB(company,"FundamentalData")
            
            # Scrape fundamental data 
            if not dict_fundamental_data:
                dict_fundamental_data = ShareSansarScraper.scrape_Price_History(company)
                # Check if empty data returned after scraping
                if not dict_fundamental_data: 
                    LogHandler.log_warning(f"Company: {company} seems to be missing Fundamental Data; Website Verification Required, TimeoutException()")
                    return None
                # Save to DB
                if cls._SAVE_SCRAPED_DATA_FLAG: 
                    FirestoreManager.save_doc_DB(company, dict_fundamental_data, "FundamentalData" )
                    LogHandler.log_info(f"Company: {company} Fundamental Data added")

            
            else:
                # UPDATE Data
                # Scrape new data and merge with the older set
                if cls._UPDATE_SCRAPED_DATA_FLAG:
                    # Check the latest data on date and update if not current
                    # NOTE: Assumption that the first elemet of date list is the latest date
                    lastUpdatedDate = datetime.datetime.strptime(dict_fundamental_data["date"][0], "%Y-%m-%d" )
                    current_date = datetime.datetime.today()
                    diff_date = abs((lastUpdatedDate - current_date).days)
                    if diff_date > cls._STALE_MIN_DAYS:
                        # Get latest data
                        new_dict_fundamental_data = ShareSansarScraper.scrape_Price_History(company, lastUpdatedDate)
                        
                        # Check if empty data returned after scraping
                        if not new_dict_fundamental_data: raise Exception(f"Func: DataManager.collect_Fundamental_Data() lastUpdate: {lastUpdatedDate}, Empty List")
                        
                        merged_dict = {key: new_dict_fundamental_data.get(key, []) + dict_fundamental_data.get(key, []) 
                                       for key in set(new_dict_fundamental_data) | set(dict_fundamental_data)}
                        # Save to DB
                        if DataManager._SAVE_SCRAPED_DATA_FLAG: 
                            FirestoreManager.save_doc_DB(company, merged_dict, "FundamentalData" )
                            LogHandler.log_info(f"Company: {company} Fundamental Data updated from {lastUpdatedDate} to {current_date}")
                        return merged_dict

        # Top Level Upward Propagation Exception
        # Log the exception and errors
        except Exception as e:
            print("Error: Check Error Log for more details")
            LogHandler.log_error(f"Company:{company} {e}")
            return
        return dict_fundamental_data
 
    # Calculate Average Sentiment Score from Dict News
    # average_Sentiment_Score_Daily
    @classmethod
    def collect_Financial_News_Data(cls, company = None):
        dict_Sentiment_Score = {}
        try:
            # collect Fundamental data for all the companies from the list in DB
            if company is None:
                comp_dict = cls.company_list()
                company_list_flattened = [item for sublist in comp_dict.values() for item in sublist]
                # Recursive function, passed as parameter in Multithread object
                multithread = MultiThread(cls.collect_Financial_News_Data)
                results = multithread.process_tasks_with_threads(company_list_flattened)
                return results
            
            dict_Sentiment_Score = FirestoreManager.get_doc_DB(company,"FinancialNewsData")
            
            # Scrape News
            if not dict_Sentiment_Score:
                news_dict = ShareSansarScraper.scrape_News(company)
                # Check if empty data returned after scraping
                if not news_dict:
                    LogHandler.log_warning(f"Company: {company} seems to be missing Financial News Data; Website Verification Required, TimeoutException() ")
                    return None
                dict_Sentiment_Score = cls.__sentiment_scores(news_dict)
                # Save to DB
                if cls._SAVE_SCRAPED_DATA_FLAG: 
                    FirestoreManager.save_doc_DB(company, dict_Sentiment_Score, "FinancialNewsData" )
                    LogHandler.log_info(f"Company: {company} Financial News Data added")

            else:
                # UPDATE Data
                # Scrape new data and merge with the older set
                if cls._UPDATE_SCRAPED_DATA_FLAG:
                    dates_list = list(dict_Sentiment_Score.keys())
                    # Not necessarily true that keys in dict are sorted
                    dates_list.sort()
                    # Check the latest data on date and update if not current
                    lastUpdatedDate = datetime.datetime.strptime(dates_list[-1], "%Y-%m-%d" )
                    current_date = datetime.datetime.today()
                    diff_date = abs((lastUpdatedDate - current_date).days)
                    if diff_date > cls._STALE_MIN_DAYS:
                        lastUpdatedDate_string = lastUpdatedDate.date().strftime("%Y-%m-%d")
                        new_news_dict = ShareSansarScraper.scrape_News(company, lastUpdatedDate_string)
                        
                        if not new_news_dict: raise Exception(f"Func: DataManager.collect_Financial_News_Data() lastUpdate: {lastUpdatedDate}, Empty News Data")

                        new_dict_Sentiment_Score = cls.__sentiment_scores(news_dict)

                        merged_dict = {key: dict_Sentiment_Score.get(key, []) + new_dict_Sentiment_Score.get(key, []) 
                                       for key in set(dict_Sentiment_Score) | set(new_dict_Sentiment_Score)}
                        
                        if cls._SAVE_SCRAPED_DATA_FLAG: 
                            FirestoreManager.save_doc_DB(company, dict_Sentiment_Score, "FinancialNewsData" )
                            LogHandler.log_info(f"Company: {company} Financial News Data updated from {lastUpdatedDate} to {current_date}")

                        return merged_dict

        # Top Level Upward Propagation Exception
        # Log the exception and errors
        except Exception as e:
            print("Error: Check Error Log for more details")
            LogHandler.log_error(f"Company:{company} {e}")
        
        return dict_Sentiment_Score
    
    # Moving Average Convergence Divergence (MACD), Average True Range (ATR), 
    # Relative Strength Index (RSI) and Money Flow Index (MFI)
    @classmethod
    def collect_Technical_Data(cls, company = None):
        dict_technical_data = {}
        
        try:
             # collect Technical data for all the companies from the list in DB
            if company is None:
                comp_dict = cls.company_list()
                company_list_flattened = [item for sublist in comp_dict.values() for item in sublist]
                # Recursive function, passed as parameter in Multiprocess object
                multiprocess = MultiProcess(cls.collect_Technical_Data)
                results = multiprocess.process_tasks(company_list_flattened)
                return results
            
            dict_technical_data =  FirestoreManager.get_doc_DB(company,"TechnicalData")
            
            if not dict_technical_data:
                dict_fundamental_data = cls.collect_Fundamental_Data(company)

                tech_calculator = TechCalculator(dict_fundamental_data)
                dict_technical_data = tech_calculator.get_technical_indicators()

                # Save Technical data
                if DataManager._SAVE_SCRAPED_DATA_FLAG:
                    FirestoreManager.save_doc_DB(company, dict_technical_data, "TechnicalData" )
                    LogHandler.log_info(f"Company: {company} Technical Data added")
            
            else:
                # TODO: Update work required
                if(cls._UPDATE_SCRAPED_DATA_FLAG):
                    pass
                    # dict_fundamental_data = cls.collect_Fundamental_Data(company)
                    # fund_lastUpdatedDate = datetime.datetime.strptime(dict_fundamental_data["date"][0], "%Y-%m-%d" )
                    # tech_lastUpdatedDate = datetime.datetime.strptime(dict_technical_data["date"][0], "%Y-%m-%d" )
                    # diff_date = abs((fund_lastUpdatedDate - tech_lastUpdatedDate).days)
                    # if diff_date > 0:
                    #     tech_calculator = TechCalculator(dict_fundamental_data)
                    #     new_dict_tech_data = tech_calculator.get_technical_indicators(tech_lastUpdatedDate)

                    #     # Check if empty data returned after scraping
                    #     if not new_dict_tech_data: raise Exception(f"Func: DataManager.collect_Technical_Data() lastUpdate: {tech_lastUpdatedDate}, Empty List")
                        
                    #     merged_dict = {key: new_dict_tech_data.get(key, []) + dict_technical_data.get(key, []) 
                    #                    for key in set(new_dict_tech_data) | set(dict_technical_data)}
                    #     # Save to DB
                    #     if DataManager._SAVE_SCRAPED_DATA_FLAG: 
                    #         FirestoreManager.save_doc_DB(company, merged_dict, "TechnicalData" )
                    #         LogHandler.log_info(f"Company: {company} Technical Data updated from {tech_lastUpdatedDate} to {fund_lastUpdatedDate}")
                    #     return merged_dict

        # Top Level Upward Propagation Exception
        # Log the exception and errors
        except Exception as e:
            print("Error: Check Error Log for more details")
            LogHandler.log_error(f"Company: {company} {e}")
        
        return dict_technical_data
   
    # Remittance, Inflation Rate, Exchange Rate, Consumer Price Index
    # Treasury Bill and Commercial Bank Interest Rate
    # TODO Look into Reserve Requirements including RR, RRR, CRR, and SLR indispensable tools 
    #   for Nepal Rastra Bank in regulating the country's financial system
    #   Price to Earning Ratio, Asset Liability (Balance Sheet) and Operating Margin
    def collect_Macroeconomic_Data(cls):
        dict_macro_data = {}
        share_Sansar_Scraper = ShareSansarScraper()
        # TODO: cleaner class defination
        nrb_forex_api = NRBForexAPI()

        try:
            dict_macro_data =  cls.data_manager.get_doc_DB("Data","MacroEconomicData")
            if dict_macro_data is None :
                remittance = ShareSansarScraper.scarpe_Remittance()
                inflation = ShareSansarScraper.scarpe_Inflation()
                # Specify from and to date to get specific data
                exchange_rate_US = nrb_forex_api.get_US_Rate()

                dict_macro_data = {
                    "remittance": remittance,
                    "inflation" : inflation,
                    "exchangeRateUS" : exchange_rate_US
                }

                # Save MacroEconomic Data
                if cls._SAVE_SCRAPED_DATA_FLAG:
                    FirestoreManager.save_doc_DB("Data", dict_macro_data, "MacroEconomicData" )
                    # TODO
                    # LogHandler.log_info(f"Company: {company} Fundamental Data added")
                else:
                # TODO: UPDATE Data
                # Scrape new data and merge with the older set
                    if cls._UPDATE_SCRAPED_DATA_FLAG:
                        pass


        except BaseException as e:
            LogHandler.log_error("MacroEconomicData")
        
        return dict_macro_data
    
    # Delete Collection
    def deleteCollection(self, collection_Name):
        FirestoreManager.delete_Collection(collection_Name)

    # TODO Fine tune VADER for beter analysis
    # Returns the Compound Sentiment Score
    def __sentiment_scores(self, newsDict):
        
        # Create a SentimentIntensityAnalyzer object.
        sia_obj = SentimentIntensityAnalyzer()
        
        # Get Sentient score for each news in the dict
        for keyDate in newsDict:
            daily_News_Array = newsDict[keyDate]["news"]
            sumSentiment_Score = 0.0
            for daily_News in daily_News_Array:
                # returns a sentiment dictionary with pos, neg, neu, and compound scores.
                sentiment_dict = sia_obj.polarity_scores(daily_News)
                sumSentiment_Score += sentiment_dict['compound']
            averageSentimentScore = sumSentiment_Score / len(daily_News_Array)
            # Store score as key-value pair
            newsDict[keyDate]["score"] = averageSentimentScore
        
        # Return the compound score as the news sentiment score
        return newsDict
