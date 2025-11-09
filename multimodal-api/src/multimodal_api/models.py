from typing import Optional, List  # ✅ Added List
from enum import Enum
from pydantic import BaseModel


# -----------------------------------------------------
# Task Status Options
# -----------------------------------------------------
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


# -----------------------------------------------------
# Request / Response Models
# -----------------------------------------------------
class ProcessVideoRequest(BaseModel):
    video_path: str
    media_id: str


class ProcessVideoResponse(BaseModel):
    success: bool
    message: str
    media_id: str


class VideoUploadResponse(BaseModel):
    success: bool
    message: str
    video_path: str
    media_id: str


class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    image_path: str
    media_id: str


class UserMessageRequest(BaseModel):
    message: str
    video_path: str | None = None
    image_base64: str | None = None
    video_ids: List[str] | None = None  # Optional list of video IDs to search


class AIAgentResponse(BaseModel):
    success: bool
    message: str
    output_video_path: str | None = None
    media_id: str | None = None


# Media file models
class MediaFileResponse(BaseModel):
    media_id: str
    media_url: str
    media_type: str
    source: str
    createdAt: int
    processed: bool = False
    error: str | None = None
    file_size: int | None = None


class MediaFilesListResponse(BaseModel):
    success: bool
    files: list[MediaFileResponse]
    total_count: int


class DeleteMediaRequest(BaseModel):
    media_id: str
    file_path: str


class DeleteMediaResponse(BaseModel):
    success: bool
    message: str
    task_id: str | None = None
