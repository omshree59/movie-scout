from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import movies, users
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle manager."""
    # ── Startup ─────────────────────────────────────────────────────────────
    logger.info("MovieScout API starting up…")

    # Start the background scheduler (TMDB ingestion + ML retraining)
    try:
        from schedulers.scheduler import start_scheduler
        start_scheduler()
        logger.info("APScheduler started ✓")
    except Exception as e:
        logger.warning(f"Scheduler could not start (non-fatal): {e}")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    try:
        from schedulers.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    logger.info("MovieScout API shut down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Advanced Netflix-style K-Drama Recommendation Engine API",
    lifespan=lifespan,
)

# CORS Configuration
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
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
