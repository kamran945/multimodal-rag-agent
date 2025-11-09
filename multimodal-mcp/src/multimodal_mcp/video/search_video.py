# video_search_engine.py

from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING
from loguru import logger

import pixeltable as pxt

from multimodal_mcp.config import get_settings
from multimodal_mcp.video.ingestion.tools import decode_image

settings = get_settings()

if TYPE_CHECKING:
    from multimodal_mcp.video.ingestion.models import (
        VideoTableStub,
        FramesViewStub,
        AudioChunksViewStub,
    )


class VideoSearchEngine:
    """
    Unified search engine for processed videos — supports text, image, and caption-based search.

    Integrates directly with the Pixeltable-based registry from your VideoProcessor pipeline.
    """

    def __init__(self):
        """
        Initialize the search engine for the user query.

        Args:
            None

        Raises:
            RuntimeError: If the required tables are not found.
        """
        logger.info(f"Initializing VideoSearchEngine...'")
        self.video_table: "VideoTableStub|pxt.Table" = None
        self.audio_chunks_view: "AudioChunksViewStub|pxt.Table" = None
        self.frames_view: "FramesViewStub|pxt.Table" = None

        required_tables = {
            "video_table": settings.GLOBAL_VIDEO_TABLE_NAME,
            "audio_chunks_view": settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME,
            "frames_view": settings.GLOBAL_FRAME_VIEW_NAME,
        }

        existing_tables = set(pxt.list_tables())
        missing = [
            name for name in required_tables.values() if name not in existing_tables
        ]

        if missing:
            raise RuntimeError(f"Missing required PixelTable(s): {', '.join(missing)}")

        # If all exist, load them
        self.video_table = pxt.get_table(settings.GLOBAL_VIDEO_TABLE_NAME)
        self.audio_chunks_view = pxt.get_table(settings.GLOBAL_AUDIO_CHUNKS_VIEW_NAME)
        self.frames_view = pxt.get_table(settings.GLOBAL_FRAME_VIEW_NAME)

        # ✅ Sanity check: ensure tables contain data
        try:
            video_count = self.video_table.count()
            frame_count = self.frames_view.count()
            audio_count = self.audio_chunks_view.count()
        except Exception as e:
            raise RuntimeError(f"Failed to count Pixeltable rows: {e}")

        if video_count == 0 or frame_count == 0 or audio_count == 0:
            raise RuntimeError(
                f"Pixeltable is initialized but contains no processed data. "
                f"Process at least one video before running a search.\n"
                f"(videos={video_count}, frames={frame_count}, audio_chunks={audio_count})"
            )

        logger.info(
            f"Loaded video search context (videos={video_count}, frames={frame_count}, audio_chunks={audio_count})"
        )

        logger.info("Loaded video search context for user query...")

    # -------------------------------------------------------------------------
    # HELPER METHOD
    # -------------------------------------------------------------------------
    def _get_video_ids_from_names(self, video_names: List[str]) -> Set[int]:
        """
        Convert video names to video IDs by querying the video table.

        Args:
            video_names: List of video names to filter by

        Returns:
            Set of video IDs corresponding to the given names
        """
        if not video_names:
            return set()

        # Query video table to get IDs for the given names
        results = (
            self.video_table.select(
                self.video_table.video_id, self.video_table.video_name
            )
            .where(self.video_table.video_name.isin(video_names))
            .collect()
        )

        video_ids = {r["video_id"] for r in results}

        # Log if any video names weren't found
        found_names = {r["video_name"] for r in results}
        missing_names = set(video_names) - found_names
        if missing_names:
            logger.warning(f"Video names not found in table: {missing_names}")

        return video_ids

    # -------------------------------------------------------------------------
    # SPEECH SEARCH
    # -------------------------------------------------------------------------
    def search_by_speech(
        self, query: str, top_k: int = None, video_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search video segments by similarity of transcribed speech.

        Args:
            query: Search query text
            top_k: Number of results to return
            video_ids: Optional list of video ids to filter by

        Returns:
            List of dicts with start_time, end_time, video_id, and similarity
        """
        top_k = top_k or settings.SPEECH_SIMILARITY_SEARCH_TOP_K
        sims = self.audio_chunks_view.audio_chunk_text.similarity(query)

        results = self.audio_chunks_view.select(
            self.audio_chunks_view.video_id,
            self.audio_chunks_view.start_time_sec,
            self.audio_chunks_view.end_time_sec,
            similarity=sims,
        )

        # Filter by video ids if provided
        # if video_names:
        #     video_ids = self._get_video_ids_from_names(video_names)
        if video_ids:
            results = results.where(
                self.audio_chunks_view.video_id.isin(list(video_ids))
            )

        results = results.order_by(sims, asc=False)

        return [
            {
                "video_id": r["video_id"],
                "start_time": float(r["start_time_sec"]),
                "end_time": float(r["end_time_sec"]),
                "similarity": float(r["similarity"]),
            }
            for r in results.limit(top_k).collect()
        ]

    # -------------------------------------------------------------------------
    # IMAGE SEARCH
    # -------------------------------------------------------------------------
    def search_by_image(
        self,
        image_base64: str,
        top_k: int = None,
        video_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search similar frames by visual similarity.

        Args:
            image_base64: Base64 encoded query image
            top_k: Number of results to return
            video_ids: Optional list of video ids to filter by

        Returns:
            List of dicts with start_time, end_time, video_id, and similarity
        """
        top_k = top_k or settings.IMAGE_SIMILARITY_SEARCH_TOP_K
        query_image = decode_image(image_base64)

        sims = self.frames_view.frame.similarity(query_image)
        results = self.frames_view.select(
            self.frames_view.video_id,
            self.frames_view.pos_msec,
            similarity=sims,
        )

        # Filter by video ids if provided
        # if video_names:
        #     video_ids = self._get_video_ids_from_names(video_names)
        if video_ids:
            results = results.where(self.frames_view.video_id.isin(list(video_ids)))

        results = results.order_by(sims, asc=False)

        return [
            {
                "video_id": entry["video_id"],
                "start_time": entry["pos_msec"] / 1000.0
                - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0
                + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    # -------------------------------------------------------------------------
    # CAPTION SEARCH
    # -------------------------------------------------------------------------
    def search_by_caption(
        self, query: str, top_k: int = None, video_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search similar frames by caption text similarity.

        Args:
            query: Search query text
            top_k: Number of results to return
            video_ids: Optional list of video ids to filter by

        Returns:
            List of dicts with start_time, end_time, video_id, and similarity
        """
        top_k = top_k or settings.CAPTION_SIMILARITY_SEARCH_TOP_K
        sims = self.frames_view.caption.similarity(query)
        results = self.frames_view.select(
            self.frames_view.video_id,
            self.frames_view.pos_msec,
            self.frames_view.caption,
            similarity=sims,
        )

        # Filter by video ids if provided
        # if video_names:
        #     video_ids = self._get_video_ids_from_names(video_names)
        if video_ids:
            results = results.where(self.frames_view.video_id.isin(list(video_ids)))

        results = results.order_by(sims, asc=False)

        return [
            {
                "video_id": entry["video_id"],
                "start_time": entry["pos_msec"] / 1000.0
                - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0
                + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    # -------------------------------------------------------------------------
    # SPEECH INFO
    # -------------------------------------------------------------------------
    def get_speech_info(
        self, query: str, top_k: int = None, video_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most similar speech chunks and their text content.

        Args:
            query: Search query text
            top_k: Number of results to return
            video_ids: Optional list of video ids to filter by

        Returns:
            List of dicts with text, video_id, and similarity
        """
        top_k = top_k or settings.SPEECH_SIMILARITY_SEARCH_TOP_K
        sims = self.audio_chunks_view.audio_chunk_text.similarity(query)

        results = self.audio_chunks_view.select(
            self.audio_chunks_view.video_id,
            self.audio_chunks_view.audio_chunk_text,
            similarity=sims,
        )

        # Filter by video ids if provided
        # if video_names:
        #     video_ids = self._get_video_ids_from_names(video_names)
        if video_ids:
            results = results.where(
                self.audio_chunks_view.video_id.isin(list(video_ids))
            )

        results = results.order_by(sims, asc=False)

        return [
            {
                "video_id": entry["video_id"],
                "text": entry["audio_chunk_text"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    # -------------------------------------------------------------------------
    # CAPTION INFO
    # -------------------------------------------------------------------------
    def get_caption_info(
        self, query: str, top_k: int = None, video_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most similar frame captions and similarity scores.

        Args:
            query: Search query text
            top_k: Number of results to return
            video_ids: Optional list of video ids to filter by

        Returns:
            List of dicts with caption, video_id, and similarity
        """
        top_k = top_k or settings.CAPTION_SIMILARITY_SEARCH_TOP_K
        sims = self.frames_view.caption.similarity(query)

        results = self.frames_view.select(
            self.frames_view.video_id,
            self.frames_view.caption,
            similarity=sims,
        )

        # Filter by video ids if provided
        # if video_names:
        #     video_ids = self._get_video_ids_from_names(video_names)
        if video_ids:
            results = results.where(self.frames_view.video_id.isin(list(video_ids)))

        results = results.order_by(sims, asc=False)

        return [
            {
                "video_id": entry["video_id"],
                "caption": entry["caption"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]
