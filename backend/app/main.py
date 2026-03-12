from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import movies, users
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Advanced Netflix-style Movie Recommendation Engine API",
)

# CORS Configuration (allow React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(movies.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
