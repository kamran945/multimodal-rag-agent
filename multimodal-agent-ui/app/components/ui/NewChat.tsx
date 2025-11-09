"use client";

import React from "react";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

// --- NewChat Component ---
// Renders a button that creates a new chat in Firestore and navigates to it.
const NewChat = () => {
  const router = useRouter();

  // --- Start a New Chat ---
  // Adds a new chat document in Firestore and navigates to its page
  const startNewChat = async () => {
    const chatDocumentId = crypto.randomUUID();
    // Navigate to the newly created chat page
    router.push(`/chat/${chatDocumentId}`);
  };

  return (
    <div className="w-full flex justify-center">
      {/* --- New Chat Button --- */}
      <button
        onClick={startNewChat}
        className="w-full flex items-center justify-center gap-2
          text-sm md:text-base p-3 rounded-xl font-medium
          bg-transparent text-[hsl(var(--sidebar-foreground))]/70
          border border-transparent
          hover:text-[hsl(var(--sidebar-foreground))] 
          hover:border-[hsl(var(--border-color))]
          hover:bg-[hsl(var(--button-hover))]
          hover:cursor-pointer
          transition-all duration-200 active:scale-[0.98]"
      >
        {/* Plus icon */}
        <Plus className="w-4 h-4" />
        New Chat
      </button>
    </div>
  );
};

export default NewChat;
