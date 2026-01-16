/**
 * Centralized API client for backend communication.
 * All requests include JWT token from Better Auth session.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API error with status code and message.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Task type matching backend TaskResponse schema.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Request body for creating a task.
 */
export interface TaskCreateRequest {
  title: string;
  description?: string;
}

/**
 * Request body for updating a task.
 */
export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * Make an authenticated API request.
 *
 * @param path - API path (e.g., "/api/user123/tasks")
 * @param options - Fetch options
 * @param token - JWT token from session
 * @returns Response data
 * @throws ApiError for non-2xx responses
 */
async function apiRequest<T>(
  path: string,
  options: RequestInit,
  token: string
): Promise<T> {
  const url = `${API_BASE}${path}`;

  console.log(`API Request: ${options.method || 'GET'} ${url}`);

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });
  } catch (fetchError) {
    console.error("Fetch error:", fetchError);
    console.error("URL attempted:", url);
    console.error("API_BASE:", API_BASE);
    throw fetchError;
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `Request failed with status ${response.status}`;
    throw new ApiError(response.status, message);
  }

  return response.json();
}

/**
 * List all tasks for the authenticated user.
 *
 * @param userId - User ID from session
 * @param token - JWT token from session
 * @returns Array of tasks
 */
export async function listTasks(userId: string, token: string): Promise<Task[]> {
  return apiRequest<Task[]>(`/api/${userId}/tasks`, { method: "GET" }, token);
}

/**
 * Create a new task.
 *
 * @param userId - User ID from session
 * @param data - Task creation data
 * @param token - JWT token from session
 * @returns Created task
 */
export async function createTask(
  userId: string,
  data: TaskCreateRequest,
  token: string
): Promise<Task> {
  return apiRequest<Task>(
    `/api/${userId}/tasks`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token
  );
}

/**
 * Get a single task by ID.
 *
 * @param userId - User ID from session
 * @param taskId - Task ID
 * @param token - JWT token from session
 * @returns Task
 */
export async function getTask(
  userId: string,
  taskId: number,
  token: string
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, { method: "GET" }, token);
}

/**
 * Update an existing task.
 *
 * @param userId - User ID from session
 * @param taskId - Task ID
 * @param data - Fields to update
 * @param token - JWT token from session
 * @returns Updated task
 */
export async function updateTask(
  userId: string,
  taskId: number,
  data: TaskUpdateRequest,
  token: string
): Promise<Task> {
  return apiRequest<Task>(
    `/api/${userId}/tasks/${taskId}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
    token
  );
}

/**
 * Delete a task.
 *
 * @param userId - User ID from session
 * @param taskId - Task ID
 * @param token - JWT token from session
 * @returns Delete confirmation
 */
export async function deleteTask(
  userId: string,
  taskId: number,
  token: string
): Promise<{ deleted: boolean }> {
  return apiRequest<{ deleted: boolean }>(
    `/api/${userId}/tasks/${taskId}`,
    { method: "DELETE" },
    token
  );
}

/**
 * Toggle task completion status.
 *
 * @param userId - User ID from session
 * @param taskId - Task ID
 * @param token - JWT token from session
 * @returns Updated task
 */
export async function toggleTaskComplete(
  userId: string,
  taskId: number,
  token: string
): Promise<Task> {
  return apiRequest<Task>(
    `/api/${userId}/tasks/${taskId}/complete`,
    { method: "PATCH" },
    token
  );
}

// ============================================================================
// Phase III: Chat API Types and Functions
// ============================================================================

/**
 * Tool call made by the AI agent.
 */
export interface ToolCall {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

/**
 * Request body for chat endpoint.
 */
export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

/**
 * Response from chat endpoint.
 */
export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

/**
 * Conversation summary for listing.
 */
export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string | null;
}

/**
 * Chat message.
 */
export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

/**
 * Conversation with full message history.
 */
export interface ConversationDetail {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

/**
 * Send a chat message to the AI agent.
 *
 * @param userId - User ID from session
 * @param data - Chat request with message and optional conversation_id
 * @param token - JWT token from session
 * @returns Chat response with agent's reply and tool calls
 */
export async function sendChatMessage(
  userId: string,
  data: ChatRequest,
  token: string
): Promise<ChatResponse> {
  return apiRequest<ChatResponse>(
    `/api/${userId}/chat`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token
  );
}

/**
 * List all conversations for the user.
 *
 * @param userId - User ID from session
 * @param token - JWT token from session
 * @returns Array of conversation summaries
 */
export async function listConversations(
  userId: string,
  token: string
): Promise<Conversation[]> {
  return apiRequest<Conversation[]>(
    `/api/${userId}/conversations`,
    { method: "GET" },
    token
  );
}

/**
 * Get a conversation with all messages.
 *
 * @param userId - User ID from session
 * @param conversationId - Conversation ID
 * @param token - JWT token from session
 * @returns Conversation with message history
 */
export async function getConversation(
  userId: string,
  conversationId: number,
  token: string
): Promise<ConversationDetail> {
  return apiRequest<ConversationDetail>(
    `/api/${userId}/conversations/${conversationId}`,
    { method: "GET" },
    token
  );
}

/**
 * Delete a conversation and all its messages.
 *
 * @param userId - User ID from session
 * @param conversationId - Conversation ID
 * @param token - JWT token from session
 * @returns Delete confirmation
 */
export async function deleteConversation(
  userId: string,
  conversationId: number,
  token: string
): Promise<{ deleted: boolean }> {
  return apiRequest<{ deleted: boolean }>(
    `/api/${userId}/conversations/${conversationId}`,
    { method: "DELETE" },
    token
  );
}
