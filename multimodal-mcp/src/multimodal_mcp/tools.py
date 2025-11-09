"""
MCP Video Tools - Clean Interface Layer (Updated with video_ids)

Each tool now accepts optional video_ids parameter for targeted search.
If video_ids is provided, search only in those videos.
If not provided (or empty), search in all videos.
"""

from typing import List, Optional
from loguru import logger

from multimodal_mcp.models import ToolResult
from multimodal_mcp.video.ingestion.video_processor import VideoProcessor
from multimodal_mcp.validators import (
    ValidationError,
    VideoPathValidator,
    UserQueryValidator,
    ImageBase64Validator,
    VideoNamesValidator,
    VideoIdValidator,
)
from multimodal_mcp.video.clip_extractor import (
    VideoClipExtractor,
    VideoQuestionAnswerer,
    ClipExtractionError,
)

logger = logger.bind(name="MCPVideoTools")

# Initialize services (singleton pattern)
_video_processor = None
_clip_extractor = None
_question_answerer = None


def _get_video_processor() -> VideoProcessor:
    """Lazy initialization of video processor."""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor


def _get_clip_extractor() -> VideoClipExtractor:
    """Lazy initialization of clip extractor."""
    global _clip_extractor
    if _clip_extractor is None:
        try:
            _clip_extractor = VideoClipExtractor()
        except ClipExtractionError as e:
            logger.error(f"Failed to initialize clip extractor: {e}")
            raise
    return _clip_extractor


def _get_question_answerer() -> VideoQuestionAnswerer:
    """Lazy initialization of question answerer."""
    global _question_answerer
    if _question_answerer is None:
        try:
            _question_answerer = VideoQuestionAnswerer()
        except ClipExtractionError as e:
            logger.error(f"Failed to initialize question answerer: {e}")
            raise
    return _question_answerer


# =====================================================================
# PUBLIC TOOL FUNCTIONS (Updated with video_ids)
# =====================================================================


def process_video(video_path: str, video_id: str) -> bool:
    """
    Process a video file end-to-end (frames + audio + embeddings).
    """
    try:
        validated_path = VideoPathValidator.validate(video_path)
        validated_id = VideoIdValidator.validate(video_id)

        processor = _get_video_processor()
        return processor.add_video(
            video_path=str(validated_path), video_id=validated_id
        )

    except ValidationError as e:
        logger.warning(f"Video processing validation failed: {e}")
        return False
    except Exception as e:
        logger.exception(f"Failed to process video '{video_path}': {e}")
        return False


def delete_video(video_id: str) -> bool:
    """
    Delete a video and all associated data.
    """
    try:
        validated_id = VideoIdValidator.validate(video_id)

        processor = _get_video_processor()
        success = processor.delete_video(validated_id)

        if success:
            logger.info(f"✅ Successfully deleted video: {video_id}")
        else:
            logger.warning(f"⚠️ No video found for deletion: {video_id}")

        return success

    except ValidationError as e:
        logger.warning(f"Video deletion validation failed: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error in delete_video: {e}")
        return False


def get_video_clip_from_user_query(
    user_query: str, video_ids: Optional[List[str]] = None
) -> ToolResult:
    """
    Extract a relevant video clip based on text query.

    ✅ NEW: If video_ids provided, search only in those videos.
    Otherwise, search all videos.
    """
    try:
        validated_query = UserQueryValidator.validate(user_query)
        validated_ids = VideoNamesValidator.validate(video_ids)

        if validated_ids:
            logger.info(f"Searching in {len(validated_ids)} selected videos")
        else:
            logger.info("Searching in all videos")

        extractor = _get_clip_extractor()
        return extractor.extract_from_text_query(validated_query, validated_ids)

    except ValidationError as e:
        logger.warning(f"Input validation failed: {e}")
        return {"type": "text", "content": f"Invalid input: {str(e)}"}
    except ClipExtractionError as e:
        logger.error(f"Clip extraction initialization failed: {e}")
        return {"type": "text", "content": str(e)}
    except Exception as e:
        logger.exception(f"Unexpected error in get_video_clip_from_user_query: {e}")
        return {
            "type": "text",
            "content": "An unexpected error occurred. Please try again or contact support.",
        }


def get_video_clip_from_image(
    image_base64: str, video_ids: Optional[List[str]] = None
) -> ToolResult:
    """
    Extract clip based on visual similarity to provided image.

    ✅ NEW: If video_ids provided, search only in those videos.
    """
    try:
        validated_image = ImageBase64Validator.validate(image_base64)
        validated_ids = VideoNamesValidator.validate(video_ids)

        if validated_ids:
            logger.info(f"Searching in {len(validated_ids)} selected videos")
        else:
            logger.info("Searching in all videos")

        extractor = _get_clip_extractor()
        return extractor.extract_from_image(validated_image, validated_ids)

    except ValidationError as e:
        logger.warning(f"Input validation failed: {e}")
        return {"type": "text", "content": f"Invalid input: {str(e)}"}
    except ClipExtractionError as e:
        logger.error(f"Clip extraction initialization failed: {e}")
        return {"type": "text", "content": str(e)}
    except Exception as e:
        logger.exception(f"Unexpected error in get_video_clip_from_image: {e}")
        return {
            "type": "text",
            "content": "An unexpected error occurred. Please try again or contact support.",
        }


def ask_question_about_video(
    user_query: str, video_ids: Optional[List[str]] = None
) -> ToolResult:
    """
    Retrieve relevant captions to answer a user query.

    ✅ NEW: If video_ids provided, search only in those videos.
    """
    try:
        validated_query = UserQueryValidator.validate(user_query)
        validated_ids = VideoNamesValidator.validate(video_ids)

        if validated_ids:
            logger.info(f"Searching in {len(validated_ids)} selected videos")
        else:
            logger.info("Searching in all videos")

        answerer = _get_question_answerer()
        return answerer.answer_question(validated_query, validated_ids)

    except ValidationError as e:
        logger.warning(f"Input validation failed: {e}")
        return {"type": "text", "content": f"Invalid input: {str(e)}"}
    except ClipExtractionError as e:
        logger.error(f"Question answerer initialization failed: {e}")
        return {"type": "text", "content": str(e)}
    except Exception as e:
        logger.exception(f"Unexpected error in ask_question_about_video: {e}")
        return {
            "type": "text",
            "content": "An unexpected error occurred while processing your question. Please try again.",
        }
