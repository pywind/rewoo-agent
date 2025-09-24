
"""
FastAPI Application Factory.

This module contains the FastAPI application factory and configuration.
"""


from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from ..helpers.log_factory import setup_logging
from .exception_handler import register_exception_handlers

from ..rewoo_agent.controllers import agent_routers
from ..rewoo_agent.tools import register_default_tools
from ..config.settings import settings


class ApplicationFactory:
    """Factory class for creating FastAPI application instances."""

    def __init__(self):
        """Initialize the application factory."""
        self.app = None
        self.thread_pool = ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="app-worker"
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """Handle application lifespan events."""
        logger.info("Setup logging")
        setup_logging(
            app_name=settings.api.app_name,
        )
        # Startup
        logger.info(f"App name: {settings.api.app_name} starting up...")
        logger.info("Registering tools...")
        register_default_tools()
        logger.info("Tools registered successfully")
        try:
            yield
        finally:
            logger.info("API shutdown complete")


    def create_app(self) -> FastAPI:
        """
        Create and configure FastAPI application.

        Returns:
            FastAPI: Configured FastAPI application instance
        """
        # Create FastAPI app optimized for Gunicorn deployment
        app = FastAPI(
            title=settings.api.app_name,
            description="API for ReWOO (Reasoning without Observation) - A multi-step planner and executor system",
            version="1.0.0",
            docs_url="/docs",
            lifespan=self._lifespan,
            # Optimized for production
            openapi_url="/openapi.json"
        )

        # Configure middleware
        self._configure_middleware(app)

        # Register routes
        self._register_routes(app)

        # Register exception handlers
        self._register_exception_handlers(app)

        self.app = app
        return app

    def _configure_middleware(self, app: FastAPI) -> None:
        """Configure application middleware optimized for Gunicorn + K8s."""
        
        # CORS middleware - K8s ingress handles compression and security
        cors_origins = ["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "Accept",
                "Origin",
                "User-Agent",
                "Cache-Control"
            ],
            max_age=3600,  # Cache preflight requests for 1 hour
        )

    def _register_routes(self, app: FastAPI) -> None:
        """Register all API routes."""

        app.include_router(
            agent_routers.router,
            prefix=f"{settings.api.prefix}",
            # dependencies=[Depends(get_bearer_token)],  # TODO: Add authentication
        )



    def _register_exception_handlers(self, app: FastAPI) -> None:
        """Register global exception handlers."""
        register_exception_handlers(app)
