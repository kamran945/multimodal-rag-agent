/**
 * ChatInput Component (Refactored)
 *
 * Simplified UI component that delegates business logic to hooks.
 * Focuses solely on rendering and user interaction.
 */

/* eslint-disable @next/next/no-img-element */

"use client";

import React, { useRef, useState } from "react";
import { ArrowUp } from "lucide-react";
// import Image from "next/image";
import AttachmentMenu from "@/app/components/ui/AttachmentMenu";
import { useChat } from "@/app/lib/hooks/useChat";
import type { FilePreview } from "@/app/types";

// ============================================================================
// Component Props
// ============================================================================

interface ChatInputProps {
  chat_id: string;
}

// ============================================================================
// Component
// ============================================================================

export default function ChatInput({ chat_id }: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState("");
  const [filePreview, setFilePreview] = useState<FilePreview | null>(null);

  const { isLoading, sendMessage } = useChat(chat_id);

  // ------------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------------

  const handleSend = async () => {
    if (!message.trim() && !filePreview) return;

    // Save current state before clearing
    const currentMessage = message;
    const currentFile = filePreview;

    // Clear UI immediately for better UX
    setMessage("");
    setFilePreview(null);

    // Send message
    await sendMessage(currentMessage, currentFile);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (file: File, type: "image" | "video") => {
    setFilePreview({
      file,
      url: URL.createObjectURL(file),
      type,
    });
    inputRef.current?.focus();
  };

  const handleRemovePreview = () => {
    if (filePreview?.url) {
      URL.revokeObjectURL(filePreview.url);
    }
    setFilePreview(null);
  };

  // ------------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------------

  return (
    <div className="sticky bottom-0 shrink-0 px-6 py-2 bg-[hsl(var(--main-background))] border-t border-[hsl(var(--border-color))]">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center w-full rounded-full bg-[hsl(var(--input-background))] border border-[hsl(var(--input-border))] px-2"
      >
        {/* Attachment Menu */}
        <AttachmentMenu onFileSelect={handleFileSelect} />

        {/* File Preview */}
        {filePreview && (
          <div className="relative shrink-0 w-10 h-10 mr-2">
            {filePreview.type === "image" ? (
              <img
                src={filePreview.url}
                // <Image
                //   src={filePreview.url || ""}
                className="w-10 h-10 rounded object-cover"
                alt="preview"
              />
            ) : (
              <video
                src={filePreview.url}
                className="w-10 h-10 rounded object-cover"
              />
            )}
            <button
              type="button"
              className="absolute -top-2 -right-2 bg-[hsl(var(--button-background))] text-[hsl(var(--button-foreground))] rounded-full w-4 h-4 text-xs flex items-center justify-center hover:bg-[hsl(var(--button-hover))]"
              onClick={handleRemovePreview}
            >
              ×
            </button>
          </div>
        )}

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading}
          className="flex-1 min-w-0 px-3 py-3 text-[hsl(var(--input-foreground))] placeholder-[hsl(var(--input-placeholder))] bg-transparent outline-none disabled:opacity-50"
        />

        {/* Send Button */}
        <button
          type="submit"
          disabled={(!message.trim() && !filePreview) || isLoading}
          className={`flex items-center justify-center w-10 h-10 rounded-full text-[hsl(var(--foreground))] transition-colors ${
            message.trim() || filePreview
              ? "hover:bg-[hsl(var(--button-hover))] hover:cursor-pointer"
              : "opacity-50 cursor-not-allowed"
          }`}
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      </form>

      <p className="text-xs mt-2 font-medium text-[hsl(var(--foreground))] tracking-wide py-1 text-center">
        ---
      </p>
    </div>
  );
}
