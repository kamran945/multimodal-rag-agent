import pathlib
from typing import Any, Optional
import io
import base64
from PIL import Image
import pixeltable as pxt
from groq import Groq
import io
import base64
import asyncio
import json
from loguru import logger
from typing import Any, Optional
from PIL import Image
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
    wait_fixed,
    RetryCallState,
)
from groq import RateLimitError

# Optional: load key from environment or .env file
from dotenv import load_dotenv
import os

load_dotenv()

_GROQ_CLIENT = None


# Configure module logger (Pixeltable will respect this)

logger = logger.bind(name=__name__)

# ---------------------------
# Helpers
# ---------------------------


def _groq_client() -> Groq:
    """Lazy singleton Groq client"""
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY environment variable or .env entry.")
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def _extract_reset_time(e: Exception) -> Optional[float]:
    """
    Extract rate-limit reset time from exception response headers (if available).
    Returns number of seconds to wait, or None if not present.
    """
    try:
        headers = getattr(e, "response", {}).headers
        if headers and "x-ratelimit-reset-seconds" in headers:
            return float(headers["x-ratelimit-reset-seconds"])
    except Exception:
        pass
    return None


# ---------------------------
# Pixeltable UDF
# ---------------------------
@pxt.udf
async def transcriptions(
    audio: pxt.Audio,
    *,
    model: str = "whisper-large-v3",
    model_kwargs: Optional[dict[str, Any]] = None,
) -> dict:
    """
    Transcribes audio using Groq's Whisper endpoint.

    Equivalent to Groq's `audio.transcriptions.create` API.
    Docs: https://console.groq.com/docs/audio

    Args:
        audio: The audio to transcribe (Pixeltable Audio column or file path).
        model: Groq model for transcription. Defaults to 'whisper-large-v3'.
        model_kwargs: Extra parameters for the Groq API.

    Returns:
        A dictionary containing the transcription text and metadata.

    Example:
        >>> tbl.add_computed_column(
        ...     transcription=transcriptions(tbl.audio, model='whisper-large-v3')
        ... )
    """
    if model_kwargs is None:
        model_kwargs = {}

    file_path = pathlib.Path(audio)
    client = _groq_client()

    # Groq SDK isn't async, so run it in a thread pool
    import asyncio

    loop = asyncio.get_event_loop()

    def _sync_transcribe():
        with open(file_path, "rb") as f:
            return client.audio.transcriptions.create(
                file=f, model=model, **model_kwargs
            )

    transcription = await loop.run_in_executor(None, _sync_transcribe)
    return (
        transcription.model_dump()
        if hasattr(transcription, "dict")
        else dict(transcription)
    )


# ---------------------------
# Pixeltable UDF
# ---------------------------
@pxt.udf
async def vision(
    prompt: str,
    image: Image.Image,
    *,
    model: str = "llama-3.2-11b-vision-preview",
    model_kwargs: Optional[dict[str, Any]] = None,
    _runtime_ctx: Optional[Any] = None,
) -> str:
    """
    Groq Vision UDF with Tenacity retry + structured logging.
    Automatically backs off on rate limits and logs retry attempts.
    """

    if model_kwargs is None:
        model_kwargs = {}

    # Convert image to base64
    bytes_arr = io.BytesIO()
    image.save(bytes_arr, format="PNG")
    b64_bytes = base64.b64encode(bytes_arr.getvalue()).decode("utf-8")

    # Prepare Groq chat message
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_bytes}"},
                },
            ],
        }
    ]

    # Retry logic for rate limits with dynamic wait time + exponential backoff
    def _wait_strategy(retry_state: RetryCallState):
        last_exc = retry_state.outcome.exception() if retry_state.outcome else None
        if isinstance(last_exc, RateLimitError):
            reset_time = _extract_reset_time(last_exc)
            if reset_time:
                logger.warning(
                    f"Rate limit hit — waiting {reset_time:.1f}s before retry"
                )
                return wait_fixed(reset_time)
        return wait_exponential(multiplier=1, min=2, max=30)(retry_state)

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=_wait_strategy,
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logger, logger.warning),
    )
    def _sync_infer():
        """Synchronous Groq inference call with retry + logging."""
        client = _groq_client()
        # logger.info(f"Sending vision prompt to {model}")
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            **model_kwargs,
        )
        return response

    # Run Groq call in a background thread (Pixeltable-safe)
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(None, _sync_infer)
    except RateLimitError as e:
        logger.error(f"Exhausted retries after rate limit errors: {e}")
        raise

    # Parse response safely
    try:
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to parse Groq response: {e}")
        return json.dumps(response, indent=2)
