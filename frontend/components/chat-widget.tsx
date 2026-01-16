"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useSession, authClient } from "@/lib/auth-client";
import {
  sendChatMessage,
  ChatMessage,
  ApiError,
} from "@/lib/api";

/**
 * Floating chat widget with expandable chat window.
 */
export function ChatWidget() {
  const { data: session } = useSession();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSendMessage = useCallback(async () => {
    const message = inputValue.trim();
    if (!message || !session?.user?.id || sendingMessage) return;

    try {
      setSendingMessage(true);
      setError(null);
      setInputValue("");

      const tokenResponse = await authClient.token();
      const token = tokenResponse.data?.token;
      if (!token) return;

      // Optimistically add user message
      const tempUserMessage: ChatMessage = {
        id: Date.now(),
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMessage]);

      // Send to API
      const response = await sendChatMessage(
        session.user.id,
        { message, conversation_id: conversationId },
        token
      );

      // Update conversation ID
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.response,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Failed to send message:", err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to send message. Please try again.");
      }
      // Remove optimistic message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSendingMessage(false);
    }
  }, [inputValue, session?.user?.id, sendingMessage, conversationId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  };

  if (!session?.user) return null;

  return (
    <>
      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-44 right-6 w-96 h-[500px] bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 flex flex-col z-50 animate-fade-in overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 flex items-center justify-between rounded-t-2xl">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">Todo AI Assistant</h3>
                <p className="text-white/70 text-xs">Ask me to manage your tasks</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleNewChat}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="New chat"
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-800">
            {messages.length === 0 && !sendingMessage ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <p className="font-medium text-sm">Start a conversation</p>
                <p className="text-xs text-gray-500 mt-1 text-center px-4">
                  Try: "Add a task to buy groceries" or "Show my tasks"
                </p>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                        msg.role === "user"
                          ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                          : "bg-gray-700 text-gray-100"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      <p className={`text-xs mt-1 ${msg.role === "user" ? "text-white/60" : "text-gray-500"}`}>
                        {new Date(msg.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                ))}

                {sendingMessage && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700 rounded-2xl px-4 py-3">
                      <div className="flex items-center space-x-1.5">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Error */}
          {error && (
            <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/30">
              <p className="text-red-400 text-xs">{error}</p>
            </div>
          )}

          {/* Input */}
          <div className="p-3 bg-gray-900 border-t border-gray-700">
            <div className="flex items-end gap-2">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                disabled={sendingMessage}
                rows={1}
                className="flex-1 resize-none rounded-xl border border-gray-600 bg-gray-800 text-white placeholder-gray-500 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                style={{ minHeight: "44px", maxHeight: "100px" }}
              />
              <button
                onClick={handleSendMessage}
                disabled={sendingMessage || !inputValue.trim()}
                className="h-11 w-11 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl flex items-center justify-center hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-28 right-6 w-14 h-14 rounded-full shadow-lg hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-purple-400/50 transition-all duration-200 hover:scale-110 active:scale-95 z-50 flex items-center justify-center ${
          isOpen
            ? "bg-gray-700 hover:bg-gray-600"
            : "bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-purple-500/25"
        }`}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? (
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}

        {/* Notification dot when closed */}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-gray-900 animate-pulse" />
        )}
      </button>
    </>
  );
}
