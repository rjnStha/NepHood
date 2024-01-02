from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

class Scraper(object):
    def __init__(self):
        # self.db = FirestoreManager(env="dev").db
        self.chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        # self.chrome_options.add_argument("--headless") # Opens the browser up in background
        self.chrome_options.add_argument("--incognito")

    def _scrape(self, complete_link):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        print("Log: Fetching Data from", complete_link)
        try:
            self.driver.get(complete_link)
        except TimeoutException as e:
            self.driver.quit()
            return []
        print("Log: Fetch Complete")
    
    def _error_handler(self, e):
        if e == AttributeError:
            print("AttributeError")
        elif e == TimeoutException:
            print("TimeoutException")
    