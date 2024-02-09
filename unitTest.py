import pytest
from ShareSansar.ShareSansarScraper import ShareSansarScraper
from TechnicalDataCalculator.TechCalculator import TechCalculator
from Firebase.Firebase import FirestoreManager


company = "nica"


# Test Fundamental Data for Duplicates  
def __has_duplicate_values(dictionary):
    seen_values = []

    for key, values_list in dictionary.items():
        print(key)
        if(key == "date"):
            count = 0
            for value in values_list:
                try:
                    index = seen_values.index(value)
                    print(f"The value {value} is at index {index}.")
                    print(f'Current index:{count}')
                except ValueError:
                    seen_values.append(value)
                count+=1

    return

test_dict = {
    "date": ["2024-01-01","2024-01-01"]
}
__has_duplicate_values(test_dict)

share_sansar_dict = {}
firestore_manager = FirestoreManager(env="dev")
db = firestore_manager.db
docref = db.collection("FundamentalData").document(company)
doc = docref.get()
if doc.exists:
    share_sansar_dict = doc._data
print("share_sansar_DB")
__has_duplicate_values(share_sansar_dict)

# share_sansar_scraper = ShareSansarScraper()
# share_scrape_dict = share_sansar_scraper.scrape_Price_History(company)
# print("share_sansar_scraper")
# __has_duplicate_values(share_scrape_dict)

tech_calculator = TechCalculator()
tech_dict = tech_calculator.preprocess_fundamental_data(share_sansar_dict)
print("tech_calculator")
__has_duplicate_values(tech_dict)