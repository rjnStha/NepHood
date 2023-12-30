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
    def scrape_news(self, company):
        # Dictionary with Date as key and News+Score as value 
        NewsDict = {}
        self._scrape(self.base_link + "company/" + company)
        try:
            # Click the news tab to get news-table of the specific company
            # self.driver.find_element(By.ID,"btn_cnews").click()
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID,"btn_cnews"))).click()
            # Wait for the news-table to load and Get the number of pages
            numPages = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_paginate"]/span/a[6]'))).text

            # Get news from every Pages
            int(numPages)
            for _ in range(3):
                print("Getting table html")
                try:
                    # Wait until the news-table loads
                    tableHTML = WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.ID,"myTableCNews")))
                    # Timeout as WebDriver gets enough time to locate the Table
                    time.sleep(3)

                    #Parse the HTML table 
                    tableHTML = tableHTML.get_attribute("outerHTML")                
                    soup = BeautifulSoup(tableHTML, 'html.parser')
                    newsTable = soup.find('table')
                    newsTableBody = newsTable.find('tbody')
                    for tableRow in newsTableBody.find_all('tr'):
                        tableData = tableRow.find_all('td')
                        newsDate = tableData[0].string.replace(',','')
                        news = tableData[1].string.replace(',','')
                        # Add the news the Dict 
                        if newsDate in NewsDict:
                            NewsDict[newsDate].append(news)
                        else:
                            NewsDict[newsDate] = [news]

                except BaseException as e:
                    raise Exception()
                
                # Click the next navigate button for new list of news
                self.driver.find_element(By.XPATH,'//*[@id="myTableCNews_next"]').click()

        except BaseException as e:
                self._error_handler(e)
        
        finally:
            self.driver.quit()
                    
        return NewsDict
    
    # TODO Change the news_results XPATH
    # https://www.sharesansar.com/category/{exclusive}
    def scrape_category(self, category):
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
    s.scrape_news("nmb")