# Frontend Architecture & Existing Codebase

## Overview

The `frontend/` directory contains a Next.js 16 (App Router) and React 19 TypeScript application styled with Tailwind CSS v4. It currently implements a standalone, client-side single-board Kanban workspace ("Kanban Studio") using `@dnd-kit` for drag-and-drop interactions.

## Tech Stack

- **Framework**: Next.js 16.1.6 (`src/app`), React 19.2.3, TypeScript 5
- **Styling**: Tailwind CSS v4 (`@tailwindcss/postcss`) with custom CSS variables defined in `src/app/globals.css`
- **Drag and Drop**: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- **Unit Testing**: Vitest 3 + React Testing Library + `@testing-library/user-event` (`jsdom` environment)
- **E2E Testing**: Playwright (`@playwright/test`) targeting Chromium at `http://127.0.0.1:3000`

## Directory Structure

- `src/app/layout.tsx`: Root layout configuring Google Fonts (`Space_Grotesk` as `--font-display` and `Manrope` as `--font-body`) and metadata.
- `src/app/globals.css`: Defines the project color variables (`--accent-yellow`, `--primary-blue`, `--secondary-purple`, `--navy-dark`, `--gray-text`, plus surface and shadow tokens) and base typography styles.
- `src/app/page.tsx`: Root route (`/`) managing client authentication state (`localStorage`). Renders `<LoginForm />` when unauthenticated and `<KanbanBoard />` with logout handling when signed in.
- `src/app/page.test.tsx`: Component tests for the authentication and session persistence flow on `/`.
- `src/lib/api.ts`: Typed API client for FastAPI endpoints (`loginUser` to `POST /api/auth/login`, `fetchKanbanBoard` to `GET /api/kanban`, `updateKanbanBoard` to `PUT /api/kanban`, and `sendChatMessage` to `POST /api/chat`).
- `src/lib/api.test.ts`: Unit tests verifying API request formats and error propagation for all endpoints.
- `src/lib/kanban.ts`: Core domain types (`Card`, `Column`, `BoardData`), initial seed data (`initialData` with 5 columns and 8 cards), `moveCard()` pure function for reordering/moving cards across columns, and `createId()` helper.
- `src/lib/kanban.test.ts`: Unit tests for `moveCard()` (same-column reorder, cross-column move, column drop).
- `src/components/LoginForm.tsx`: Accessible sign-in form styled with project tokens, validating against hardcoded `user` / `password` credentials and displaying inline errors.
- `src/components/LoginForm.test.tsx`: Unit tests for `LoginForm` input fields, credential validation, error states, and submission.
- `src/components/KanbanBoard.tsx`: Main client component (`"use client"`) holding `board` state and `activeCardId` drag state. Supports `user` and `onLogout` props, rendering a "Log out" button and "AI Assistant" toggle button in the header alongside `DndContext`, column renaming, card creation, card editing, card deletion, `DragOverlay`, and `ChatSidebar`.
- `src/components/KanbanBoard.test.tsx`: Component tests verifying 5 columns render, column title renaming, adding/editing/removing a card, logout action callback, and AI assistant toggle button.
- `src/components/ChatSidebar.tsx`: AI assistant copilot sidebar (`"use client"`) maintaining session conversation history, sending messages to `POST /api/chat`, rendering user/assistant bubbles with board update indicators, suggestion chips, loading states, and triggering board state updates.
- `src/components/ChatSidebar.test.tsx`: Unit tests for `ChatSidebar` message rendering, history passing, suggestion clicks, loading states, and board update callbacks.
- `src/components/KanbanColumn.tsx`: Droppable column container (`data-testid="column-${column.id}"`) with an editable column title input, `SortableContext` list of cards, empty state drop zone, and `<NewCardForm />`.
- `src/components/KanbanCard.tsx`: Sortable card item (`data-testid="card-${card.id}"`) displaying card title, details, blue pencil edit icon, and gray trash can delete icon. "Edit" swaps in an inline form (title/details) and disables dragging while editing.
- `src/components/KanbanCardPreview.tsx`: Presentational card component rendered inside `DragOverlay` while dragging.
- `src/components/NewCardForm.tsx`: Toggleable inline form inside each column with a blue plus icon button for creating a new card with `title` and `details`.
- `tests/kanban.spec.ts`: Playwright E2E tests verifying board load, column rename, card add/edit/delete, mouse drag-and-drop between columns, persistence across page reload, and AI chat assistant toggling, prompt suggestions, and board updates.

## Commands

- `npm run dev`: Start Next.js development server
- `npm run build`: Static export (`output: "export"`) to `out/`, served by FastAPI at `/` (backend defaults `STATIC_DIR` to `frontend/out`; Docker copies it to `/app/static`)
- `npm run test:unit`: Run Vitest unit and component tests once
- `npm run test:e2e`: Run Playwright E2E tests against FastAPI at `http://127.0.0.1:8000` (builds and starts the backend with `uv` unless a server, e.g. the Docker container, is already running there)
- `npm run test:all`: Run unit tests followed by E2E tests

