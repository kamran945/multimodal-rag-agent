/**
 * AttachmentMenu Component (Refactored)
 *
 * Pure UI component for file attachment selection.
 * No business logic, just renders menu and handles file input.
 */

"use client";

import React, { useState, useRef, useEffect } from "react";
import { Plus, Image } from "lucide-react";

// ============================================================================
// Component Props
// ============================================================================

interface AttachmentMenuProps {
  onFileSelect?: (file: File, type: "image" | "video") => void;
  disabled?: boolean;
}

// ============================================================================
// Component
// ============================================================================

export default function AttachmentMenu({
  onFileSelect,
  disabled = false,
}: AttachmentMenuProps) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  // ------------------------------------------------------------------------
  // Click Outside Handler
  // ------------------------------------------------------------------------

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ------------------------------------------------------------------------
  // File Handlers
  // ------------------------------------------------------------------------

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !onFileSelect) return;

    setOpen(false);
    onFileSelect(file, "image");

    // Reset input value so same file can be reselected
    e.target.value = "";
  };

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !onFileSelect) return;

    setOpen(false);
    onFileSelect(file, "video");

    // Reset input value so same file can be reselected
    e.target.value = "";
  };

  // ------------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------------

  return (
    <div ref={menuRef} className="relative">
      {/* Plus Button */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        disabled={disabled}
        className="flex items-center justify-center w-10 h-10 rounded-full text-[hsl(var(--foreground))] hover:bg-[hsl(var(--button-hover))] transition-colors hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Plus className="w-5 h-5" />
      </button>

      {/* Dropdown Menu */}
      {open && !disabled && (
        <div className="absolute bottom-12 left-0 mb-2 w-44 bg-[hsl(var(--card-background))] border border-[hsl(var(--card-border))] rounded-xl shadow-lg overflow-hidden z-50">
          <button
            type="button"
            className="cursor-pointer w-full flex items-center gap-2 px-4 py-2 text-sm text-[hsl(var(--foreground))] hover:bg-[hsl(var(--button-hover))] transition-colors"
            onClick={() => imageInputRef.current?.click()}
          >
            <Image className="w-4 h-4" /> Upload Image
          </button>
          {/* <button
            type="button"
            className="cursor-pointer w-full flex items-center gap-2 px-4 py-2 text-sm text-[hsl(var(--foreground))] hover:bg-[hsl(var(--button-hover))] transition-colors"
            onClick={() => videoInputRef.current?.click()}
          >
            <Video className="w-4 h-4" /> Upload Video
          </button> */}
        </div>
      )}

      {/* Hidden File Inputs */}
      <input
        ref={imageInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleImageUpload}
        disabled={disabled}
      />
      <input
        ref={videoInputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={handleVideoUpload}
        disabled={disabled}
      />
    </div>
  );
}
