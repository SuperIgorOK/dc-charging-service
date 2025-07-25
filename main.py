import logging
from contextlib import asynccontextmanager

from aredis_om import Migrator
from fastapi import FastAPI
from apps.routers.session_router import router as session_router
from apps.routers.station_router import router as station_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    try:
        migrator = Migrator()
        await migrator.run()
        logger.info("Redis index created successfully.")
    except Exception as e:
        logger.error(f"Failed to create Redis indices: {e}")
        raise

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "OK"}


app.include_router(session_router, prefix="/stations")
app.include_router(station_router, prefix="")
