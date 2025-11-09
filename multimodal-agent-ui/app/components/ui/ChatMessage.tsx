/**
 * ChatMessage Component (Refactored)
 *
 * Pure presentational component for rendering a single message.
 * Supports text, image, and video content.
 */

/* eslint-disable @next/next/no-img-element */

"use client";

import React from "react";
import { Bot, User } from "lucide-react";
// import Image from "next/image";
import type { Message } from "@/app/types";

// ============================================================================
// Component Props
// ============================================================================

interface ChatMessageProps {
  message: Message;
}

// ============================================================================
// Component
// ============================================================================

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isAi = message.role === "ai";

  return (
    <div
      className={`flex items-start gap-3 ${
        isAi ? "justify-start" : "justify-end"
      }`}
    >
      {/* AI Avatar */}
      {isAi && (
        <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center border border-[hsl(var(--border-color))] mt-1">
          <Bot size={18} className="text-[hsl(var(--foreground))] opacity-80" />
        </div>
      )}

      {/* Message Bubble */}
      <div className={!isAi ? "chat-user" : "chat-ai"}>
        {/* Text Content */}
        {message.message_content && <p>{message.message_content}</p>}

        {/* Image Attachment */}
        {message.message_image && (
          <img
            src={message.message_image}
            // <Image
            //   src={message.message_image}
            alt="uploaded image"
            className="rounded-lg max-w-xs mt-2 object-cover"
          />
        )}

        {/* Video Attachment */}
        {message.message_video && (
          <video
            src={message.message_video}
            controls
            className="rounded-lg max-w-xs mt-2 object-cover"
          />
        )}
      </div>

      {/* User Avatar */}
      {!isAi && (
        <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center border border-[hsl(var(--border-color))] mt-1">
          <User
            size={18}
            className="text-[hsl(var(--foreground))] opacity-80"
          />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
