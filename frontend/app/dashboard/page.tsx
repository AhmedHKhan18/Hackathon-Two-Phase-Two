"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession, authClient, getSession } from "@/lib/auth-client";
import { Navbar } from "@/components/navbar";
import { TaskList } from "@/components/task-list";
import { TaskForm } from "@/components/task-form";
import { Modal } from "@/components/modal";
import { FloatingActionButton } from "@/components/floating-action-button";
import {
  Task,
  TaskCreateRequest,
  TaskUpdateRequest,
  listTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskComplete,
  ApiError,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const { data: sessionData, isPending, error: sessionError, refetch } = useSession();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [sessionChecked, setSessionChecked] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Extract user from session - Better Auth structure
  const user = sessionData?.user;
  const session = sessionData?.session;

  // Debug logging and session verification
  useEffect(() => {
    console.log("Session state:", { sessionData, isPending, sessionError, user, session });

    // If session hook says no pending but no user, try fetching directly
    if (!isPending && !user && !sessionChecked) {
      setSessionChecked(true);
      getSession().then((result) => {
        console.log("Direct getSession result:", result);
        if (result.data?.user) {
          // Session exists, refetch the hook
          refetch();
        }
      });
    }
  }, [sessionData, isPending, sessionError, user, session, sessionChecked, refetch]);

  // Fetch tasks when session is ready
  const fetchTasks = useCallback(async () => {
    if (!user?.id) return;

    setLoading(true);
    setError("");

    try {
      // Get JWT token
      const tokenData = await authClient.token();
      console.log("Token response:", tokenData);
      const token = tokenData.data?.token;

      if (!token) {
        console.log("No token available, tokenData:", tokenData);
        router.push("/signin");
        return;
      }

      console.log("Using token (first 50 chars):", token.substring(0, 50) + "...");
      const fetchedTasks = await listTasks(user.id, token);
      setTasks(fetchedTasks);
    } catch (err) {
      console.error("Fetch tasks error:", err);
      if (err instanceof ApiError) {
        if (err.status === 401) {
          router.push("/signin");
          return;
        }
        setError(err.message);
      } else {
        setError("Failed to load tasks");
      }
    } finally {
      setLoading(false);
    }
  }, [user?.id, router]);

  useEffect(() => {
    // Wait for session to load
    if (isPending) return;

    // Wait for session check to complete before redirecting
    if (!user && !sessionChecked) {
      console.log("Waiting for session verification...");
      return;
    }

    // Redirect unauthenticated users to sign-in only after verification
    if (!user && sessionChecked) {
      console.log("No user after session check, redirecting to signin");
      router.push("/signin");
      return;
    }

    // Fetch tasks when we have a user
    if (user) {
      fetchTasks();
    }
  }, [user, isPending, router, fetchTasks, sessionChecked]);

  const getToken = async (): Promise<string | null> => {
    try {
      const tokenData = await authClient.token();
      return tokenData.data?.token || null;
    } catch {
      return null;
    }
  };

  const handleCreateTask = async (data: TaskCreateRequest | TaskUpdateRequest) => {
    if (!user?.id) return;

    const token = await getToken();
    if (!token) {
      router.push("/signin");
      return;
    }

    try {
      const newTask = await createTask(user.id, data as TaskCreateRequest, token);
      setTasks((prev) => [newTask, ...prev]);
      setIsCreateModalOpen(false); // Close modal after successful creation
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/signin");
        return;
      }
      throw err;
    }
  };

  const handleUpdateTask = async (data: TaskCreateRequest | TaskUpdateRequest) => {
    if (!user?.id || !editingTask) return;

    const token = await getToken();
    if (!token) {
      router.push("/signin");
      return;
    }

    try {
      const updatedTask = await updateTask(
        user.id,
        editingTask.id,
        data as TaskUpdateRequest,
        token
      );
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
      );
      setEditingTask(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/signin");
        return;
      }
      throw err;
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user?.id) return;

    const token = await getToken();
    if (!token) {
      router.push("/signin");
      return;
    }

    try {
      await deleteTask(user.id, taskId, token);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/signin");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    if (!user?.id) return;

    const token = await getToken();
    if (!token) {
      router.push("/signin");
      return;
    }

    try {
      const updatedTask = await toggleTaskComplete(user.id, taskId, token);
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
      );
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/signin");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  // Show loading while checking session
  if (isPending || (!user && !sessionChecked)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
          <div className="text-gray-400 font-medium">Verifying session...</div>
        </div>
      </div>
    );
  }

  // Don't render dashboard if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin"></div>
          <div className="text-gray-400 font-medium">Redirecting...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">
      {/* Navbar */}
      <Navbar user={user} taskCount={tasks.length} />

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error message */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg flex items-start gap-2 animate-scale-in backdrop-blur-sm">
            <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <span className="text-sm">{error}</span>
            </div>
            <button
              onClick={() => setError("")}
              className="text-red-400 hover:text-red-300 transition-colors"
              aria-label="Dismiss error"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Edit Task Form (shown inline when editing) */}
        {editingTask && (
          <div className="mb-8 animate-fade-in">
            <TaskForm
              task={editingTask}
              onSubmit={handleUpdateTask}
              onCancel={handleCancelEdit}
            />
          </div>
        )}

        {/* Task list */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <p className="mt-4 text-gray-400 font-medium">Loading your tasks...</p>
          </div>
        ) : (
          <div className="animate-fade-in">
            <TaskList
              tasks={tasks}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
              onToggleComplete={handleToggleComplete}
            />
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      {!editingTask && (
        <FloatingActionButton onClick={() => setIsCreateModalOpen(true)} />
      )}

      {/* Create Task Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Task"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Modal>
    </div>
  );
}
