import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Read JSON from environment variable
firebase_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_admin._apps:
    if firebase_json:
        cred_dict = json.loads(firebase_json.replace('\\n', '\n'))
        cred = credentials.Certificate(cred_dict)
    else:
        raise Exception("FIREBASE_CREDENTIALS env variable missing")

    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_db():
    return db
