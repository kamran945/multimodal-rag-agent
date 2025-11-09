"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/app/components/layouts/Sidebar";
import Header from "@/app/components/layouts/Header";

// --- Component Props ---
// Expects 'children' representing the main content to render inside the layout
interface ClientLayoutProps {
  children: React.ReactNode;
}

// --- ClientLayout Component ---
// Provides the overall layout structure with a responsive sidebar, header, and main content area.
export default function ClientLayout({ children }: ClientLayoutProps) {
  // --- Sidebar State ---
  // null = unknown initially, true = open, false = closed
  const [sidebarOpen, setSidebarOpen] = useState<boolean | null>(null);

  // --- Handle Window Resize ---
  // Updates sidebar visibility based on screen width
  const handleResize = () => {
    if (window.innerWidth >= 768) {
      setSidebarOpen(true); // Medium+ screens: show sidebar
    } else {
      setSidebarOpen(false); // Small screens: hide sidebar
    }
  };

  // useEffect(() => {
  //   handleResize(); // Set initial sidebar state on mount
  //   window.addEventListener("resize", handleResize); // Update on window resize
  //   return () => window.removeEventListener("resize", handleResize); // Cleanup listener
  // }, []);

  useEffect(() => {
    const frame = requestAnimationFrame(handleResize);
    window.addEventListener("resize", handleResize); // Set initial sidebar state on mount,Update on window resize
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", handleResize); // Cleanup listener
    };
  }, []);

  // --- Avoid Rendering Until Client-Side Measurement ---
  // Ensures sidebar state is determined before rendering to prevent layout shift
  if (sidebarOpen === null) return null;

  return (
    <div className="flex min-h-screen">
      {/* --- Sidebar --- */}
      <Sidebar
        isOpen={sidebarOpen}
        toggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* --- Main Panel --- */}
      <div
        className={`flex flex-col flex-1 transition-all duration-300 ease-in-out bg-[hsl(var(--main-background))] ${
          sidebarOpen ? "md:ml-64" : "ml-0" // Adjust main panel margin when sidebar is open
        }`}
      >
        {/* Header */}
        <Header sidebarOpen={sidebarOpen} />

        {/* --- Scrollable Middle Content --- */}
        <div className="flex-1">{children}</div>
      </div>
    </div>
  );
}
