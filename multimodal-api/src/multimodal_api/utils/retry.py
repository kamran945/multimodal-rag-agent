"""
Retry utilities using tenacity - only for API calls
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
from loguru import logger

logger = logger.bind(name="Retry")


# API-specific exceptions that are worth retrying
API_RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
)


# Retry decorator ONLY for API calls (MCP client, LLM calls, etc.)
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(API_RETRYABLE_EXCEPTIONS),
    before_sleep=before_sleep_log(logger, "WARNING"),
    after=after_log(logger, "INFO"),
    reraise=True,
)


# More aggressive retry for critical API calls
critical_api_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(API_RETRYABLE_EXCEPTIONS),
    before_sleep=before_sleep_log(logger, "WARNING"),
    after=after_log(logger, "INFO"),
    reraise=True,
)
