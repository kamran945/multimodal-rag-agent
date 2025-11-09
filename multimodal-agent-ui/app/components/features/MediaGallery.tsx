/**
 * MediaGallery Component (Improved)
 *
 * Displays and manages media files with organized sections.
 * Delegates business logic to custom hooks for better separation of concerns.
 *
 * Features:
 * - Image/Video gallery with categorization
 * - Video upload with processing tracking
 * - File deletion with status polling
 * - Video selection for targeted search
 * - Full-screen media viewer
 */

/* eslint-disable @next/next/no-img-element */

"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { useChatStore } from "@/app/lib/store/chatStore";
import MediaViewer from "@/app/components/ui/MediaViewer";
import AddVideoButton from "@/app/components/ui/UploadVideo";
import VideoSelector from "@/app/components/features/VideoSelector";
import { useMediaSync } from "@/app/lib/hooks/useMediaSync";
import { useMediaUpload, useMediaDelete } from "@/app/lib/hooks/useMedia";
import { MediaFile } from "@/app/types";

// ============================================================================
// Types
// ============================================================================

type SectionType = "images" | "uploaded-videos" | "ai-videos" | null;
type MediaType = "image" | "video";

// ============================================================================
// Component
// ============================================================================

export default function MediaGallery() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Sync with backend on mount
  useMediaSync();

  // Zustand state - Now with proper reactivity for selection
  const mediaFiles = useChatStore((state) => state.mediaFiles);
  const selectedVideoIds = useChatStore((state) => state.selectedVideoIds);
  const toggleVideoSelection = useChatStore(
    (state) => state.toggleVideoSelection
  );
  const updateMediaFile = useChatStore((state) => state.updateMediaFile);

  // Custom hooks for business logic
  const { uploadVideo } = useMediaUpload();
  const { deleteMedia } = useMediaDelete();

  // Local UI state
  const [viewerOpen, setViewerOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentType, setCurrentType] = useState<MediaType | null>(null);
  const [openSection, setOpenSection] = useState<SectionType>(null);

  // -------------------------------------------------------------------------
  // Memoized File Categories
  // -------------------------------------------------------------------------

  const images = useMemo(
    () => mediaFiles.filter((f) => f.media_type === "image"),
    [mediaFiles]
  );

  const uploadedVideos = useMemo(
    () =>
      mediaFiles.filter((f) => f.media_type === "video" && f.source === "user"),
    [mediaFiles]
  );

  const aiVideos = useMemo(
    () =>
      mediaFiles.filter((f) => f.media_type === "video" && f.source === "ai"),
    [mediaFiles]
  );

  const processedUploadedVideos = useMemo(
    () => uploadedVideos.filter((v) => v.processed),
    [uploadedVideos]
  );

  // -------------------------------------------------------------------------
  // Viewer Handlers
  // -------------------------------------------------------------------------

  const openViewer = useCallback((index: number, type: MediaType) => {
    setCurrentType(type);
    setCurrentIndex(index);
    setViewerOpen(true);
  }, []);

  const getActiveVideoList = useCallback(() => {
    if (openSection === "uploaded-videos") return uploadedVideos;
    if (openSection === "ai-videos") return aiVideos;
    return [];
  }, [openSection, uploadedVideos, aiVideos]);

  // -------------------------------------------------------------------------
  // Video Upload Handler
  // -------------------------------------------------------------------------

  const handleVideoUpload = useCallback(
    async (file: File) => {
      const toastId = `video-upload-${Date.now()}`;

      try {
        // ✅ Show persistent loading
        toast.loading("📤 Uploading video...", {
          id: toastId,
          duration: Infinity,
        });

        const result = await uploadVideo(file);

        if (result) {
          toast.success("✅ Video uploaded! Processing started.", {
            id: toastId,
            duration: 3000,
          });
        } else {
          toast.error("❌ Video upload failed", {
            id: toastId,
            duration: 4000,
          });
        }
      } catch (error) {
        console.error("Video upload error:", error);
        toast.error("❌ Video upload failed", {
          id: toastId,
          duration: 4000,
        });
      }
    },
    [uploadVideo]
  );

  // -------------------------------------------------------------------------
  // File Deletion Handler
  // -------------------------------------------------------------------------

  const handleDelete = useCallback(
    async (file: MediaFile) => {
      try {
        toast.loading(`Deleting ${file.media_type}...`, { id: file.media_id });
        await deleteMedia(file);
        toast.success("File Deleted!", { id: file.media_id });
      } catch (error) {
        console.error("Delete error:", error);
        toast.error("Failed to delete file", { id: file.media_id });
      }
    },
    [deleteMedia]
  );

  // -------------------------------------------------------------------------
  // Video Processing Polling
  // -------------------------------------------------------------------------

  useEffect(() => {
    const interval = setInterval(async () => {
      const pendingFiles = mediaFiles.filter(
        (f) => f.media_type === "video" && !f.processed && !f.error
      );

      if (pendingFiles.length === 0) return;

      for (const file of pendingFiles) {
        try {
          const res = await fetch(`${API_URL}/task-status/${file.media_id}`);
          if (!res.ok) continue;
          const data = await res.json();

          switch (data.status) {
            case "completed":
              updateMediaFile(file.media_id, { processed: true });
              // ✅ Show success for 3 seconds
              toast.success("✅ Video processed successfully!", {
                id: file.media_id,
                duration: 3000,
              });
              break;

            case "failed":
              updateMediaFile(file.media_id, {
                processed: false,
                error: "failed",
              });
              // ✅ Show error for 5 seconds
              toast.error("❌ Video processing failed", {
                id: file.media_id,
                duration: 5000,
              });
              break;

            case "not_found":
              updateMediaFile(file.media_id, {
                processed: false,
                error: "not_found",
              });
              // ✅ Show warning for 4 seconds
              toast.error("⚠️ Processing task not found", {
                id: file.media_id,
                duration: 4000,
              });
              break;
          }
        } catch (err) {
          console.error(`Polling error for ${file.media_id}:`, err);
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [mediaFiles, API_URL, updateMediaFile]);

  // -------------------------------------------------------------------------
  // Auto-close Viewer on Empty List
  // -------------------------------------------------------------------------

  useEffect(() => {
    if (!viewerOpen || !currentType) return;

    const activeList = currentType === "image" ? images : getActiveVideoList();

    if (activeList.length === 0) {
      setTimeout(() => setViewerOpen(false), 0);
      return;
    }

    if (currentIndex >= activeList.length) {
      setTimeout(() => setCurrentIndex(activeList.length - 1), 0);
    }
  }, [
    images,
    uploadedVideos,
    aiVideos,
    viewerOpen,
    currentType,
    currentIndex,
    getActiveVideoList,
  ]);

  // -------------------------------------------------------------------------
  // Section Toggle Handler
  // -------------------------------------------------------------------------

  const toggleSection = useCallback((section: SectionType) => {
    setOpenSection((prev) => (prev === section ? null : section));
  }, []);

  // -------------------------------------------------------------------------
  // Render Helper: Media Thumbnail (FIXED - Now properly reactive)
  // -------------------------------------------------------------------------

  const renderMediaThumbnail = useCallback(
    (file: MediaFile, index: number, type: MediaType, showSelector = false) => {
      const isProcessing =
        file.media_type === "video" && !file.processed && !file.error;
      const hasFailed = Boolean(file.error);
      const isSelected = selectedVideoIds.includes(file.media_id);

      return (
        <div
          key={file.media_id}
          className="relative flex-1 min-w-[120px] max-w-[200px] h-24 rounded overflow-hidden border border-[hsl(var(--border-color))] cursor-pointer hover:opacity-90 transition-opacity"
        >
          {/* Media Content */}
          {type === "image" ? (
            <img
              src={file.media_url}
              alt={file.media_id}
              className="w-full h-full object-cover"
              onClick={() => openViewer(index, type)}
            />
          ) : (
            <video
              src={file.media_url}
              className={`w-full h-full object-cover ${
                isProcessing ? "opacity-50" : ""
              }`}
              onClick={() => openViewer(index, type)}
            />
          )}

          {/* Status Overlays */}
          {isProcessing && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/40">
              <span className="text-white text-[10px] font-medium">
                Processing...
              </span>
            </div>
          )}

          {hasFailed && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-500/60">
              <span className="text-white text-[10px] font-medium">Failed</span>
            </div>
          )}

          {/* Delete Button */}
          <button
            className="absolute top-1 right-1 w-5 h-5 text-[hsl(var(--button-foreground))] bg-[hsl(var(--button-background))] rounded-full text-xs flex items-center justify-center hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(file);
            }}
            aria-label="Delete file"
          >
            ×
          </button>

          {/* Selection Checkbox (Videos Only) - FIXED */}
          {showSelector && file.processed && (
            <button
              className={`absolute bottom-1 left-1 w-6 h-6 rounded flex items-center justify-center text-sm font-bold border-2 transition-all ${
                isSelected
                  ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] border-[hsl(var(--primary))] scale-110"
                  : "bg-white/90 text-gray-600 border-gray-300 hover:border-[hsl(var(--primary))] hover:bg-white"
              }`}
              onClick={(e) => {
                e.stopPropagation();
                toggleVideoSelection(file.media_id);
              }}
              aria-label={isSelected ? "Deselect video" : "Select video"}
              style={{
                boxShadow: isSelected
                  ? "0 2px 8px hsla(var(--primary), 0.4)"
                  : "0 1px 3px rgba(0,0,0,0.1)",
              }}
            >
              {isSelected ? "✓" : ""}
            </button>
          )}
        </div>
      );
    },
    [openViewer, handleDelete, selectedVideoIds, toggleVideoSelection]
  );

  // -------------------------------------------------------------------------
  // Render: Empty State
  // -------------------------------------------------------------------------

  if (mediaFiles.length === 0) {
    return (
      <div className="flex flex-col gap-3">
        {/* Section Buttons */}
        <SectionButton
          label="Images"
          isActive={openSection === "images"}
          onClick={() => toggleSection("images")}
        />
        <SectionButton
          label="Uploaded Videos"
          isActive={openSection === "uploaded-videos"}
          onClick={() => toggleSection("uploaded-videos")}
        />
        <SectionButton
          label="AI Response Videos"
          isActive={openSection === "ai-videos"}
          onClick={() => toggleSection("ai-videos")}
        />

        {/* Upload Prompt */}
        {openSection === "uploaded-videos" && (
          <div className="flex flex-col gap-2 mt-2">
            <AddVideoButton onUpload={handleVideoUpload} />
            <p className="text-xs text-[hsl(var(--foreground))] opacity-60">
              No videos uploaded yet.
            </p>
          </div>
        )}
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render: Gallery with Files
  // -------------------------------------------------------------------------

  return (
    <>
      {/* Section Buttons */}
      <div className="flex flex-col gap-2 mb-3">
        <SectionButton
          label="Images"
          count={images.length}
          isActive={openSection === "images"}
          onClick={() => toggleSection("images")}
        />
        <SectionButton
          label="Uploaded Videos"
          count={uploadedVideos.length}
          isActive={openSection === "uploaded-videos"}
          onClick={() => toggleSection("uploaded-videos")}
        />
        <SectionButton
          label="AI Response Videos"
          count={aiVideos.length}
          isActive={openSection === "ai-videos"}
          onClick={() => toggleSection("ai-videos")}
        />
      </div>

      {/* Content Area */}
      <div className="flex flex-col gap-3 overflow-y-auto main-scrollable p-2">
        {/* Images Section */}
        {openSection === "images" && images.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {images.map((file, i) =>
              renderMediaThumbnail(file, i, "image", false)
            )}
          </div>
        )}

        {/* Uploaded Videos Section */}
        {openSection === "uploaded-videos" && (
          <div className="flex flex-col gap-3">
            <AddVideoButton onUpload={handleVideoUpload} />

            {processedUploadedVideos.length > 0 && (
              <VideoSelector videos={processedUploadedVideos} />
            )}

            {uploadedVideos.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {uploadedVideos.map((file, i) =>
                  renderMediaThumbnail(file, i, "video", true)
                )}
              </div>
            ) : (
              <p className="text-xs text-center text-[hsl(var(--foreground))] opacity-60">
                No videos uploaded yet.
              </p>
            )}
          </div>
        )}

        {/* AI Videos Section */}
        {openSection === "ai-videos" && aiVideos.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {aiVideos.map((file, i) =>
              renderMediaThumbnail(file, i, "video", false)
            )}
          </div>
        )}
      </div>

      {/* Media Viewer Modal */}
      {viewerOpen && currentType && (
        <MediaViewer
          mediaFiles={currentType === "image" ? images : getActiveVideoList()}
          currentIndex={currentIndex}
          setCurrentIndex={setCurrentIndex}
          close={() => setViewerOpen(false)}
        />
      )}
    </>
  );
}

// ============================================================================
// Helper Component: Section Button
// ============================================================================

interface SectionButtonProps {
  label: string;
  count?: number;
  isActive: boolean;
  onClick: () => void;
}

function SectionButton({
  label,
  count,
  isActive,
  onClick,
}: SectionButtonProps) {
  return (
    <button
      className={`cursor-pointer text-xs py-1.5 px-3 rounded transition-all duration-200 ${
        isActive
          ? "bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] font-medium shadow-sm"
          : "bg-transparent text-[hsl(var(--foreground))] hover:bg-[hsl(var(--button-hover))]"
      }`}
      onClick={onClick}
      aria-pressed={isActive}
    >
      {label} {count !== undefined && count > 0 && `(${count})`}
    </button>
  );
}
