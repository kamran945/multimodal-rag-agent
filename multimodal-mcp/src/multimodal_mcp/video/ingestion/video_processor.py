import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, TYPE_CHECKING, Any
from enum import Enum

import pixeltable as pxt
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.video import FrameIterator
from pixeltable.functions import openai, video, huggingface
from pixeltable.functions.video import extract_audio
from loguru import logger

import multimodal_mcp.video.ingestion.registry as registry
from multimodal_mcp.config import get_settings
from multimodal_mcp.video.ingestion.helper import resize_image, extract_text_from_chunk
import multimodal_mcp.groq_functions as pxt_groq

logger = logger.bind(name="VideoProcessor")
settings = get_settings()


class VideoStatus(str, Enum):
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


if TYPE_CHECKING:
    from multimodal_mcp.video.ingestion.models import (
        VideoTableStub,
        FramesViewStub,
        AudioChunksViewStub,
    )


class VideoProcessor:

    def __init__(self):
        self.video_table: "VideoTableStub | pxt.Table | None" = None
        self.frames_table: "FramesViewStub | pxt.Table | None" = None
        self.audio_table: "AudioChunksViewStub | pxt.Table | None" = None

        self.video_name: Optional[str] = None
        self.video_id: Optional[str] = None
        self.video_path: Optional[str] = None

        self._ensure_dirs_and_tables_exist()

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------
    def _ensure_dirs_and_tables_exist(self):
        """Ensure global tables exist, creating them if necessary."""
        # if settings.DEFAULT_VIDEO_TABLE_DIR not in pxt.list_dirs():
        #     pxt.create_dir(settings.DEFAULT_VIDEO_TABLE_DIR)
        #     logger.info(f"Created global directory {settings.DEFAULT_VIDEO_TABLE_DIR}")

        # --- videos table ---
        if settings.GLOBAL_VIDEO_TABLE_NAME not in pxt.list_tables():
            self.video_table = pxt.create_table(
                settings.GLOBAL_VIDEO_TABLE_NAME,
                {
                    "video_id": pxt.String,
                    "video": pxt.Video,
                    "video_name": pxt.String,
                    "status": pxt.String,
                    "processed_at": pxt.Timestamp,
                },
                if_exists="ignore",
            )
            logger.info("Created global videos table.")
        else:
            self.video_table = pxt.get_table(settings.GLOBAL_VIDEO_TABLE_NAME)

        # --- frames table ---
        if settings.GLOBAL_FRAME_VIEW_NAME not in pxt.list_tables():
            self._process_frames()
            logger.info("Created global frames table.")
        else:
            self.frames_table = pxt.get_table(settings.GLOBAL_FRAME_VIEW_NAME)

        # --- audio table ---
        if settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME not in pxt.list_tables():
            self._process_audio()
            logger.info("Created global audio_chunks table.")
        else:
            self.audio_table = pxt.get_table(settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME)

    # -------------------------------------------------------------------------
    # VALIDATION HELPERS (NEW)
    # -------------------------------------------------------------------------
    def _validate_video_file(self, video_path: str) -> tuple[bool, str]:
        """
        Validate video file exists and is accessible.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(video_path)

        # Check if file exists
        if not path.exists():
            return False, f"Video file not found: {video_path}"

        # Check if it's a file (not directory)
        if not path.is_file():
            return False, f"Path is not a file: {video_path}"

        # Check if file is readable
        if not os.access(video_path, os.R_OK):
            return False, f"Video file is not readable: {video_path}"

        # Check file size (not empty, not too large)
        file_size = path.stat().st_size
        if file_size == 0:
            return False, f"Video file is empty: {video_path}"

        # Check reasonable max size (e.g., 5GB)
        max_size = 5 * 1024 * 1024 * 1024  # 5GB
        if file_size > max_size:
            return False, f"Video file too large (max 5GB): {video_path}"

        # Check file extension
        valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".flv"}
        if path.suffix.lower() not in valid_extensions:
            return (
                False,
                f"Unsupported video format: {path.suffix}. Supported: {', '.join(valid_extensions)}",
            )

        return True, ""

    def _validate_video_format(self, video_path: str) -> tuple[bool, str]:
        """
        Validate video can be opened by PyAV (quick check).

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import av

            # Try to open video and check it has video streams
            with av.open(video_path) as container:
                if not container.streams.video:
                    return False, "No video streams found in file"

                # Check if we can get basic info
                video_stream = container.streams.video[0]
                if video_stream.duration is None and video_stream.frames == 0:
                    return False, "Video appears to be empty or corrupted"

            return True, ""

        except av.AVError as e:
            return False, f"Invalid video format or corrupted file: {str(e)}"
        except Exception as e:
            return False, f"Failed to validate video: {str(e)}"

    def _cleanup_video(self, video_id: str):
        """
        Clean up partial data from failed video processing.

        Args:
            video_id: ID of the failed video
        """
        try:
            # Delete from video table
            if self.video_table:
                deleted_count = self.video_table.delete(
                    where=(self.video_table.video_id == video_id)
                )
                logger.info(f"Cleaned up video table entry for video_id: {video_id}")

        except Exception as e:
            logger.warning(f"Failed to cleanup video_id {video_id}: {e}")

    # -------------------------------------------------------------------------
    # Delete Video (Public API)
    # -------------------------------------------------------------------------
    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video and all related data (frames, audio chunks)
        from Pixeltable tables.

        Args:
            video_id (str): The ID of the video to delete.

        Returns:
            bool: True if deleted successfully, False if not found or failed.
        """
        try:
            if not video_id:
                logger.warning("No video_id provided for deletion.")
                return False

            # Check if video exists
            existing = []
            if self.video_table:
                existing = self.video_table.where(
                    self.video_table.video_id == video_id
                ).collect()

            if not existing:
                logger.info(f"No video found for deletion: video_id={video_id}")
                return False

            logger.info(f"Deleting video and related data for video_id={video_id} ...")

            # Reuse cleanup logic
            self._cleanup_video(video_id)

            logger.success(f"Deleted video and related data for video_id={video_id}")
            return True

        except Exception as e:
            logger.exception(f"Error deleting video_id={video_id}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Video Addition & Processing (IMPROVED)
    # -------------------------------------------------------------------------
    def add_video(self, video_path: str, video_id: str) -> bool:
        """
        Add and process a video file with proper validation.

        Args:
            video_path: Path to the video file
            video_id: Unique video identifier (uuid4)

        Returns:
            bool: True if processing succeeded, False otherwise
        """
        logger.info(f"Adding and processing video '{video_path}'...")

        # Step 1: Validate file exists and is accessible
        is_valid, error_msg = self._validate_video_file(video_path)
        if not is_valid:
            logger.error(f"Video file validation failed: {error_msg}")
            return False

        # Step 2: Validate video format (can be opened)
        is_valid, error_msg = self._validate_video_format(video_path)
        if not is_valid:
            logger.error(f"Video format validation failed: {error_msg}")
            return False

        # Step 3: Set video info
        self.video_path = video_path
        self.video_name = Path(video_path).stem

        try:
            # Step 4: Ensure tables exist
            self._ensure_dirs_and_tables_exist()

            # Step 5: Check if video already processed
            if self._is_already_added():
                logger.info(f"Video '{self.video_name}' already processed. Skipping.")
                return True  # Not an error, just already done

            # Step 6: Check if incomplete processing exists
            existing = self.video_table.where(
                self.video_table.video_name == self.video_name
            ).collect()

            if existing:
                logger.info(f"Reprocessing incomplete video '{self.video_name}'...")
                old_video_id = existing[0]["video_id"]

                # Clean up old incomplete data
                self._cleanup_video(old_video_id)

            # Step 7: Create new video ID and insert
            # self.video_id = uuid.uuid4().hex[:8]
            self.video_id = video_id

            logger.info(
                f"Inserting video '{self.video_name}' with ID '{self.video_id}'"
            )
            self.video_table.insert(
                [
                    {
                        "video_id": self.video_id,
                        "video": video_path,
                        "video_name": self.video_name,
                        "status": VideoStatus.PROCESSING,
                        "processed_at": None,
                    }
                ]
            )

            # Step 8: Mark as done (actual processing happens via computed columns)
            self._mark_done()
            logger.success(f"Successfully processed video '{self.video_name}'")
            return True

        except Exception as e:
            error_details = f"Failed to process '{self.video_name}': {str(e)}"
            logger.exception(error_details)

            # Clean up on failure if we have a video_id
            if self.video_id:
                self._cleanup_video(self.video_id)

            # Try to mark as failed (if entry was created)
            try:
                if self.video_id:
                    self._mark_failed()
            except Exception:
                pass  # Don't throw if marking failed also fails

            return False

    def _is_already_added(self) -> bool:
        """
        Check if a video with this name exists in the global table
        and has completed processing. If it exists but is not DONE,
        allow reprocessing (by returning False).
        """
        existing = self.video_table.where(
            self.video_table.video_name == self.video_name
        ).collect()

        if not existing:
            return False

        # If exists and status == DONE → skip
        status = existing[0].get("status")
        return status == VideoStatus.DONE

    def _mark_processing(self):
        """Mark video as currently processing"""
        self.video_table.where(self.video_table.video_id == self.video_id).update(
            {"status": VideoStatus.PROCESSING, "processed_at": datetime.now()}
        )

    def _mark_done(self):
        """Mark video as successfully processed"""
        self.video_table.where(self.video_table.video_id == self.video_id).update(
            {"status": VideoStatus.DONE, "processed_at": datetime.now()}
        )

    def _mark_failed(self):
        """Mark video as failed processing"""
        if not self.video_id:
            logger.warning("Cannot mark as failed: no video_id set")
            return

        try:
            self.video_table.where(self.video_table.video_id == self.video_id).update(
                {"status": VideoStatus.FAILED, "processed_at": datetime.now()}
            )
            logger.info(f"Marked video '{self.video_id}' as FAILED")
        except Exception as e:
            logger.error(f"Failed to mark video as failed: {e}")

    # -------------------------------------------------------------------------
    # Audio Processing
    # -------------------------------------------------------------------------
    def _process_audio(self):
        logger.info("Processing audio...")

        self.video_table.add_computed_column(
            audio=extract_audio(self.video_table.video, format="mp3")
        )

        self.audio_table = pxt.create_view(
            settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME,
            self.video_table,
            iterator=AudioSplitter.create(
                audio=self.video_table.audio,
                chunk_duration_sec=settings.AUDIO_CHUNK_DURATION_SEC,
                overlap_sec=settings.AUDIO_OVERLAP_SEC,
                min_chunk_duration_sec=settings.AUDIO_MIN_CHUNK_DURATION_SEC,
            ),
            if_exists="ignore",
        )
        logger.info(
            f"Created Audio view table: '{settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME}'"
        )

        # Transcribe
        if settings.MODEL_PROVIDER == "openai":
            self.audio_table.add_computed_column(
                transcription=openai.transcriptions(
                    audio=self.audio_table.audio_chunk,
                    model=settings.AUDIO_TRANSCRIPTION_MODEL,
                )
            )
        else:
            self.audio_table.add_computed_column(
                transcription=pxt_groq.transcriptions(
                    audio=self.audio_table.audio_chunk,
                    model=settings.AUDIO_TRANSCRIPTION_MODEL,
                )
            )

        self.audio_table.add_computed_column(
            audio_chunk_text=extract_text_from_chunk(self.audio_table.transcription),
            if_exists="ignore",
        )

        # Global embedding index (shared across videos)
        self.audio_table.add_embedding_index(
            column=self.audio_table.audio_chunk_text,
            string_embed=huggingface.sentence_transformer.using(
                model_id=settings.TEXT_EMBEDDING_MODEL
            ),
            idx_name="audio_chunk_embeddings_global",
            if_exists="ignore",
        )

        logger.success("Audio Table created.")

    # -------------------------------------------------------------------------
    # Frame Processing
    # -------------------------------------------------------------------------
    def _process_frames(self):
        logger.info("Processing frames table...")

        # Frame iterator
        self.frames_table: "FramesViewStub | pxt.Table" = pxt.create_view(
            settings.GLOBAL_FRAME_VIEW_NAME,
            self.video_table,
            iterator=FrameIterator.create(
                video=self.video_table.video,
                num_frames=settings.NUM_FRAMES,
            ),
            if_exists="ignore",
        )
        logger.info(f"Created Frames view table: '{settings.GLOBAL_FRAME_VIEW_NAME}'")

        self.frames_table.add_computed_column(
            resized_frame=resize_image(
                self.frames_table.frame,
                width=settings.IMAGE_RESIZE_WIDTH,
                height=settings.IMAGE_RESIZE_HEIGHT,
            ),
            if_exists="replace_force",
        )

        if settings.MODEL_PROVIDER == "openai":
            self.frames_table.add_computed_column(
                caption=openai.vision(
                    prompt=settings.IMAGE_CAPTION_PROMPT,
                    image=self.frames_table.frame,
                    model=settings.IMAGE_CAPTION_MODEL,
                )
            )
        else:
            self.frames_table.add_computed_column(
                caption=pxt_groq.vision(
                    prompt=settings.IMAGE_CAPTION_PROMPT,
                    image=self.frames_table.frame,
                    model=settings.IMAGE_CAPTION_MODEL,
                )
            )

        # Global embedding indices (shared across all videos)
        self.frames_table.add_embedding_index(
            column=self.frames_table.frame,
            image_embed=huggingface.clip.using(model_id=settings.IMAGE_EMBEDDING_MODEL),
            idx_name=settings.GLOBAL_FRAME_INDEX_NAME,
            if_exists="ignore",
        )

        self.frames_table.add_embedding_index(
            column=self.frames_table.caption,
            string_embed=huggingface.sentence_transformer.using(
                model_id=settings.TEXT_EMBEDDING_MODEL
            ),
            idx_name=settings.GLOBAL_CAPTION_INDEX,
            if_exists="ignore",
        )

        logger.success("Frames Table processed.")


# -------------------------------------------------------------------------
# Example Usage
# -------------------------------------------------------------------------
if __name__ == "__main__":
    processor = VideoProcessor()
    processor.add_video("example.mp4")
