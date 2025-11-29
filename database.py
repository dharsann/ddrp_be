import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

def get_db():
    return db
