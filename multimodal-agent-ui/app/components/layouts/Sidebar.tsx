/**
 * Sidebar Component (FIXED - No Infinite Loop)
 *
 * Main navigation sidebar with chat history and media gallery.
 * Uses stable selector to prevent infinite re-renders.
 */

"use client";

import React, { useState, useMemo } from "react";
import { Menu } from "lucide-react";
import { useChatStore } from "@/app/lib/store/chatStore";
import NewChat from "@/app/components/ui/NewChat";
import ChatHistory from "@/app/components/features/ChatHistory";
import HomeButton from "@/app/components/ui/HomeButton";
import ThemeToggle from "@/app/components/ui/ThemeToggle";
import MediaGallery from "@/app/components/features/MediaGallery";

// ============================================================================
// Component Props
// ============================================================================

interface SidebarProps {
  isOpen: boolean;
  toggle: () => void;
}

// ============================================================================
// Component
// ============================================================================

const Sidebar: React.FC<SidebarProps> = ({ isOpen, toggle }) => {
  // ✅ Use direct state access instead of selector
  const messages = useChatStore((state) => state.messages);

  // ✅ Compute unique chat IDs with useMemo (stable reference)
  const uniqueChatIds = useMemo(() => {
    return Array.from(new Set(messages.map((m) => m.chat_id)));
  }, [messages]);

  const [openDropdown, setOpenDropdown] = useState<"chat" | "media" | null>(
    null
  );

  const toggleDropdown = (tab: "chat" | "media") => {
    setOpenDropdown((prev) => (prev === tab ? null : tab));
  };

  return (
    <>
      {/* Hamburger Menu Toggle */}
      <button
        className={`fixed top-4 z-50 bg-[hsl(var(--sidebar-background))] 
        text-[hsl(var(--sidebar-foreground))] p-2 rounded-md shadow-md 
        transition-all duration-300 ${isOpen ? "left-52" : "left-4"}
        hover:cursor-pointer`}
        onClick={toggle}
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Sidebar Panel */}
      <aside
        className={`sidebar w-64 flex flex-col fixed top-0 left-0 h-full
          bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))]
          border-r border-[hsl(var(--border-color))] shadow-lg
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full"} z-40`}
      >
        {/* Top Fixed Section */}
        <div className="flex flex-col px-4 pt-4 pb-2 bg-[hsl(var(--sidebar-background))] shrink-0 border-b border-[hsl(var(--border-color))]">
          {/* Logo/Home Button */}
          <div className="font-bold text-lg mb-3 select-none">
            <HomeButton />
          </div>

          {/* New Chat Button */}
          <NewChat />

          {/* Tab Buttons */}
          <div className="flex flex-col gap-2 mt-3">
            <button
              className={`cursor-pointer text-xs py-1 px-2 rounded ${
                openDropdown === "chat"
                  ? "bg-[hsl(var(--button-background))] font-medium"
                  : "bg-transparent hover:bg-[hsl(var(--button-hover))]"
              } transition-colors duration-200`}
              onClick={() => toggleDropdown("chat")}
            >
              Chat History
            </button>
            <button
              className={`cursor-pointer text-xs py-1 px-2 rounded ${
                openDropdown === "media"
                  ? "bg-[hsl(var(--button-background))] font-medium"
                  : "bg-transparent hover:bg-[hsl(var(--button-hover))]"
              } transition-colors duration-200`}
              onClick={() => toggleDropdown("media")}
            >
              Media Gallery
            </button>
          </div>
        </div>

        {/* Scrollable Content Area */}
        <nav className="flex-1 overflow-y-auto px-4 py-3 scrollbar-thin scrollbar-thumb-[hsl(var(--border-color))] scrollbar-track-[hsl(var(--sidebar-background))]">
          {/* Chat History Dropdown */}
          {openDropdown === "chat" && (
            <div className="chat-history">
              {uniqueChatIds.length > 0 ? (
                <>
                  <p className="chat-history-title">Chat History</p>
                  <div className="chat-history-list flex flex-col gap-2">
                    {uniqueChatIds.map((chatId) => (
                      <ChatHistory key={chatId} chat_id={chatId} />
                    ))}
                  </div>
                </>
              ) : (
                <div className="chat-history-empty">
                  <p>No chat history</p>
                </div>
              )}
            </div>
          )}

          {/* Media Gallery Dropdown */}
          {openDropdown === "media" && <MediaGallery />}
        </nav>

        {/* Theme Toggle (Fixed at bottom) */}
        <div className="mt-auto p-4 border-t border-[hsl(var(--border-color))] flex justify-end shrink-0">
          <ThemeToggle />
        </div>
      </aside>

      {/* Overlay for Small Screens */}
      {isOpen && typeof window !== "undefined" && window.innerWidth < 768 && (
        <div className="fixed inset-0 bg-black/30 z-30" onClick={toggle}></div>
      )}
    </>
  );
};

export default Sidebar;
