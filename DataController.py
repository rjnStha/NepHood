from ShareSansar.ShareSansarScraper import ShareSansarScraper
from Firebase.Firebase import FirestoreManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



class DataController(object):
    def __init__(self):
        # TODO create flags to save or just process data save_DB
        return
    
    # Returns the Compound Sentiment Score
    def __sentiment_scores(self,sentence):

        # Create a SentimentIntensityAnalyzer object.
        sid_obj = SentimentIntensityAnalyzer()

        # returns a sentiment dictionary with pos, neg, neu, and compound scores.
        sentiment_dict = sid_obj.polarity_scores(sentence)
        # Return the compound score as the news sentiment score
        return sentiment_dict['compound']

    # Calculate Average Sentiment Score from Dict News
    # average_Sentiment_Score_Daily
    def collect_Financial_News_Data(self, company):
        share_Sansar_Scraper = ShareSansarScraper()
        # TODO Data Prepossessing
        news = share_Sansar_Scraper.scrape_News(company)
        dict_News_Sentiment_Score = {}
        
        # Iterate Dict News
        for key in news:
            daily_News_Array = news[key]
            sumSentiment_Score = 0.0
            for daily_News in daily_News_Array:
                sentiment_Score = self.__sentiment_scores(daily_News)
                print (key + ": " + str(sentiment_Score))
                sumSentiment_Score += sentiment_Score
            averageSentimentScore = sumSentiment_Score / len(daily_News_Array)
            dict_News_Sentiment_Score[key] = averageSentimentScore
        
        self.save_DB(company,dict_News_Sentiment_Score,"FinancialNewsData")

        return dict_News_Sentiment_Score
    
    # Open, High, Low, Close and Volume of the company
    def collect_Fundamental_Data(self, company):
        share_Sansar_Scraper = ShareSansarScraper()
        dict_fundamental_data = share_Sansar_Scraper.scrape_Price_History(company)
        self.save_DB(company,dict_fundamental_data,"FundamentalData")
        return dict_fundamental_data

    def save_DB(self, company, dict, collection_Name):
        db = FirestoreManager(env="dev").db
        # Save the Dict to the database 
        doc_ref = db.collection(collection_Name).document(company).set(dict)