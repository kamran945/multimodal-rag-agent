"use client";

import { Home } from "lucide-react";
import Link from "next/link";
import React from "react";

// --- HomeButton Component ---
// Renders a clickable icon button that navigates to the homepage ("/").
// Styled with hover effects and responsive padding.
const HomeButton = () => {
  return (
    <Link
      href="/"
      className="
        inline-flex items-center justify-center
        p-2 md:p-2 rounded-md
        text-[hsl(var(--sidebar-foreground))]/70
        border border-[hsl(var(--border-color))]
        hover:text-[hsl(var(--sidebar-foreground))]
        hover:border-[hsl(var(--button-border))]
        hover:bg-[hsl(var(--button-hover))]
        transition-all duration-300
      "
    >
      {/* Home icon */}
      <Home className="text-[hsl(var(--foreground))]" />
    </Link>
  );
};

export default HomeButton;
