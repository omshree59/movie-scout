from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "MovieScout"
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase_credentials.json"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # TMDB
    TMDB_API_KEY: str = ""

    # ML Settings
    MODELS_PATH: str = os.path.join(os.path.dirname(__file__), "../../ml_pipeline/saved_models")
    DATA_PATH: str = os.path.join(os.path.dirname(__file__), "../../ml_pipeline/data")

    class Config:
        env_file = ".env"

settings = Settings()
