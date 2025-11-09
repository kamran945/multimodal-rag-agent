"""
Error Handlers - Centralized error handling decorators for API endpoints
"""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
from loguru import logger

from multimodal_api.config.constants import HTTP_INTERNAL_ERROR


def handle_api_errors(operation_name: str):
    """
    Decorator for consistent error handling across API endpoints.

    Catches all exceptions, logs them, and converts to HTTPException.
    HTTPException instances are re-raised as-is to preserve status codes.

    Args:
        operation_name: Human-readable name of the operation for logging

    Returns:
        Decorator function

    Example:
        @router.post("/upload")
        @handle_api_errors("image upload")
        async def upload_image(file: UploadFile):
            # ... your logic here ...
            return {"success": True}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is (they already have proper status codes)
                raise
            except Exception as e:
                # Log the full exception with traceback
                logger.exception(f"Error in {operation_name}: {e}")
                # Convert to HTTP 500 error
                raise HTTPException(
                    status_code=HTTP_INTERNAL_ERROR,
                    detail=f"{operation_name.capitalize()} failed: {str(e)}",
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error in {operation_name}: {e}")
                raise HTTPException(
                    status_code=HTTP_INTERNAL_ERROR,
                    detail=f"{operation_name.capitalize()} failed: {str(e)}",
                )

        # Return appropriate wrapper based on whether function is async
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_endpoint_call(endpoint_name: str):
    """
    Decorator to log API endpoint calls with parameters (excluding sensitive data).

    Args:
        endpoint_name: Name of the endpoint for logging

    Returns:
        Decorator function

    Example:
        @router.get("/media/{file_id}")
        @log_endpoint_call("serve_media")
        async def serve_media(file_id: str):
            # ... your logic ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Extract route params (exclude 'self', 'request', etc.)
            params = {
                k: v
                for k, v in kwargs.items()
                if k not in ["request", "fastapi_request", "bg_tasks"]
            }

            logger.info(f"API Call: {endpoint_name} | Params: {params}")
            result = await func(*args, **kwargs)
            logger.debug(f"API Success: {endpoint_name}")
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            params = {
                k: v
                for k, v in kwargs.items()
                if k not in ["request", "fastapi_request", "bg_tasks"]
            }

            logger.info(f"API Call: {endpoint_name} | Params: {params}")
            result = func(*args, **kwargs)
            logger.debug(f"API Success: {endpoint_name}")
            return result

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class APIError(Exception):
    """
    Base exception for API-specific errors.
    Allows attaching status code and detail message.
    """

    def __init__(self, detail: str, status_code: int = HTTP_INTERNAL_ERROR):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class ValidationError(APIError):
    """Exception for input validation errors (400)"""

    def __init__(self, detail: str):
        super().__init__(detail, status_code=400)


class NotFoundError(APIError):
    """Exception for resource not found errors (404)"""

    def __init__(self, detail: str):
        super().__init__(detail, status_code=404)


class ForbiddenError(APIError):
    """Exception for forbidden access errors (403)"""

    def __init__(self, detail: str):
        super().__init__(detail, status_code=403)
