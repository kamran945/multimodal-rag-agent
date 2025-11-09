"""
API Constants - Centralized constants for media handling and API responses
"""

from typing import Set

# =====================================================
# MEDIA FILE EXTENSIONS
# =====================================================
IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
VIDEO_EXTENSIONS: Set[str] = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".flv"}
ALL_MEDIA_EXTENSIONS: Set[str] = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# =====================================================
# MEDIA DIRECTORY PATHS (relative to SHARED_MEDIA_DIR)
# =====================================================
MEDIA_DIR_IMAGES = "images"
MEDIA_DIR_VIDEOS_UPLOADS = "videos/uploads"
MEDIA_DIR_VIDEOS_AI = "videos/ai_responses"

# =====================================================
# API RESPONSE MESSAGES
# =====================================================
# Success messages
MSG_FILE_NOT_FOUND = "File not found"
MSG_INVALID_PATH = "Invalid file path"
MSG_ACCESS_DENIED = "Access denied"
MSG_UPLOAD_SUCCESS = "File uploaded successfully"
MSG_DELETE_SUCCESS = "File deletion scheduled"
MSG_DELETE_COMPLETED = "File deleted successfully"
MSG_PROCESSING_STARTED = "Processing started"
MSG_VIDEO_PROCESSED = "Video uploaded and processing started!"
MSG_IMAGE_UPLOADED = "Image uploaded successfully"

# Error messages
MSG_NO_FILE_UPLOADED = "No file uploaded"
MSG_FILE_UPLOAD_FAILED = "File upload failed"
MSG_FILE_DELETE_FAILED = "Failed to delete file"
MSG_PROCESSING_FAILED = "Video upload or processing failed"
MSG_EMPTY_QUERY = "Query cannot be empty"
MSG_INVALID_BASE64 = "Invalid base64 format"
MSG_FILE_TOO_LARGE = "File too large"

# =====================================================
# FILE SIZE LIMITS
# =====================================================
MAX_IMAGE_SIZE_MB = 10
MAX_VIDEO_SIZE_GB = 5
MAX_QUERY_LENGTH = 2000
MAX_BASE64_SIZE_MB = 10

# =====================================================
# HTTP STATUS CODES (for reference)
# =====================================================
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500
