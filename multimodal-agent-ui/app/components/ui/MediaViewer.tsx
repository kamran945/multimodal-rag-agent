/* eslint-disable @next/next/no-img-element */

"use client";

import React, { useRef, useEffect } from "react";
// import Image from "next/image";

import { MediaFile } from "@/app/types/index";

// ============================================================================
// MediaViewer Component Props
// ============================================================================
interface MediaViewerProps {
  mediaFiles: MediaFile[]; // Array of media files to display
  currentIndex: number; // Index of currently displayed media
  setCurrentIndex: (i: number) => void; // Function to update current index
  close: () => void; // Function to close the viewer
}

// ============================================================================
// MediaViewer Component
// Full-screen overlay viewer for images and videos with navigation controls
// Positioned in the center of the screen with backdrop click-to-close
// ============================================================================
export default function MediaViewer({
  mediaFiles,
  currentIndex,
  setCurrentIndex,
  close,
}: MediaViewerProps) {
  // Get the current media file based on index
  const media = mediaFiles[currentIndex];

  // Reference to video element for programmatic control (pause, reset)
  const videoRef = useRef<HTMLVideoElement>(null);

  // -------------------------------------------------------------------------
  // Effect: Reset video playback when switching between media files
  // -------------------------------------------------------------------------
  // This ensures videos don't autoplay and start from beginning when navigated to
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.pause(); // Stop playback
      videoRef.current.currentTime = 0; // Reset to beginning
    }
  }, [currentIndex]); // Runs whenever user navigates to different media

  // -------------------------------------------------------------------------
  // Effect: Handle Escape key to close viewer
  // -------------------------------------------------------------------------
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        close();
      }
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [close]);

  // -------------------------------------------------------------------------
  // Navigation Handlers
  // -------------------------------------------------------------------------

  // Navigate to previous media (wraps around to end if at start)
  const prev = () => {
    setCurrentIndex((currentIndex - 1 + mediaFiles.length) % mediaFiles.length);
  };

  // Navigate to next media (wraps around to start if at end)
  const next = () => {
    setCurrentIndex((currentIndex + 1) % mediaFiles.length);
  };

  // -------------------------------------------------------------------------
  // Handle backdrop click (close viewer when clicking outside content)
  // -------------------------------------------------------------------------
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Only close if clicking the backdrop itself, not its children
    if (e.target === e.currentTarget) {
      close();
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    // Full-screen dark overlay - FIXED positioning to cover entire viewport
    // Click on backdrop closes the viewer
    <div
      className="fixed inset-0 w-screen h-screen bg-black/80 flex-center flex-col gap-4 z-9999 cursor-pointer"
      onClick={handleBackdropClick}
    >
      {/* ------------------------------------------------------------------
          Content Container
          Prevents clicks from bubbling to backdrop (doesn't close viewer)
          ------------------------------------------------------------------ */}
      <div
        className="relative flex flex-col items-center gap-4 cursor-default"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button (Top Right of Content) */}
        <button
          className="cursor-pointer absolute -top-12 right-0 w-10 h-10 flex-center rounded-full bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] transition-all hover:scale-110 text-xl font-light"
          onClick={close}
          aria-label="Close viewer"
        >
          ×
        </button>

        {/* ------------------------------------------------------------------
            Media Display Area
            Conditionally renders image or video based on media type
            ------------------------------------------------------------------ */}
        {media.media_type === "image" ? (
          // Image display - maintains aspect ratio, max 80vh height
          <img
            src={media.media_url}
            // <Image
            //   src={media.media_url || ""}
            alt={media.media_id}
            className="max-h-[80vh] max-w-[90vw] object-contain rounded-lg shadow-2xl"
            // onError={(e) => {
            onError={() => {
              console.error("❌ Image failed to load:", media.media_url);
            }}
          />
        ) : (
          // Video display - no autoplay, user must click play
          <video
            ref={videoRef}
            src={media.media_url}
            className="max-h-[80vh] max-w-[90vw] rounded-lg shadow-2xl"
            controls // Shows play/pause, timeline, volume controls
          />
        )}

        {/* ------------------------------------------------------------------
            Navigation Controls (Below Media)
            Previous/Next buttons with current position counter
            ------------------------------------------------------------------ */}
        <div className="flex gap-4 items-center mt-4">
          {/* Previous button - disabled if only one media file */}
          <button
            className="cursor-pointer px-4 py-2 rounded-lg bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={prev}
            disabled={mediaFiles.length <= 1}
          >
            ← Prev
          </button>

          {/* Media counter - shows current position (e.g., "3 / 10") */}
          <span className="text-white text-sm font-medium min-w-[60px] text-center bg-black/50 px-3 py-1 rounded-full">
            {currentIndex + 1} / {mediaFiles.length}
          </span>

          {/* Next button - disabled if only one media file */}
          <button
            className="cursor-pointer px-4 py-2 rounded-lg bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={next}
            disabled={mediaFiles.length <= 1}
          >
            Next →
          </button>
        </div>

        {/* Helpful hint */}
        <p className="text-white/60 text-xs mt-2">
          Press ESC or click outside to close
        </p>
      </div>
    </div>
  );
}
