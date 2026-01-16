"use client";

import { Conversation } from "@/lib/api";

interface ConversationListProps {
  conversations: Conversation[];
  selectedId?: number;
  onSelect: (id: number) => void;
  onDelete: (id: number) => void;
  onNewChat: () => void;
}

/**
 * List of conversations with selection and management.
 */
export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onDelete,
  onNewChat,
}: ConversationListProps) {
  return (
    <div className="w-64 border-r bg-gray-50 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <button
          onClick={onNewChat}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          + New Chat
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            No conversations yet
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {conversations.map((conv) => (
              <li
                key={conv.id}
                className={`relative group ${
                  selectedId === conv.id ? "bg-blue-50" : "hover:bg-gray-100"
                }`}
              >
                <button
                  onClick={() => onSelect(conv.id)}
                  className="w-full text-left p-3"
                >
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {conv.preview || "New conversation"}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 flex justify-between">
                    <span>{conv.message_count} messages</span>
                    <span>
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(conv.id);
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete conversation"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
