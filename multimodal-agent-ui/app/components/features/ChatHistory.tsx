/**
 * ChatHistory Component (FIXED - No Infinite Loop)
 *
 * Displays a single chat history item with delete functionality.
 * Uses direct state access with useMemo for filtering.
 */

"use client";

import Link from "next/link";
import { MessageCircle, Trash } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useMemo } from "react";
import { useChatStore } from "@/app/lib/store/chatStore";

// ============================================================================
// Component Props
// ============================================================================

interface ChatHistoryProps {
  chat_id: string;
}

// ============================================================================
// Component
// ============================================================================

const ChatHistory = ({ chat_id }: ChatHistoryProps) => {
  const pathname = usePathname();
  const router = useRouter();
  const [active, setActive] = useState(false);

  // ✅ FIX: Use direct state access
  const allMessages = useChatStore((state) => state.messages);
  const removeChat = useChatStore((state) => state.removeChat);

  // ✅ FIX: Filter messages with useMemo
  const chatMessages = useMemo(() => {
    return allMessages.filter((m) => m.chat_id === chat_id);
  }, [allMessages, chat_id]);

  // Get last message text
  const lastMessage = chatMessages[chatMessages.length - 1];
  const chatText = lastMessage?.message_content || "new chat";

  // Determine if this chat is active
  // useEffect(() => {
  //   if (!pathname) return;
  //   setActive(pathname.includes(chat_id));
  // }, [pathname, chat_id]);

  useEffect(() => {
    if (!pathname) return;
    const frame = requestAnimationFrame(() =>
      setActive(pathname.includes(chat_id))
    );
    return () => cancelAnimationFrame(frame);
  }, [pathname, chat_id]);

  // Handle chat deletion
  const handleRemoveChat = async () => {
    removeChat(chat_id);
    if (active) router.push("/");
  };

  // ------------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------------

  return (
    <div className="flex flex-col gap-1">
      <div
        className={`w-full flex items-center justify-center gap-2
        text-sm md:text-base px-1 rounded-xl font-medium
        transition-all duration-200 active:scale-[0.98]
        ${
          active
            ? "bg-[hsl(var(--button-hover))] text-[hsl(var(--foreground))] border border-[hsl(var(--border-color))]"
            : "bg-transparent text-[hsl(var(--sidebar-foreground))]/70 border border-transparent hover:text-[hsl(var(--sidebar-foreground))] hover:border-[hsl(var(--border-color))] hover:bg-[hsl(var(--button-hover))]"
        }`}
      >
        <Link
          href={`/chat/${chat_id}`}
          className="flex items-center gap-3 flex-1 overflow-hidden"
        >
          <MessageCircle
            className="text-[hsl(var(--foreground))] shrink-0"
            size={18}
          />
          <p className="truncate text-sm font-medium tracking-wide text-[hsl(var(--foreground))]">
            {chatText}
          </p>
        </Link>
        <button
          onClick={handleRemoveChat}
          className="flex items-center justify-center p-1.5 rounded-lg
          text-[hsl(var(--foreground))]/60
          hover:text-[hsl(var(--foreground))]
          hover:bg-[hsl(var(--button-hover))]
          hover:cursor-pointer
          transition-colors duration-200"
        >
          <Trash size={16} />
        </button>
      </div>
    </div>
  );
};

export default ChatHistory;
