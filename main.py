from Firebase.Firebase import FirestoreManager
from ShareSansar.ShareSansarScraper import ShareSansarScraper 

# Save the Dict to the database
# TODO Move this to Lower Hierarchy
db = FirestoreManager(env="dev").db
shareSansarScraper = ShareSansarScraper()
company = "nmb"
doc_ref = db.collection("CompanyNewsScore").document(company).set(shareSansarScraper.scrape_news_score(company))