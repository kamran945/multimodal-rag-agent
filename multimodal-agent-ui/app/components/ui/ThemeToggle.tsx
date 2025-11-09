"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  // Track current theme state (true = dark)
  const [isDark, setIsDark] = useState(false);

  // On mount → check saved theme preference and apply it
  // useEffect(() => {
  //   const storedTheme = localStorage.getItem("theme");
  //   if (storedTheme === "dark") {
  //     document.documentElement.classList.add("dark");
  //     setIsDark(true);
  //   }
  // }, []);

  useEffect(() => {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "dark") {
      document.documentElement.classList.add("dark");
      const frame = requestAnimationFrame(() => setIsDark(true));
      return () => cancelAnimationFrame(frame);
    }
  }, []);

  // Toggle theme between light and dark modes
  const toggleTheme = () => {
    const html = document.documentElement;
    const newTheme = html.classList.toggle("dark") ? "dark" : "light";
    setIsDark(newTheme === "dark");
    localStorage.setItem("theme", newTheme); // save preference
  };

  return (
    // Outer button (uses your global .button style and HSL vars)
    <button
      onClick={toggleTheme}
      className="cursor-pointer button flex items-center gap-2 transition-colors"
      style={{
        backgroundColor: `hsl(var(--button-background))`,
        color: `hsl(var(--button-foreground))`,
        border: `1px solid hsl(var(--button-border))`,
      }}
      aria-label="Toggle theme"
    >
      {/* Toggle track */}
      <div
        className="relative w-10 h-5 rounded-full transition-colors duration-300"
        style={{
          backgroundColor: isDark
            ? `hsl(var(--button-hover))`
            : `hsl(var(--border-color))`,
        }}
      >
        {/* Toggle thumb (moves left/right) */}
        <div
          className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full transition-transform duration-300"
          style={{
            backgroundColor: `hsl(var(--primary))`,
            transform: isDark ? "translateX(20px)" : "translateX(0)",
          }}
        />
      </div>

      {/* Text label */}
      <span className="text-sm select-none">
        {isDark ? "Dark Mode" : "Light Mode"}
      </span>
    </button>
  );
}
