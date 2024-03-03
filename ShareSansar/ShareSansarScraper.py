import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidArgumentException
from Log.LogHandler import LogHandler
import datetime
import threading

# Static class since no instance variables 
class ShareSansarScraper():
    
    _base_link = "https://www.sharesansar.com/"
    
    '''
    NOTE:   
        Thread-local Storage pattern provides each thread with own 
        isolated WebDriver instance and helps prevent concurrency issues 
    '''
     # Create thread-local storage for driver instances
    _driver = threading.local()

    # Gets each driver instance for each thread 
    @classmethod
    def _get_driver(cls):
        if not hasattr(cls._driver, "instance"):
            # Define driver options
            chrome_options = Options()
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument("--headless") # Opens the browser up in background
            chrome_options.add_argument("--incognito")
            # Create a new WebDriver instance for this thread if it doesn't exist
            cls._driver.instance = webdriver.Chrome(options=chrome_options)
        return cls._driver.instance

    @classmethod
    def _quit_driver(cls):
        if hasattr(cls._driver, "instance"):
            # Quit the WebDriver instance if it exists
            cls._driver.instance.quit()
            del cls._driver.instance
    '''
    **************
    '''
    # NOTE: https://www.sharesansar.com/company-list
    @classmethod
    def scrape_Company_List(cls):
        # Complete link to be scraped
        complete_link = cls._base_link + "company-list"
        company_dict = {}
        driver = cls._get_driver()
        try:
            # Navigate to a URL
            driver.get(complete_link)
            print("Fetching Company List from", complete_link)

            # NOTE: Data is presented in table format for each sector with dropdown to select the sectors 
            select_element = Select(WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.XPATH,'//*[@id="sector"]'))))
            sector_options = select_element.options
            for sector in sector_options:
                try:
                    # Select next option
                    select_element.select_by_visible_text(sector.text)
                    # Search/Submit button
                    driver.find_element('id','btn_listed_submit').click()
                    # Wait for the company-table to load and get span element from the paginate 
                    # element that contains Previous btn, page numbers btns(span) and Next btn 
                    paginate_span = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH,'//*[@id="myTable_paginate"]/span')))
                    # Get the last span element total num pages
                    num_Pages = int(paginate_span.find_elements('css selector','a')[-1].text)
                    # empty list to add all the companies based on the sector
                    company_dict[sector.text] = []
                    
                    for page_num in range(1, num_Pages + 1):
                        print(f'Sector: {sector.text} HTML Page: {page_num}')
                    
                        # Wait until the price history table loads
                        table_html = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located((By.ID,"myTable")))
                        
                        # Timeout for the data in the table to load
                        # Not recommended, see how ShareSansarScraper.scrape_Price_History() handled this scenario
                        time.sleep(2)

                        # Parse the HTML table 
                        table_html = table_html.get_attribute("outerHTML")                
                        soup = BeautifulSoup(table_html, 'html.parser')
                        news_table = soup.find('table')
                        news_table_body = news_table.find('tbody')
                        for table_row in news_table_body.find_all('tr'):
                            table_data = table_row.find_all('td')
                            companySymbol = table_data[1].string.replace(',','')
                            
                            '''
                            NOTE :
                                Sector: Corporate Debentures 
                                Companies : GBD80/81, NICD83/84, NMBD87/88, GBILD86/87, NIFRAUR85/86 not added to list
                                The forward slash ( / ) throws Firstore off when accessing document
                                Error : document must have an even number of path elements
                            ''' 
                            if '/' in companySymbol: continue

                            company_dict[sector.text].append(companySymbol)
                        
                        # Next button inactive in last page so skip click 
                        if page_num < num_Pages:
                            # Click the next navigate button for new list of companies
                            driver.find_element(By.XPATH,'//*[@id="myTable_next"]').click()
                        
                except Exception as e: raise Exception(f"Error Extracting {sector} {companySymbol}", e)    

        except Exception as e:
            # Upward propagation 
            # Check for specific exceptions within the broader exception handler
            if isinstance(e, (TimeoutException, WebDriverException, InvalidArgumentException)):
                # NOTE: possible to recall the function one or more time ???
                raise Exception(f"Func: ShareSansarScraper.scarpe_Company_List(), Error occurred during navigation {complete_link}", e)
            else:
                # Handle any other exceptions
                raise Exception(f"Func: ShareSansarScraper.scarpe_Company_List()", e)
        
        # Close the WebDriver session
        finally: cls._quit_driver()
                
        return company_dict
    
    # NOTE: https://www.sharesansar.com/company/{nmb}
    # lastUpdated -> datetime type, last updated date
    @classmethod
    def scrape_Price_History(cls, company, lastUpdated = None):
        # Link to be scraped
        complete_link = cls._base_link + "company/" + company
        # Dictionary of list with keys: {Open, High, Low, Close, Volume}
        # NOTE: Save Data later in Pandas DataFrames for easier postprocessing using Panda
        price_history_dict = {}
        driver = cls._get_driver()

        try:
            driver.get(complete_link)
            print("Fetching Data from", complete_link)

            # Empty Lists to store price data
            date_list, open_list, high_list, low_list, ltp_list, volume_list = ([] for i in range(6))
            
            # Click the price history tab to get price-table of the specific company
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID,"btn_cpricehistory"))).click()
            try:
                # Wait for the company-table to load and get span element from the paginate 
                # element that contains Previous btn, page numbers btns(span) and Next btn 
                paginate_span = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCPriceHistory_paginate"]/span')))
            except: return None
            # Get the last span element for total num pages
            num_Pages = int(paginate_span.find_elements('css selector','a')[-1].text)

            # Data Validation varibales
            seen = {}
            repeated_date = []

            # Get history from every Pages
            for page_num in range(1, num_Pages + 1):
                print(f'Getting Price History {company} Page: {page_num}')
                try:
                    # Wait until the price history table loads
                    table_html = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.ID,"cpricehistory")))
                    # Sleep for the table data to load to prevent stale data
                    # Parse the HTML table 
                    table_html_outer = table_html.get_attribute("outerHTML")
                    soup = BeautifulSoup(table_html_outer, 'html.parser')
                    price_table = soup.find('table')
                    price_table_body = price_table.find('tbody')
                    for table_row in price_table_body.find_all('tr'):
                        table_data = table_row.find_all('td')
                        date = table_data[1].string.replace(',','')
                        
                        # NOTE: Sharesansar had repeated data for some companies
                        # Therefore check repeated and remove the data
                        if date in seen: 
                            repeated_date.append(date)
                            continue 
                        else: seen[date] = 1                

                        # Get the data until the last updated date
                        if lastUpdated is not None and lastUpdated <= datetime.datetime.strptime(date, "%Y-%m-%d" ):
                            price_history_dict = {
                                "date": date_list,
                                "open" : open_list,
                                "high" : high_list,
                                "low" : low_list,
                                "ltp" : ltp_list,
                                "volume": volume_list
                            }
                            # Log the removed data message
                            if len(repeated_date) != 0:
                                result_string = ', '.join(repeated_date)
                                message = f"Company:{company} Repeated data removed:{result_string}"
                                LogHandler.log_info(message)
                            
                            return price_history_dict
                    
                        date_list.append(date)
                        # Shraresansar provides volume as float but should be int 
                        volume_list.append(int(float(table_data[7].string.replace(',',''))))
                        # Convert string prices to float prices
                        open_list.append(float(table_data[2].string.replace(',','')))
                        high_list.append(float(table_data[3].string.replace(',','')))
                        low_list.append(float(table_data[4].string.replace(',','')))
                        ltp_list.append(float(table_data[5].string.replace(',','')))
                        
                    '''
                    NOTE: 
                        After navigating to next dataset in the table, it took some time to load 
                        the new data in the table. Therefore the code extracted the stale data and it 
                        was vital that we extracted correct data. 
                        One solution was to use time.sleep(3) but when multithreading the extra 3 secs 
                        added up and increased the total scarping time.
                        Another solution was to keep checking the old and new data until they are not
                        same(new data was loaded) but it was hassle -> extract table, body, rows then data
                        Thankfully the next button altered another element beside the table.                    
                    '''
                    # Next button inactive in last page so skip click 
                    if page_num < num_Pages:
                        beforeEntriesInfo = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCPriceHistory_info"]'))).text
                        # Navigate Next
                        WebDriverWait(driver, 20).until(
                                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCPriceHistory_next"]'))).click()
                        
                        # Wait until new data loaded in the table
                        while True:
                            afterEntriesInfo = WebDriverWait(driver, 20).until(
                                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCPriceHistory_info"]'))).text
                            if beforeEntriesInfo  != afterEntriesInfo:
                                break

                except Exception as e: raise Exception(f"Error Extracting page:{page_num}", e)    
            
            # Dictionary to store all fundamental data
            price_history_dict = {
                "date": date_list,
                "open" : open_list,
                "high" : high_list,
                "low" : low_list,
                "ltp" : ltp_list,
                "volume": volume_list
            }

            # Log the removed data message
            if len(repeated_date) != 0:
                result_string = ', '.join(repeated_date)
                message = f"Company:{company} Repeated data removed:{result_string}"
                LogHandler.log_info(message)
         
        except Exception as e:
            # Upward propagation 
            # Check for specific exceptions within the broader exception handler
            if isinstance(e, (TimeoutException, WebDriverException, InvalidArgumentException)):
                # Handle specific exceptions
                # TODO: possible to recall the function one or more time ???
                raise Exception(f"Func: ShareSansarScraper.scrape_Price_History(), Error occurred during navigation {complete_link}", e)
            else:
                # Handle any other exceptions
                raise Exception(f"Func: ShareSansarScraper.scrape_Price_History()", e)
        
        # Close the WebDriver session
        finally: cls._quit_driver()        

        return price_history_dict
    
    # NOTE: https://www.sharesansar.com/company/{nmb}
    @classmethod
    def scrape_News(cls, company, lastUpdated = None):
        # Dictionary with Date as key and News+Score as value 
        news_dict = {}
        # Complete link to be scraped
        complete_link = cls._base_link + "company/" + company
        driver = cls._get_driver()

        try:
            driver.get(complete_link)
            print("Fetching Data from", complete_link)

            # Click the news tab to get news-table of the specific company
            # self.driver.find_element(By.ID,"btn_cnews").click()
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID,"btn_cnews"))).click()
            # Check span element present in the page
            try:
                # Wait for the company-table to load and get span element from the paginate 
                # element that contains Previous btn, page numbers btns(span) and Next btn 
                paginate_span = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_paginate"]/span')))
            except: return None
            # Get the last span element for total num pages
            num_Pages = int(paginate_span.find_elements('css selector','a')[-1].text)
            for page_num in range(1, num_Pages + 1):
                print(f'Getting News {company} Page: {page_num}')
                try:
                    # Wait until the news-table loads
                    table_html = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.ID,"myTableCNews")))
                   
                    #Parse the HTML table 
                    table_html = table_html.get_attribute("outerHTML")                
                    soup = BeautifulSoup(table_html, 'html.parser')
                    news_table = soup.find('table')
                    news_table_body = news_table.find('tbody')
                    for table_row in news_table_body.find_all('tr'):
                        table_data = table_row.find_all('td')
                        news_date = table_data[0].string.replace(',','')
                        news = table_data[1].string.replace(',','')
                        # Get the data until the last updated date
                        if lastUpdated is not None and lastUpdated == news_date: 
                            return news_dict

                        # Add the news the Dict 
                        if news_date in news_dict: news_dict[news_date]["news"].append(news)
                        else: news_dict[news_date] = {"news": [news]}
                    
                    # NOTE: See ShareSansarScraper.scrape_Price_History() Note for
                    #   explation on why following codes required to extract data
                    # Next button inactive in last page so skip click 
                    if page_num < num_Pages:
                        beforeEntriesInfo = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_info"]'))).text
                        # Navigate Next
                        WebDriverWait(driver, 20).until(
                                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_next"]'))).click()
                        
                        # Wait until new data loaded in the table
                        while True:
                            afterEntriesInfo = WebDriverWait(driver, 20).until(
                                EC.visibility_of_element_located((By.XPATH,'//*[@id="myTableCNews_info"]'))).text
                            if beforeEntriesInfo  != afterEntriesInfo: break

                except Exception as e: raise Exception(f"Error Extracting page:{page_num}", e)

        except Exception as e:
            # Upward propagation 
            # Check for specific exceptions within the broader exception handler
            if isinstance(e, (TimeoutException, WebDriverException, InvalidArgumentException)):
                # Handle specific exceptions
                # TODO: possible to recall the function one or more time ???
                raise Exception(f"Func: ShareSansarScraper.scrape_News(), Error occurred during navigation {complete_link}", e)
            # Handle any other exceptions
            else: raise Exception(f"Func: ShareSansarScraper.scrape_News()", e)
        
        # Close the WebDriver session
        finally: cls._quit_driver()
                    
        return news_dict
    
    # NOTE: https://www.sharesansar.com/remittance
    # The monthly data in Nepali Fiscal Calender(ex. Shrawan 2080/2081) so Data Refinement required
    def scarpe_Remittance(cls):
        complete_link = cls._base_link + "remittance"
        remit_dict = {}
        driver = cls._get_driver()

        try:
            driver.get(complete_link)
            print("Fetching Remittance from", complete_link)

            # NOTE: Data is presented in table format for each fiscal year with dropdown to select the years
            select_element = Select(WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.XPATH,'//*[@id="year"]'))))
            options = select_element.options

            for fiscal_year_option in options:
                # Select the fiscal year
                select_element.select_by_visible_text(fiscal_year_option.text)
                # Search/Submit button
                driver.find_element('id','btn_remittance_submit').click()

                # List to save remitance of respective month
                month_list, remit_list = ([] for i in range(2))
            
                # Table
                table_html = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH,"/html/body/div[2]/div/section[2]/div[3]/div/div/div/div/div[1]/div[4]/div/div[1]/div/table")))
                # Timeout as WebDriver gets enough time to locate the Table
                time.sleep(3)
                # Parse the HTML table 
                table_html = table_html.get_attribute("outerHTML")                
                soup = BeautifulSoup(table_html, 'html.parser')
                news_table = soup.find('table')
                news_table_body = news_table.find('tbody')
                for table_row in news_table_body.find_all('tr'):
                    table_data = table_row.find_all('td')
                    month_list.append(table_data[1].string.replace(',',''))
                    remit_list.append(float(table_data[2].string.replace(',','')))
                
                # NOTE: Firestore doesn't support nested List
                # Save as Flattened Structure into dict
                remit_dict[fiscal_year_option.text] = {
                    "month": month_list,
                    "remittance": remit_list
                }
                             
        except Exception as e:
            # Upward propagation 
            # Check for specific exceptions within the broader exception handler
            if isinstance(e, (TimeoutException, WebDriverException, InvalidArgumentException)):
                # Handle specific exceptions
                # TODO: possible to recall the function one or more time ???
                raise Exception(f"Func: ShareSansarScraper.scarpe_Remittance(), Error occurred during navigation {complete_link}", e)
            # Handle any other exceptions
            else: raise Exception(f"Func: ShareSansarScraper.scarpe_Remittance()", e)
        
        finally: cls._quit_driver()

        return remit_dict
    
    # NOTE: https://www.sharesansar.com/inflation
    # The monthly data in Nepali Fiscal Calender(ex. Shrawan 2080/2081) so Data Refinement required
    def scarpe_Inflation(cls):
        
        complete_link = cls._base_link + "inflation"
        inflation_dict = {}
        driver = cls._get_driver()

        try:
            driver.get(complete_link)
            print("Fetching Data from", complete_link)

            # NOTE: Data is presented in table format for each fiscal year with dropdown to select the years 
            select_element = Select(WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.XPATH,'//*[@id="year"]'))))
            options = select_element.options

            for fiscal_year_option in options:
                # Select next option
                select_element.select_by_visible_text(fiscal_year_option.text)
                # Search/Submit button
                driver.find_element('id','btn_inflation_submit').click()
                
                # List to save remitance of respective month
                month_list, inflation_list = ([] for i in range(2))
            
                # Table
                table_html = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH,"/html/body/div[2]/div/section[2]/div[3]/div/div/div/div/div[1]/div[4]/div/div[1]/div/table")))
                # Timeout as WebDriver gets enough time to locate the Table
                time.sleep(3)
                # Parse the HTML table 
                table_html = table_html.get_attribute("outerHTML")                
                soup = BeautifulSoup(table_html, 'html.parser')
                news_table = soup.find('table')
                news_table_body = news_table.find('tbody')
                for table_row in news_table_body.find_all('tr'):
                    table_data = table_row.find_all('td')
                    month_list.append(table_data[1].string.replace(',',''))
                    inflation_list.append(float(table_data[2].string.replace(',','')))

                # NOTE: Firestore doesn't support nested List
                # Save as Flattened Structure into dict
                inflation_dict[fiscal_year_option.text] = {
                    "month": month_list,
                    "remittance": inflation_list
                }
                             
        except Exception as e:
            # Upward propagation 
            # Check for specific exceptions within the broader exception handler
            if isinstance(e, (TimeoutException, WebDriverException, InvalidArgumentException)):
                # Handle specific exceptions
                # TODO: possible to recall the function one or more time ???
                raise Exception(f"Func: ShareSansarScraper.scarpe_Inflation(), Error occurred during navigation {complete_link}", e)
            else:
                # Handle any other exceptions
                raise Exception(f"Func: ShareSansarScraper.scarpe_Inflation()", e)
        finally:
            cls.driver.quit()

        return inflation_dict
    
    # TODO Change the news_results XPATH
    # https://www.sharesansar.com/category/{exclusive}
    def scrape_Category(self, category):
        # Categories list: 
        # dividend-right-bonus # exclusive # latest # ipo-fpo-news # share-listed
        # expert-speak # mutual-fund # weekly-analysis # company-analysis
        self._scrape(self._base_link + "category/"+ category)
        try:
            news_results = self.driver.find_elements(By.XPATH,"//div[@class='featured-news-list margin-bottom-15']")
            for news_div in news_results:
                print(news_div)
                news_link = news_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("Link:", news_link)
            # wait for 5 seconds to confirm all data loads
            time.sleep(3)
        
        except Exception as e:
            self._error_handler(e)
        finally:
            self.driver.quit()
        return
    
# Testing
if __name__ == '__main__':
    s = ShareSansarScraper()
    s.scrape_News("nmb")