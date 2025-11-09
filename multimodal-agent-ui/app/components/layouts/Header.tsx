import React from "react";

// import SignInLink from "@/app/components/ui/SignInLink";
// import ModelSelector from "@/app/components/features/ModelSelector";

// --- Component Props ---
// Expects 'sidebarOpen' to adjust layout depending on sidebar visibility
interface HeaderProps {
  sidebarOpen: boolean;
}

// --- Header Component ---
// Renders the top navigation bar containing the model selector on the left
// and the sign-in link on the right. Adjusts padding based on sidebar state.
const Header: React.FC<HeaderProps> = ({ sidebarOpen }) => {
  return (
    <header
      className="
        topbar h-16 w-full flex items-center justify-between
        px-6 shadow-md sticky top-0
        bg-[hsl(var(--header-background))] text-[hsl(var(--header-foreground))] 
        border-b border-[hsl(var(--border-color))] z-30
      "
    >
      <div
        className={`flex justify-center items-center w-full topbar ${
          !sidebarOpen ? "pl-12" : "pl-0"
        }`}
      >
        <h1 className="text-lg font-semibold accent-text tracking-tight">
          Multimodal RAG&nbsp;
          <span className="text-[hsl(var(--primary))]"></span>
        </h1>
      </div>

      {/* --- Left Section: Model Selector --- */}
      {/* <div className={`flex items-center ${!sidebarOpen ? "pl-12" : "pl-0"}`}>
        <ModelSelector />
      </div> */}

      {/* --- Right Section: Sign In --- */}
      {/* <div className="flex items-center">
        <SignInLink />
      </div> */}
    </header>
  );
};

export default Header;
