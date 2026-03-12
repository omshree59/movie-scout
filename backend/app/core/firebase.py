import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import os

_db = None

def init_firebase():
    global _db
    if not firebase_admin._apps:
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
