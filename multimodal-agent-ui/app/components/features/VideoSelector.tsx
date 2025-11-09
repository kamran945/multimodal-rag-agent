/**
 * VideoSelector Component (Improved)
 *
 * Compact video selection control for targeted search.
 * Displays selection status and provides quick actions.
 *
 * Features:
 * - Visual selection feedback with icons
 * - Select All / Clear actions
 * - Clear selection count indicator
 * - Accessible keyboard navigation
 * - Status-based messaging
 */

"use client";

import React from "react";
import { Target, CheckCircle2, Circle } from "lucide-react";
import { useChatStore } from "@/app/lib/store/chatStore";
import type { MediaFile } from "@/app/types";

// ============================================================================
// Component Props
// ============================================================================

interface VideoSelectorProps {
  videos: MediaFile[]; // Only processed user videos
}

// ============================================================================
// Component
// ============================================================================

export default function VideoSelector({ videos }: VideoSelectorProps) {
  const selectedVideoIds = useChatStore((state) => state.selectedVideoIds);
  // const toggleVideoSelection = useChatStore(
  //   (state) => state.toggleVideoSelection
  // );
  const clearVideoSelection = useChatStore(
    (state) => state.clearVideoSelection
  );
  const setSelectedVideoIds = useChatStore(
    (state) => state.setSelectedVideoIds
  );

  // No videos to select
  if (videos.length === 0) {
    return null;
  }

  // Handle select all
  const handleSelectAll = () => {
    const allIds = videos.map((v) => v.media_id);
    setSelectedVideoIds(allIds);
  };

  // Check selection state
  const allSelected = videos.length === selectedVideoIds.length;
  const noneSelected = selectedVideoIds.length === 0;
  const someSelected = !allSelected && !noneSelected;

  return (
    <div
      className="border border-[hsl(var(--border-color))] rounded-lg bg-[hsl(var(--card-background))] p-3 shadow-sm"
      role="region"
      aria-label="Video search target selector"
    >
      {/* Header with Icon and Badge */}
      <div className="flex items-center gap-2 mb-2">
        <Target className="w-4 h-4 text-[hsl(var(--primary))]" />
        <span className="text-xs font-semibold text-[hsl(var(--foreground))]">
          Search Target
        </span>
        {selectedVideoIds.length > 0 && (
          <span className="ml-auto text-xs bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] px-2 py-0.5 rounded-full font-medium">
            {selectedVideoIds.length}
          </span>
        )}
      </div>

      {/* Status Description */}
      <div className="mb-3">
        {noneSelected ? (
          <p className="text-xs text-[hsl(var(--foreground))] opacity-70 flex items-center gap-1">
            <Circle className="w-3 h-3" />
            No videos selected - searches all videos
          </p>
        ) : (
          <p className="text-xs text-[hsl(var(--primary))] flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Searches only {selectedVideoIds.length} selected video
            {selectedVideoIds.length > 1 ? "s" : ""}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={handleSelectAll}
          disabled={allSelected}
          className="flex-1 text-xs px-3 py-1.5 rounded bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] hover:bg-[hsl(var(--button-hover))] disabled:opacity-40 disabled:cursor-not-allowed transition-all font-medium shadow-sm"
          aria-label="Select all videos"
        >
          Select All
        </button>
        <button
          onClick={clearVideoSelection}
          disabled={noneSelected}
          className="flex-1 text-xs px-3 py-1.5 rounded bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] hover:bg-[hsl(var(--button-hover))] disabled:opacity-40 disabled:cursor-not-allowed transition-all font-medium shadow-sm"
          aria-label="Clear selection"
        >
          Clear
        </button>
      </div>

      {/* Selection Hint */}
      {someSelected && (
        <p className="text-xs text-[hsl(var(--foreground))] opacity-60 mt-2">
          Click checkboxes on videos to adjust selection
        </p>
      )}
    </div>
  );
}
