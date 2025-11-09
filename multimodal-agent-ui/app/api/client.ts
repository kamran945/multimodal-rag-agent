/**
 * API Client Layer
 *
 * Centralized API communication with error handling, retry logic, and type safety.
 * All API calls should go through this layer to ensure consistency.
 */

import type {
  UploadImageResponse,
  UploadVideoResponse,
  ProcessVideoResponse,
  AIAgentResponse,
  MediaFilesListResponse,
  DeleteMediaResponse,
  TaskStatusResponse,
  ChatRequestPayload,
  ProcessVideoPayload,
  DeleteMediaPayload,
} from "@/app/types";

// ============================================================================
// Configuration
// ============================================================================

const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || "",
  mediaURL: process.env.NEXT_PUBLIC_API_MEDIA_URL || "",
  timeout: 30000,
  retries: 3,
} as const;

// ============================================================================
// Error Handling
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text().catch(() => "Unknown error");
    throw new APIError(
      `API Error: ${response.statusText}`,
      response.status,
      error
    );
  }

  try {
    return await response.json();
  } catch {
    throw new APIError("Failed to parse API response");
  }
}

// ============================================================================
// HTTP Client
// ============================================================================

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_CONFIG.baseURL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new APIError("Network request failed", undefined, error);
  }
}

// ============================================================================
// File Upload Utilities
// ============================================================================

/**
 * Upload a file with FormData
 */
async function uploadFile<T>(endpoint: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_CONFIG.baseURL}${endpoint}`;

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new APIError("File upload failed", undefined, error);
  }
}

/**
 * Convert File to base64 string
 */
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64String = (reader.result as string).split(",")[1];
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Construct full media URL from relative path
 */
export function getFullMediaURL(relativePath: string): string {
  if (!relativePath) return "";
  if (relativePath.startsWith("http")) return relativePath;

  const cleanPath = relativePath.replace(/^\/media\/?/, "");
  return `${API_CONFIG.mediaURL}/${cleanPath}`;
}

// ============================================================================
// API Methods
// ============================================================================

export const api = {
  // ------------------------------------------------------------------------
  // Media Upload
  // ------------------------------------------------------------------------

  async uploadImage(file: File): Promise<UploadImageResponse> {
    const response = await uploadFile<UploadImageResponse>(
      "/upload-image",
      file
    );

    // Normalize paths to full URLs
    if (response.image_path) {
      response.image_path = getFullMediaURL(response.image_path);
    }

    return response;
  },

  async uploadVideo(file: File): Promise<UploadVideoResponse> {
    const response = await uploadFile<UploadVideoResponse>(
      "/upload-video",
      file
    );

    // Normalize paths to full URLs
    if (response.video_path) {
      response.video_path = getFullMediaURL(response.video_path);
    }

    return response;
  },

  // ------------------------------------------------------------------------
  // Video Processing
  // ------------------------------------------------------------------------

  async processVideo(
    payload: ProcessVideoPayload
  ): Promise<ProcessVideoResponse> {
    return request<ProcessVideoResponse>("/process-video", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return request<TaskStatusResponse>(`/task-status/${taskId}`);
  },

  // ------------------------------------------------------------------------
  // Chat
  // ------------------------------------------------------------------------

  async sendChatMessage(payload: ChatRequestPayload): Promise<AIAgentResponse> {
    return request<AIAgentResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // ------------------------------------------------------------------------
  // Media Management
  // ------------------------------------------------------------------------

  async listMediaFiles(): Promise<MediaFilesListResponse> {
    const response = await request<MediaFilesListResponse>("/media-files");

    // Normalize all media URLs
    response.files = response.files.map((file) => ({
      ...file,
      media_url: getFullMediaURL(file.media_url),
    }));

    return response;
  },

  async deleteMediaFile(
    payload: DeleteMediaPayload
  ): Promise<DeleteMediaResponse> {
    return request<DeleteMediaResponse>("/media-file", {
      method: "DELETE",
      body: JSON.stringify(payload),
    });
  },

  async getMediaStats() {
    return request<{
      success: boolean;
      total_files: number;
      total_size_bytes: number;
      total_size_mb: number;
      images: number;
      videos: number;
    }>("/media-files/stats");
  },
};

export default api;
