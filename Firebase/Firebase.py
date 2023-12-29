import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import sys
from dotenv import load_dotenv
from os.path import dirname, abspath

class BuffettNoEnvironment(Exception):
    pass

class FirestoreManager:
    # Make sure that I only initialize this once during each run
    def __init__(self, env) -> None:
        # Credentials
        cred = credentials.Certificate(r"D:\AI\ainepse-firebaseKey.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def users_ref(self):
        return self.db.collection(u'buffetters')