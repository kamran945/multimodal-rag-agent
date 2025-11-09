/**
 * MediaThumbnail Component
 *
 * Reusable thumbnail component for media files with processing status indicators.
 */

/* eslint-disable @next/next/no-img-element */

"use client";

import React from "react";
// import Image from "next/image";
import type { MediaFile } from "@/app/types";

// ============================================================================
// Component Props
// ============================================================================

interface MediaThumbnailProps {
  file: MediaFile;
  onClick: () => void;
  onDelete: () => void;
}

// ============================================================================
// Component
// ============================================================================

export default function MediaThumbnail({
  file,
  onClick,
  onDelete,
}: MediaThumbnailProps) {
  const isProcessing = !file.processed && !file.error;
  const hasFailed = Boolean(file.error);

  return (
    <div
      className="relative w-24 h-24 rounded overflow-hidden border border-[hsl(var(--border-color))] cursor-pointer hover:opacity-90 transition-opacity"
      onClick={onClick}
    >
      {/* Media Content */}
      {file.media_type === "image" ? (
        <img
          src={file.media_url}
          // <Image
          //   src={file.media_url || ""}
          alt={file.media_id}
          className="w-full h-full object-cover"
        />
      ) : (
        <video
          src={file.media_url}
          className={`w-full h-full object-cover ${
            isProcessing || hasFailed ? "opacity-50" : ""
          }`}
        />
      )}

      {/* Processing Overlay */}
      {isProcessing && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/40">
          <span className="text-white text-[10px] font-medium">
            Processing...
          </span>
        </div>
      )}

      {/* Error Overlay */}
      {hasFailed && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-500/60">
          <span className="text-white text-[10px] font-medium">Failed</span>
        </div>
      )}

      {/* Delete Button */}
      <button
        className="absolute top-1 right-1 w-5 h-5 text-[hsl(var(--button-foreground))] bg-[hsl(var(--button-background))] rounded-full text-xs flex items-center justify-center hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))]"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        ×
      </button>
    </div>
  );
}
