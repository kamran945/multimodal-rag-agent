import pixeltable as pxt
from PIL import Image

from loguru import logger


from loguru import logger
import pixeltable as pxt


# -------------------------------------------------------------------------
# Audio Pipeline helper functions
# -------------------------------------------------------------------------
@pxt.udf
def extract_text_from_chunk(transcript: pxt.type_system.Json) -> str:
    """
    Extract text from a transcript JSON object.
    Handles missing keys and None values gracefully.
    Logs cases where transcript is None or missing the 'text' key.
    """
    if not transcript:
        logger.warning("Transcript chunk is None")
        return ""

    text = transcript.get("text")
    if text is None:
        logger.warning(f"Transcript chunk missing 'text' key: {transcript}")
        return ""

    cleaned_text = str(text).strip()

    return cleaned_text


# -------------------------------------------------------------------------
# Frame Pipeline helper functions
# -------------------------------------------------------------------------
@pxt.udf
def resize_image(
    image: pxt.type_system.Image, width: int, height: int
) -> pxt.type_system.Image:
    """
    Resize a Pixeltable Image column to the given width and height using Pixeltable's thumbnail function.
    Returns the resized image.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a pxt.type_system.Image")

    try:
        return image.thumbnail((width, height))
        # resized = image.resize((width, height))
        # return resized

    except Exception as e:
        logger.exception(f"Failed to resize image: {e}")
        return image  # fallback to original
