/**
 * Shared TypeScript type definitions
 *
 * Centralized type definitions to ensure type safety across the application.
 * All interfaces and types used by multiple modules should be defined here.
 */

// ============================================================================
// Message & Chat Types
// ============================================================================

export type MessageRole = "user" | "ai";

export interface Message {
  message_id: string;
  chat_id: string;
  role: MessageRole;
  message_content: string;
  message_image?: string;
  message_video?: string;
  createdAt: number;
}

// ============================================================================
// Media Types
// ============================================================================

export type MediaType = "image" | "video";
export type MediaSource = "user" | "ai";

export interface MediaFile {
  media_id: string;
  media_url?: string;
  media_type: MediaType;
  source: MediaSource;
  createdAt: number;
  task_id?: string;
  processed?: boolean;
  error?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface BaseAPIResponse {
  success: boolean;
  message: string;
}

export interface UploadImageResponse extends BaseAPIResponse {
  image_path?: string;
  media_id: string;
}

export interface UploadVideoResponse extends BaseAPIResponse {
  video_path?: string;
  media_id: string;
}

export interface ProcessVideoResponse extends BaseAPIResponse {
  media_id: string;
}

export interface AIAgentResponse extends BaseAPIResponse {
  output_video_path?: string;
  media_id?: string;
}

export interface MediaFileResponse {
  media_id: string;
  media_url: string;
  media_type: MediaType;
  source: MediaSource;
  createdAt: number;
  processed: boolean;
  error?: string;
  file_size?: number;
}

export interface MediaFilesListResponse {
  success: boolean;
  files: MediaFileResponse[];
  total_count: number;
}

export interface DeleteMediaResponse extends BaseAPIResponse {
  deleted: boolean;
}

export type TaskStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "failed"
  | "not_found";

export interface TaskStatusResponse {
  task_id: string;
  status: TaskStatus;
}

// ============================================================================
// Request Payload Types
// ============================================================================

export interface ChatRequestPayload {
  message: string;
  video_path?: string | null;
  image_base64?: string | null;
  video_ids?: string[];
}

export interface ProcessVideoPayload {
  video_path: string;
  media_id: string;
}

export interface DeleteMediaPayload {
  media_id: string;
  file_path: string;
}

// ============================================================================
// UI Component Props Types
// ============================================================================

export interface FilePreview {
  file: File;
  url: string;
  type: MediaType;
}

export interface LayoutProps {
  children: React.ReactNode;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}
