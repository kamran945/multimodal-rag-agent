/**
 * AddVideoButton Component
 *
 * Simple button for triggering video upload file dialog.
 */

"use client";

import React from "react";

// ============================================================================
// Component Props
// ============================================================================

interface AddVideoButtonProps {
  onUpload?: (file: File) => void;
  disabled?: boolean;
}

// ============================================================================
// Component
// ============================================================================

export default function AddVideoButton({
  onUpload,
  disabled = false,
}: AddVideoButtonProps) {
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUpload) {
      onUpload(file);
    }
    // Reset input value
    e.target.value = "";
  };

  return (
    <div>
      <button
        type="button"
        onClick={() => document.getElementById("videoUploadInput")?.click()}
        disabled={disabled}
        className="cursor-pointer flex items-center justify-center gap-2 w-full px-4 py-2 rounded-md 
          bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] 
          hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] 
          transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
      >
        + Add Video
      </button>

      <input
        id="videoUploadInput"
        type="file"
        accept="video/*"
        className="hidden"
        onChange={handleFileSelect}
        disabled={disabled}
      />
    </div>
  );
}
