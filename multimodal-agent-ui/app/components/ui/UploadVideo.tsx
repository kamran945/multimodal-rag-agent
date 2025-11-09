"use client";
import React from "react";

interface AddVideoButtonProps {
  onUpload?: (file: File) => void;
}

export default function AddVideoButton({ onUpload }: AddVideoButtonProps) {
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUpload) onUpload(file);
  };

  return (
    <div>
      <button
        onClick={() => document.getElementById("videoUploadInput")?.click()}
        className="cursor-pointer flex items-center justify-center gap-2 w-full px-4 py-2 rounded-md 
          bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] 
          hover:bg-[hsl(var(--button-hover))] border border-[hsl(var(--button-border))] 
          transition-all font-medium"
      >
        ＋ Add Video
      </button>

      <input
        id="videoUploadInput"
        type="file"
        accept="video/*"
        className="hidden"
        onChange={handleFileSelect}
      />
    </div>
  );
}
