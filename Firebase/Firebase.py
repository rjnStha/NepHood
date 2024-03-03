import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading

# Singleton Firestore Class
class FirestoreManager(object):
    _firestore_instance = None
    # Lock to ensure thread safety
    _lock = threading.Lock()

    def __init__(self, value):
        self.value = value

    @classmethod
    def _get_instance(cls):
        if cls._firestore_instance is None:
            with cls._lock:
                # Double check locking for efficiency
                if cls._firestore_instance is None:  
                    cls._firestore_instance = cls._create_firestore_client()
        return cls._firestore_instance

    @staticmethod
    def _create_firestore_client():
        # Initialize Firestore client
        cred = credentials.Certificate('Firebase/ainepse-firebaseKey.json')
        firebase_admin.initialize_app(cred)
        return firestore.client()
    
    # Save the dict of a company in Database    
    @staticmethod
    def save_doc_DB(doc_Name, dict, collection_Name):
        # Save the Dict to the database
        doc_ref = FirestoreManager._get_instance().collection(collection_Name).document(doc_Name).set(dict)
        return

    @staticmethod
    def get_doc_DB(doc_Name, collection_Name):
        docref = FirestoreManager._get_instance().collection(collection_Name).document(doc_Name)
        doc = docref.get()
        if doc.exists: return doc._data
        return None
    
    @staticmethod
    def get_collectionRef_DB(collection_Name):
        return FirestoreManager._get_instance().collection(collection_Name)
    
    @staticmethod
    def delete_Collection(collection_Name):
        collection_ref = FirestoreManager._get_instance().collection(collection_Name)
        batchSize = 500
        FirestoreManager._delete_Collection_InBatches(collection_ref, batchSize)

    @staticmethod
    def _delete_Collection_InBatches(coll_ref, batch_size):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0
        for doc in docs:
            # print(f'Deleting doc {doc.id} => {doc.to_dict()}')
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            return FirestoreManager._delete_Collection_InBatches(coll_ref, batch_size)
    
    # # Save file
    # def save_to_csv(self, company, collection_Name):
    #     data_dict = self.get_DB(company,collection_Name)
    #     data_macd = data_dict["MACD"]
    #     data_rsi = data_dict["RSI"]
    #     data = data_macd
    #     # Write data to CSV file
    #     with open('output.csv', 'w', newline='') as csvfile:
            
    #         fieldnames = data.keys()

    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
    #         # Write header
    #         writer.writeheader()
            
    #         # Transpose the data and write rows
    #         rows = zip(*data.values())
    #         for row in rows:
    #             writer.writerow(dict(zip(fieldnames, row)))
