/**
 * Model Context (Refactored)
 *
 * Global context for selected AI model with persistence.
 */

"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { DEFAULT_MODEL, STORAGE_KEYS } from "@/app/lib/constants";

// ============================================================================
// Context Type
// ============================================================================

interface ModelContextType {
  selectedModel: string;
  setSelectedModel: React.Dispatch<React.SetStateAction<string>>;
}

// ============================================================================
// Context Creation
// ============================================================================

const ModelContext = createContext<ModelContextType | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

export const ModelProvider = ({ children }: { children: React.ReactNode }) => {
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL);

  // Load from localStorage on mount
  // useEffect(() => {
  //   if (typeof window !== "undefined") {
  //     const savedModel = localStorage.getItem(STORAGE_KEYS.MODEL);
  //     if (savedModel) setSelectedModel(savedModel);
  //   }
  // }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedModel = localStorage.getItem(STORAGE_KEYS.MODEL);
      if (savedModel) {
        const frame = requestAnimationFrame(() => setSelectedModel(savedModel));
        return () => cancelAnimationFrame(frame);
      }
    }
  }, []);

  // Save to localStorage on change
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEYS.MODEL, selectedModel);
    }
  }, [selectedModel]);

  return (
    <ModelContext.Provider value={{ selectedModel, setSelectedModel }}>
      {children}
    </ModelContext.Provider>
  );
};

// ============================================================================
// Custom Hook
// ============================================================================

export const useModel = () => {
  const context = useContext(ModelContext);
  if (!context) {
    throw new Error("useModel must be used within a ModelProvider");
  }
  return context;
};
