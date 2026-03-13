"""
APScheduler pipeline
Runs automatically in the background alongside FastAPI.

Jobs:
  - Every 6 hours  → fetch TMDB trending + compute trend scores + store to Firestore
  - Every 24 hours → rebuild FAISS vector index from latest drama corpus
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


# ── Pipeline job functions ────────────────────────────────────────────────────

def run_ingestion_job():
    """Fetch latest K-dramas from TMDB and score trends. Runs every 6h."""
    try:
        logger.info("[Scheduler] Starting TMDB ingestion job…")
        from data_ingestion.tmdb_ingestion import run_ingestion
        from data_ingestion.trend_scorer import run_trend_scoring

        dramas = run_ingestion(limit=30)
        ranked = run_trend_scoring(dramas, limit=20)
        logger.info(f"[Scheduler] Ingestion complete. {len(ranked)} dramas ranked.")
    except Exception as e:
        logger.error(f"[Scheduler] Ingestion job failed: {e}", exc_info=True)


def run_training_job():
    """Rebuild FAISS index from latest Firestore drama corpus. Runs every 24h."""
    try:
        logger.info("[Scheduler] Starting ML model retraining job…")
        from ml_pipeline.train import run_training
        run_training()
        logger.info("[Scheduler] ML retraining complete.")
    except Exception as e:
        logger.error(f"[Scheduler] Training job failed: {e}", exc_info=True)


def run_pipeline_once():
    """
    Utility for testing: runs both jobs sequentially once.
    Usage: python -c "from schedulers.scheduler import run_pipeline_once; run_pipeline_once()"
    """
    logger.info("Running full pipeline once (manual trigger)…")
    run_ingestion_job()
    run_training_job()


# ── Scheduler lifecycle ───────────────────────────────────────────────────────

def _job_listener(event):
    if event.exception:
        logger.error(f"[Scheduler] Job {event.job_id} raised: {event.exception}")
    else:
        logger.info(f"[Scheduler] Job {event.job_id} finished OK.")


def start_scheduler():
    """Start the background scheduler. Call once at app startup."""
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.warning("[Scheduler] Already running — skipping start.")
        return

    _scheduler = BackgroundScheduler(
        job_defaults={"misfire_grace_time": 600, "coalesce": True},
        timezone="UTC",
    )
    _scheduler.add_listener(_job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

    # Data ingestion: every 6 hours
    _scheduler.add_job(
        run_ingestion_job,
        trigger=IntervalTrigger(hours=6),
        id="tmdb_ingestion",
        name="TMDB K-Drama Ingestion + Trend Scoring",
        replace_existing=True,
        # Run once at startup too (after 30s delay to let app fully boot)
        next_run_time=None,
    )

    # ML retraining: every 24 hours
    _scheduler.add_job(
        run_training_job,
        trigger=IntervalTrigger(hours=24),
        id="ml_retraining",
        name="FAISS Model Retraining",
        replace_existing=True,
        next_run_time=None,
    )

    _scheduler.start()
    logger.info("[Scheduler] APScheduler started. Jobs: tmdb_ingestion (6h), ml_retraining (24h).")

    # Trigger first run immediately in a separate thread
    import threading
    threading.Thread(target=run_ingestion_job, daemon=True, name="initial-ingestion").start()


def stop_scheduler():
    """Gracefully stop the scheduler. Call at app shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] APScheduler stopped.")
