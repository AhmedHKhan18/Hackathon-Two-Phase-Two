"use client";

import { useState, useEffect } from "react";
import { Task, TaskCreateRequest, TaskUpdateRequest } from "@/lib/api";

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskCreateRequest | TaskUpdateRequest) => Promise<void>;
  onCancel?: () => void;
}

export function TaskForm({ task, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isEditMode = !!task;

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    if (title.length > 200) {
      setError("Title must be 200 characters or less");
      return;
    }

    if (description.length > 2000) {
      setError("Description must be 2000 characters or less");
      return;
    }

    setLoading(true);

    try {
      if (isEditMode) {
        await onSubmit({
          title: title.trim(),
          description: description.trim() || undefined,
        } as TaskUpdateRequest);
      } else {
        await onSubmit({
          title: title.trim(),
          description: description.trim() || undefined,
        } as TaskCreateRequest);
      }

      // Clear form if not in edit mode
      if (!isEditMode) {
        setTitle("");
        setDescription("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg flex items-start gap-2 animate-scale-in">
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span className="text-sm">{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-semibold text-gray-200 mb-2">
          Task Title <span className="text-red-400">*</span>
        </label>
        <input
          id="title"
          type="text"
          required
          maxLength={200}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          placeholder="What needs to be done?"
          autoFocus
        />
        <div className="mt-1.5 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            {title.length}/200 characters
          </p>
          {title.length > 180 && (
            <span className="text-xs text-orange-400 font-medium">
              {200 - title.length} characters left
            </span>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-semibold text-gray-200 mb-2">
          Description <span className="text-gray-500 font-normal">(optional)</span>
        </label>
        <textarea
          id="description"
          maxLength={2000}
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
          placeholder="Add more details about this task..."
        />
        <div className="mt-1.5 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            {description.length}/2000 characters
          </p>
          {description.length > 1800 && (
            <span className="text-xs text-orange-400 font-medium">
              {2000 - description.length} characters left
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 px-5 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-blue-500/25 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {isEditMode ? "Saving..." : "Creating..."}
            </span>
          ) : (
            <>
              {isEditMode ? (
                <>
                  <svg className="w-5 h-5 inline-block mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Save Changes
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 inline-block mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Task
                </>
              )}
            </>
          )}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-5 py-3 bg-gray-700 text-gray-200 font-medium rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
