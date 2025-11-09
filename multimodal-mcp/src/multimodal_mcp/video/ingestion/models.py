from typing import Optional, TYPE_CHECKING, Any
import datetime

import pixeltable as pxt


class VideoTableStub:
    video_id: pxt.ColumnRef[str]
    video: pxt.ColumnRef[str]
    video_name: pxt.ColumnRef[str]
    audio: Optional[pxt.ColumnRef[Any]]
    status: pxt.ColumnRef[str]
    processed_at: pxt.ColumnRef[datetime]
    transcript_summary: pxt.ColumnRef[str]


class FramesViewStub:
    video_id: pxt.ColumnRef[str]
    pos_msec: pxt.ColumnRef[int]
    frame: pxt.ColumnRef[Any]
    resized_frame: pxt.ColumnRef[Any]
    caption: pxt.ColumnRef[str]


class AudioChunksViewStub:
    video_id: pxt.ColumnRef[str]
    pos: pxt.ColumnRef[int]
    start_time_sec: pxt.ColumnRef[float]
    end_time_sec: pxt.ColumnRef[float]
    audio_chunk: pxt.ColumnRef[Any]
    transcription: pxt.ColumnRef[Any]
    audio_chunk_text: pxt.ColumnRef[str]
