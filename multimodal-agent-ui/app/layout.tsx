import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "react-hot-toast";
import "@/app/globals.css";
import { ModelProvider } from "@/app/context/ModelContext";
import ClientLayout from "@/app/components/layouts/ClientLayout"; // new client-only layout

// --- Google Fonts Setup ---
// Load Geist Sans and Geist Mono with CSS variables for consistent font usage
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// --- Page Metadata ---
// Global metadata for SEO and browser tab display
export const metadata: Metadata = {
  title: "Agent Chat UI",
  description: "It is an Agent Chat user interface.",
};

// --- RootLayout Component ---
export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* --- Custom Model Provider Context --- */}
        <ModelProvider>
          {/* --- Client-side Layout Wrapper --- */}
          <ClientLayout>{children}</ClientLayout>
        </ModelProvider>

        {/* --- Toast Notifications --- */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000, // ✅ Default 4 seconds (can be overridden)
            style: {
              backgroundColor: "hsl(var(--sidebar-background))",
              color: "hsl(var(--sidebar-foreground))",
              fontSize: "14px",
              padding: "12px 16px",
            },
            // ✅ Custom styling for different types
            success: {
              duration: 3000,
              iconTheme: {
                primary: "hsl(var(--primary))",
                secondary: "white",
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: "#ef4444",
                secondary: "white",
              },
            },
            loading: {
              duration: Infinity, // ✅ Loading toasts stay until dismissed
            },
          }}
        />
      </body>
    </html>
  );
}
