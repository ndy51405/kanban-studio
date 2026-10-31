import type { BoardData } from "./kanban";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  username: string;
  status: string;
}

export async function loginUser(payload: LoginPayload): Promise<LoginResponse> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Invalid username or password");
  }

  return res.json();
}

export async function fetchKanbanBoard(): Promise<BoardData> {
  const res = await fetch("/api/kanban");
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to load kanban board");
  }
  return res.json();
}

export async function updateKanbanBoard(board: BoardData): Promise<BoardData> {
  const res = await fetch("/api/kanban", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(board),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to save kanban board");
  }

  return res.json();
}

