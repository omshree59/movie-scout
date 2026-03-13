import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import os
import json

_db = None

def init_firebase():
    global _db
    if not firebase_admin._apps:
        # Check for direct JSON string in environment (best for Railway/Heroku)
        env_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
        if env_json:
            try:
                cred_dict = json.loads(env_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                return _db
            except Exception as e:
                print(f"ERROR parsing FIREBASE_CREDENTIALS_JSON from env: {e}")
        
        # Fallback to local file path
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Initialize without credentials for development (limited features)
            print("WARNING: Firebase credentials not found. Using emulator/mock mode.")
            firebase_admin.initialize_app()
    _db = firestore.client()
    return _db

def get_db():
    global _db
    if _db is None:
        init_firebase()
    return _db
