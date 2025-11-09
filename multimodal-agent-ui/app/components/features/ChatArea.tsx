import React from "react";
import ChatInput from "@/app/components/features/ChatInput";

// --- MainArea Component ---
// Renders the primary content area of the app.
// Includes a scrollable content section and a fixed chat input at the bottom.
export default function ChatArea() {
  const chat_id: string = ""; // Placeholder chat ID (can be replaced dynamically)

  return (
    <div className="main flex flex-col h-[60vh] bg-[hsl(var(--main-background))] text-[hsl(var(--foreground))] ">
      {/* --- Scrollable Content Area --- */}
      <nav className="main-scrollable flex-1 flex flex-col px-6 py-4 justify-end items-center text-4xl font-semibold">
        <div className="">What can i help with?</div>
        {/* Placeholder for additional blocks/components */}
      </nav>

      {/* --- Fixed Bottom Chat Input --- */}
      <ChatInput chat_id={chat_id} />
    </div>
  );
}
