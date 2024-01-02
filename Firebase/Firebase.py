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
    # Initialize once per each run
    # NOTE Alternate solution : Singleton Pattern
    def __init__(self, env) -> None:
        # Credentials
        cred = credentials.Certificate(r"D:\AI\ainepse-firebaseKey.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()