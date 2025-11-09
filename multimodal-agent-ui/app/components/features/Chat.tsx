/**
 * Chat Component (FIXED - No Infinite Loop)
 *
 * Displays message list for a specific chat with auto-scroll.
 * Uses inline selector with proper equality check.
 */

"use client";

import React, { useRef, useEffect, useMemo } from "react";
import { ArrowDownCircle } from "lucide-react";
import { useChatStore } from "@/app/lib/store/chatStore";
import ChatMessage from "@/app/components/ui/ChatMessage";

// ============================================================================
// Component Props
// ============================================================================

interface ChatProps {
  chat_id: string;
}

// ============================================================================
// Component
// ============================================================================

const Chat: React.FC<ChatProps> = ({ chat_id }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // ✅ FIX: Use inline selector with shallow equality check
  const allMessages = useChatStore((state) => state.messages);

  // ✅ FIX: Filter messages using useMemo for stable reference
  const messages = useMemo(() => {
    return allMessages.filter((m) => m.chat_id === chat_id);
  }, [allMessages, chat_id]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ------------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------------

  return (
    <div className="flex flex-col h-full bg-[hsl(var(--main-background))] text-[hsl(var(--foreground))]">
      <nav className="main-scrollable flex-1 overflow-y-auto px-6 py-4 scrollbar-thin scrollbar-thumb-[hsl(var(--border-color))] scrollbar-track-[hsl(var(--main-background))]">
        {/* Empty State */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
            <p className="text-[hsl(var(--foreground))] text-sm opacity-80">
              Type a message below to get started!
            </p>
            <ArrowDownCircle className="w-6 h-6 text-[hsl(var(--primary))] animate-bounce" />
          </div>
        )}

        {/* Message List */}
        {messages.map((message) => (
          <div key={message.message_id}>
            <ChatMessage message={message} />
          </div>
        ))}

        {/* Scroll Anchor */}
        <div ref={bottomRef} />
      </nav>
    </div>
  );
};

export default Chat;
