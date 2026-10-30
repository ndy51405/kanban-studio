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
- `src/app/page.tsx`: Root route (`/`) rendering `<KanbanBoard />`.
- `src/lib/kanban.ts`: Core domain types (`Card`, `Column`, `BoardData`), initial seed data (`initialData` with 5 columns and 8 cards), `moveCard()` pure function for reordering/moving cards across columns, and `createId()` helper.
- `src/lib/kanban.test.ts`: Unit tests for `moveCard()` (same-column reorder, cross-column move, column drop).
- `src/components/KanbanBoard.tsx`: Main client component (`"use client"`) holding `board` state and `activeCardId` drag state. Wires `DndContext`, column renaming, card creation, card deletion, and `DragOverlay`.
- `src/components/KanbanBoard.test.tsx`: Component tests verifying 5 columns render, column title renaming, and adding/removing a card.
- `src/components/KanbanColumn.tsx`: Droppable column container (`data-testid="column-${column.id}"`) with an editable column title input, `SortableContext` list of cards, empty state drop zone, and `<NewCardForm />`.
- `src/components/KanbanCard.tsx`: Sortable card item (`data-testid="card-${card.id}"`) displaying card title, details, and a "Remove" button.
- `src/components/KanbanCardPreview.tsx`: Presentational card component rendered inside `DragOverlay` while dragging.
- `src/components/NewCardForm.tsx`: Toggleable inline form inside each column for creating a new card with `title` and `details`.
- `tests/kanban.spec.ts`: Playwright E2E tests verifying board load, card creation, and mouse drag-and-drop between columns.

## Commands

- `npm run dev`: Start Next.js development server
- `npm run build`: Build production Next.js bundle (to be configured with `output: "export"` in Part 3 for static serving by FastAPI)
- `npm run test:unit`: Run Vitest unit and component tests once
- `npm run test:e2e`: Run Playwright E2E tests
- `npm run test:all`: Run unit tests followed by E2E tests

