"""FastAPI application for webhook handling."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routers import webhooks_router
from bot.database import init_db
from bot.utils import logger
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    logger.info("Starting FastAPI application...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="GPSkilledGuardian API",
    description="Payment webhook API for GPSkilledGuardian Discord bot",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks_router)


@app.get("/")
async def root():
    """Root endpoint.
    
    Returns:
        API information
    """
    return {
        "name": "GPSkilledGuardian API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.dev_mode,
        log_level=settings.log_level.lower()
    )
