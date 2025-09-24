"""
Exception handlers for the FastAPI application.

This module contains all global exception handlers to maintain clean
architecture and separation of concerns.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from loguru import logger

from ..models import APIResponse



async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with consistent format.
    
    Args:
        request: The FastAPI request object
        exc: The HTTP exception that was raised
        
    Returns:
        JSONResponse: Formatted error response
    """
    logger.warning(
        f"HTTP Exception {exc.status_code}: {exc.detail} for {request.url}"
    )

    # Map status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED", 
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }

    response = APIResponse(
        success=False,
        message=exc.detail,
        error_code=error_code_map.get(exc.status_code, "HTTP_ERROR"),
        data=None,
    )
    return JSONResponse(
        status_code=exc.status_code, content=response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unhandled exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The general exception that was raised
        
    Returns:
        JSONResponse: Formatted error response
    """
    logger.exception(f"Unhandled exception for {request.url}: {exc}")
    response = APIResponse(
        success=False,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        data=None,
    )
    return JSONResponse(status_code=500, content=response.model_dump())


async def not_found_handler(request: Request, exc) -> JSONResponse:
    """
    Handle 404 errors.
    
    Args:
        request: The FastAPI request object
        exc: The 404 exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    response = APIResponse(
        success=False, 
        message=exc.detail, 
        error_code="NOT_FOUND", 
        data=None
    )
    return JSONResponse(status_code=404, content=response.model_dump())


async def internal_error_handler(request: Request, exc) -> JSONResponse:
    """
    Handle 500 errors.
    
    Args:
        request: The FastAPI request object
        exc: The 500 exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"Internal server error: {exc}")
    response = APIResponse(
        success=False,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        data=None,
    )
    return JSONResponse(status_code=500, content=response.model_dump())


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: The FastAPI application instance
    """
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(Exception)(general_exception_handler)
    app.exception_handler(404)(not_found_handler)
    app.exception_handler(500)(internal_error_handler)
