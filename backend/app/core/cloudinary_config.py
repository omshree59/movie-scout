import cloudinary
from app.core.config import settings

def init_cloudinary():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

def get_movie_poster_url(public_id: str) -> str:
    return cloudinary.CloudinaryImage(public_id).build_url(
        width=300, height=450, crop="fill", quality="auto"
    )
