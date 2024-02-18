import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class BuffettNoEnvironment(Exception):
    pass

class FirestoreManager:
    # Initialize once per each run
    # NOTE Alternate solution : Singleton Pattern
    def __init__(self, env) -> None:
        # Credentials
        cred = credentials.Certificate('Firebase/ainepse-firebaseKey.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    # TODO Error Handling and return success/error
    # Save the dict of a company in Database
    def save_DB(self, company, dict, collection_Name):
        # Save the Dict to the database 
        doc_ref = self.db.collection(collection_Name).document(company).set(dict)
        return

    # TODO Error Handling and return success/error
    def get_DB(self, company, collection_Name):
        docref = self.db.collection(collection_Name).document(company)
        doc = docref.get()
        if doc.exists:
            return doc._data
        return None
    
    # Save file
    def save_to_csv(self, company, collection_Name):
        data_dict = self.get_DB(company,collection_Name)
        data_macd = data_dict["MACD"]
        data_rsi = data_dict["RSI"]
        data = data_macd
        # Write data to CSV file
        with open('output.csv', 'w', newline='') as csvfile:
            
            fieldnames = data.keys()

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Transpose the data and write rows
            rows = zip(*data.values())
            for row in rows:
                writer.writerow(dict(zip(fieldnames, row)))
