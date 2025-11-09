"""
Video clip extraction service with search integration.

Handles the business logic of finding and extracting video clips
based on different search criteria (text, image, caption).
"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger

from multimodal_mcp.config import get_settings
from multimodal_mcp.video.search_video import VideoSearchEngine
from multimodal_mcp.video.ingestion.tools import extract_video_clip
from multimodal_mcp.models import ToolResult

logger = logger.bind(name="ClipExtractor")
settings = get_settings()


class ClipExtractionError(Exception):
    """Custom exception for clip extraction failures."""

    pass


class VideoClipExtractor:
    """
    Service class for extracting video clips based on search results.

    Separates search logic from clip extraction, making both more testable.
    """

    def __init__(self):
        """Initialize the clip extractor with search engine."""
        try:
            self.search_engine = VideoSearchEngine()
        except RuntimeError as e:
            logger.error(f"Failed to initialize search engine: {e}")
            raise ClipExtractionError(
                "Video search is not available. Please ensure videos are processed first."
            ) from e

        # Prepare output directory
        self.shared_media_dir = Path(settings.SHARED_MEDIA_DIR)
        self.ai_videos_dir = self.shared_media_dir / "videos" / "ai_responses"
        self.ai_videos_dir.mkdir(parents=True, exist_ok=True)

    def _get_video_path(self, video_id: str) -> str:
        """
        Retrieve video file path from database.

        Args:
            video_id: Video identifier

        Returns:
            Absolute path to video file

        Raises:
            ClipExtractionError: If video not found
        """
        results = self.search_engine.video_table.where(
            self.search_engine.video_table.video_id == video_id
        ).collect()

        if not results or not results[0].get("video"):
            raise ClipExtractionError(f"Video not found for video_id: {video_id}")

        return results[0]["video"]

    def _extract_clip(
        self, video_path: str, start_time: float, end_time: float
    ) -> Path:
        """
        Extract video clip and save to output directory.

        Args:
            video_path: Source video file path
            start_time: Clip start time in seconds
            end_time: Clip end time in seconds

        Returns:
            Path to extracted clip (relative to shared_media)

        Raises:
            ClipExtractionError: If extraction fails
        """
        destination = self.ai_videos_dir / f"{uuid.uuid4()}.mp4"

        try:
            extract_video_clip(
                video_path=video_path,
                start_time=start_time,
                end_time=end_time,
                output_path=destination,
            )
        except (IOError, OSError) as e:
            raise ClipExtractionError(
                "Failed to extract video clip. The video file may be corrupted or inaccessible."
            ) from e
        except Exception as e:
            raise ClipExtractionError(
                "An unexpected error occurred while extracting the video clip."
            ) from e

        return destination.relative_to(self.shared_media_dir)

    def extract_from_text_query(
        self, query: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        """
        Extract clip based on text query (combines speech + caption search).

        Args:
            query: User's text query
            video_ids: Optional list of video ids to search

        Returns:
            ToolResult with video path or error message
        """
        try:
            # Perform parallel searches
            speech_results = self.search_engine.search_by_speech(
                query, settings.VIDEO_CLIP_SPEECH_SEARCH_TOP_K, video_ids=video_ids
            )
            caption_results = self.search_engine.search_by_caption(
                query, settings.VIDEO_CLIP_CAPTION_SEARCH_TOP_K, video_ids=video_ids
            )

            # Check if any results found
            if not speech_results and not caption_results:
                logger.info(f"No matching segments found for query: '{query}'")
                return {
                    "type": "text",
                    "content": "No matching video segments found. Try rephrasing your query or check if videos are processed.",
                }

            # Select best result based on similarity scores
            best_clip = self._select_best_clip(speech_results, caption_results)

            # Get video path and extract clip
            video_path = self._get_video_path(best_clip["video_id"])
            relative_path = self._extract_clip(
                video_path, best_clip["start_time"], best_clip["end_time"]
            )

            logger.success(f"Extracted clip → {relative_path}")
            return {"type": "video", "content": str(relative_path.as_posix())}

        except ClipExtractionError as e:
            logger.error(f"Clip extraction failed: {e}")
            return {"type": "text", "content": str(e)}
        except Exception as e:
            logger.exception(f"Unexpected error in extract_from_text_query: {e}")
            return {
                "type": "text",
                "content": "An unexpected error occurred. Please try again or contact support.",
            }

    def extract_from_image(
        self, image_base64: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        """
        Extract clip based on visual similarity to provided image.

        Args:
            image_base64: Base64 encoded query image
            video_ids: Optional list of video ids to search

        Returns:
            ToolResult with video path or error message
        """
        try:
            # Perform image similarity search
            results = self.search_engine.search_by_image(
                image_base64,
                settings.VIDEO_CLIP_IMAGE_SEARCH_TOP_K,
                video_ids=video_ids,
            )

            # Check if any results found
            if not results:
                logger.info("No similar frames found for provided image")
                return {
                    "type": "text",
                    "content": "No visually similar video segments found. Try a different image or check if videos are processed.",
                }

            top_clip = results[0]

            # Get video path and extract clip
            video_path = self._get_video_path(top_clip["video_id"])
            relative_path = self._extract_clip(
                video_path, top_clip["start_time"], top_clip["end_time"]
            )

            logger.success(f"Extracted clip from image query → {relative_path}")
            return {"type": "video", "content": str(relative_path.as_posix())}

        except ClipExtractionError as e:
            logger.error(f"Clip extraction failed: {e}")
            return {"type": "text", "content": str(e)}
        except Exception as e:
            logger.exception(f"Unexpected error in extract_from_image: {e}")
            return {
                "type": "text",
                "content": "An unexpected error occurred. Please try again or contact support.",
            }

    def _select_best_clip(
        self, speech_results: List[Dict], caption_results: List[Dict]
    ) -> Dict:
        """
        Select the best clip from combined search results.

        Args:
            speech_results: Results from speech search
            caption_results: Results from caption search

        Returns:
            Best matching clip dictionary
        """
        speech_sim = speech_results[0]["similarity"] if speech_results else 0
        caption_sim = caption_results[0]["similarity"] if caption_results else 0

        return speech_results[0] if speech_sim >= caption_sim else caption_results[0]


class VideoQuestionAnswerer:
    """
    Service for answering questions about video content.

    Uses caption search to retrieve relevant information.
    """

    def __init__(self):
        """Initialize the question answerer with search engine."""
        try:
            self.search_engine = VideoSearchEngine()
        except RuntimeError as e:
            logger.error(f"Failed to initialize search engine: {e}")
            raise ClipExtractionError(
                "Video search is not available. Please ensure videos are processed first."
            ) from e

    def answer_question(
        self, query: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        """
        Retrieve relevant captions to answer a user query.

        Args:
            query: User question or search text
            video_ids: Optional list of video ids to search

        Returns:
            ToolResult with answer text or error message
        """
        try:
            # Search for relevant captions
            caption_info = self.search_engine.get_caption_info(
                query, settings.QUESTION_ANSWER_TOP_K, video_ids=video_ids
            )

            # Check if any results found
            if not caption_info:
                logger.info(f"No relevant captions found for query: '{query}'")
                return {
                    "type": "text",
                    "content": "No relevant information found in the videos. Try rephrasing your question or check if videos are processed.",
                }

            # Build answer with video references
            answer = self._format_answer_with_sources(caption_info)

            logger.info(f"Answer extracted: → {len(caption_info)} captions.")
            return {"type": "text", "content": answer}

        except Exception as e:
            logger.exception(f"Unexpected error in answer_question: {e}")
            return {
                "type": "text",
                "content": "An unexpected error occurred while processing your question. Please try again.",
            }

    def _format_answer_with_sources(self, caption_info: List[Dict]) -> str:
        """
        Format answer with video sources for citations.

        Args:
            caption_info: List of caption results with video IDs

        Returns:
            Formatted answer string with sources
        """
        video_name_list = []
        for entry in caption_info:
            video_result = self.search_engine.video_table.where(
                self.search_engine.video_table.video_id == entry["video_id"]
            ).collect()

            if video_result and "video_name" in video_result:
                video_name_list.append(video_result["video_name"][0])
            else:
                video_name_list.append("Unknown")

        return "\n\n".join(
            f"Video: {video_name}\nContent: {entry['caption']}"
            for video_name, entry in zip(video_name_list, caption_info)
        )
