"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * Chat input field with send button and enter key support.
 */
export function ChatInput({
  onSend,
  disabled,
  placeholder = "Type a message...",
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const charCount = message.length;
  const maxChars = 2000;
  const isOverLimit = charCount > maxChars;

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`w-full resize-none rounded-lg border px-4 py-2 pr-16 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed ${
              isOverLimit ? "border-red-500" : "border-gray-300"
            }`}
            style={{
              minHeight: "44px",
              maxHeight: "120px",
            }}
          />
          <span
            className={`absolute right-3 bottom-2 text-xs ${
              isOverLimit ? "text-red-500" : "text-gray-400"
            }`}
          >
            {charCount}/{maxChars}
          </span>
        </div>
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim() || isOverLimit}
          className="h-11 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
      {isOverLimit && (
        <p className="text-red-500 text-sm mt-1">
          Message exceeds {maxChars} character limit
        </p>
      )}
    </div>
  );
}
