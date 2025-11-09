"use client";

// import React, { useState } from "react";
import { useParams } from "next/navigation";

import ChatInput from "@/app/components/features/ChatInput";
import Chat from "@/app/components/features/Chat";

// --- Chat Page Component ---
// Displays the chat interface including the message list and input field.
// Retrieves the chat ID from URL parameters and passes it to child components.
const ChatPage = () => {
  // --- Retrieve Chat ID from URL ---
  const params = useParams();
  const chat_id = params?.chat_id as string; // Chat chat_id used to fetch and send messages

  return (
    <div className="main flex flex-col h-full bg-[hsl(var(--main-background))] text-[hsl(var(--foreground))] ">
      {/* --- Chat Display Area --- */}
      <div className="flex-1 overflow-y-auto main-scrollable border border-[hsl(var(--border-color))] rounded-lg">
        {/* Renders the list of messages for the current chat */}
        <Chat chat_id={chat_id} />
      </div>

      {/* --- Chat Input Area --- */}
      <div className="mt-4 sticky bottom-0 shrink-0">
        {/* Renders the input box for sending new messages */}
        <ChatInput chat_id={chat_id} />
      </div>
    </div>
  );
};

export default ChatPage;
