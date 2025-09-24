from src.core import init_app
from src.config.settings import settings


# Create FastAPI application
app = init_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:src",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info"
    )
