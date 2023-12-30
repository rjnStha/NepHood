import time
from ShareSansar.Scraper import Scraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class ShareSansarScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.base_link ="https://www.sharesansar.com/"
    
    # # https://www.sharesansar.com/company-list
    # def scrape_companyList(self):
    #     # Dictionary with Date as key and News+Score as value 
    #     CompanyFundDict = {}
    #     self._scrape(self.base_link + "company-list")
    #     try:
    #         # Click the news tab to get news-table of the specific company
    #         self.driver.find_element(By.ID,"btn_cnews").click()

            

    #     except BaseException as e:
    #             self._error_handler(e)
        
    #     finally:
    #         self.driver.quit()
                    
    #     return NewsDict
    
    # TODO Error Handling
    # https://www.sharesansar.com/company/{nmb}
    def scrape_News(self, company):
        # Dictionary with Date as key and News+Score as value 
        news_dict = {}
        self._scrape(self.base_link + "company/" + company)
        try:
            # Click the news tab to get news-table of the specific company
            # self.driver.find_element(By.ID,"btn_cnews").click()
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID,"btn_cnews"))).click()
            # Wait for the news-table to load and Get the number of pages
            num_Pages = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_paginate"]/span/a[6]'))).text

            # Get news from every Pages
            for _ in range(int(num_Pages)):
                print("Getting News Table HTML")
                try:
                    # Wait until the news-table loads
                    table_html = WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.ID,"myTableCNews")))
                    # Timeout as WebDriver gets enough time to locate the Table
                    time.sleep(3)

                    #Parse the HTML table 
                    table_html = table_html.get_attribute("outerHTML")                
                    soup = BeautifulSoup(table_html, 'html.parser')
                    news_table = soup.find('table')
                    news_table_body = news_table.find('tbody')
                    for table_row in news_table_body.find_all('tr'):
                        table_data = table_row.find_all('td')
                        news_date = table_data[0].string.replace(',','')
                        news = table_data[1].string.replace(',','')
                        # Add the news the Dict 
                        if news_date in news_dict:
                            news_dict[news_date].append(news)
                        else:
                            news_dict[news_date] = [news]

                except BaseException as e:
                    raise Exception()
                
                # Click the next navigate button for new list of news
                self.driver.find_element(By.XPATH,'//*[@id="myTableCNews_next"]').click()

        except BaseException as e:
                self._error_handler(e)
        
        finally:
            self.driver.quit()
                    
        return news_dict
    
    # TODO Error Handling
    # https://www.sharesansar.com/company/{nmb}
    def scrape_Price_History(self,company):
        # Dictionary with Date as key and Prices as value
        # Open, High, Low, Close and Volume
        price_history_dict = {}
        self._scrape(self.base_link + "company/" + company)
        try:
            # Click the price history tab to get price-table of the specific company
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID,"btn_cpricehistory"))).click()
            # Wait for the price-table to load and Get the number of pages
            num_Pages = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCPriceHistory_paginate"]/span/a[6]'))).text
             # Get news from every Pages
            for _ in range(int(num_Pages)):
                print("Getting Price History Table HTML")
                try:
                    # Wait until the news-table loads
                    tableHTML = WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.ID,"cpricehistory")))
                    # Timeout as WebDriver gets enough time to locate the Table
                    time.sleep(3)

                    #Parse the HTML table 
                    tableHTML = tableHTML.get_attribute("outerHTML")                
                    soup = BeautifulSoup(tableHTML, 'html.parser')
                    newsTable = soup.find('table')
                    news_table_body = newsTable.find('tbody')
                    price_daily_dict = {}
                    for table_row in news_table_body.find_all('tr'):
                        table_data = table_row.find_all('td')
                        date = table_data[1].string.replace(',','')
                        price_daily_dict = {
                            'open': table_data[2].string.replace(',',''),
                            'high': table_data[3].string.replace(',',''),
                            'low': table_data[4].string.replace(',',''),
                            'ltp:': table_data[5].string.replace(',',''),
                            'volume': table_data[7].string.replace(',','')}
                        price_history_dict[date] = price_daily_dict
                
                except BaseException as e:
                    raise Exception()
                
            # Click the next navigate button for new list of price histroy
                self.driver.find_element(By.XPATH,'//*[@id="myTableCPriceHistory_next"]').click()

        except BaseException as e:
                self._error_handler(e)
        finally:
            self.driver.quit()

        return price_history_dict

    # TODO Change the news_results XPATH
    # https://www.sharesansar.com/category/{exclusive}
    def scrape_Category(self, category):
        # Categories list: 
        # dividend-right-bonus # exclusive # latest # ipo-fpo-news # share-listed
        # expert-speak # mutual-fund # weekly-analysis # company-analysis
        self._scrape(self.base_link + "category/"+ category)
        try:
            news_results = self.driver.find_elements(By.XPATH,"//div[@class='featured-news-list margin-bottom-15']")
            for news_div in news_results:
                print(news_div)
                news_link = news_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("Link:", news_link)
            # wait for 5 seconds to confirm all data loads
            time.sleep(3)
        
        except BaseException as e:
            self._error_handler(e)
        finally:
            self.driver.quit()
        return
    
# Testing
if __name__ == '__main__':
    s = ShareSansarScraper()
    s.scrape_News("nmb")