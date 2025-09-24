#!/usr/bin/env python3
"""
Startup script for Ground Truth Generation API.

This script provides an easy way to start the API server with proper configuration.
"""

import sys
import uvicorn

from loguru import logger
from src.config.settings import settings

class StartupManager:
    """Manager class for application startup operations."""

    def __init__(self):
        """Initialize the startup manager."""
        self.logger = logger


    def start_server(self):
        """Start the FastAPI server."""
        try:
            uvicorn.run(
                "src.main:app",
                host=settings.api.host,
                port=settings.api.port,
                reload=settings.api.debug,
                log_level="info"
            )
        except KeyboardInterrupt:
            self.logger.info("\n👋 Shutting down server...")
        except Exception as e:
            self.logger.exception(f"\n❌ Server error: {e}")
            sys.exit(1)


def main():
    """Main startup function."""
    startup_manager = StartupManager()


    # Start server
    startup_manager.start_server()


if __name__ == "__main__":
    main()
