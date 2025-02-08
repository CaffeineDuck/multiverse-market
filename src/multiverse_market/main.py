import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import router
from .config import settings
from .exceptions import MultiverseMarketException
from .logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A marketplace system for trading across multiple universes",
    version=settings.VERSION,
    debug=settings.DEBUG,
)


@app.exception_handler(MultiverseMarketException)
async def market_exception_handler(_: Request, exc: MultiverseMarketException):
    """Handle market-specific exceptions."""
    logger.info(f"Handling market exception: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Multiverse Market!",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
