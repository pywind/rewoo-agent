from fastapi import FastAPI
from .app import ApplicationFactory



# Global application factory instance
app_factory = ApplicationFactory()


def init_app() -> FastAPI:
    """
    Create FastAPI application instance.

    Returns:
        FastAPI: Configured application instance
    """
    return app_factory.create_app()
