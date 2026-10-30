# Unit Testing Guide

## Overview

Unit tests validate isolated functions, components, and API routes quickly without requiring a real browser or external network services. The project uses **Vitest + React Testing Library** for the Next.js frontend and **pytest + FastAPI TestClient** for the Python backend.

---

## Frontend Unit Tests (`frontend/`)

### Stack & Configuration

- **Test Runner**: [Vitest](https://vitest.dev/) (`vitest.config.ts`)
- **DOM Environment**: `jsdom`
- **Assertions & Helpers**: `@testing-library/jest-dom` (loaded via `src/test/setup.ts`), `@testing-library/react`, `@testing-library/user-event`
- **File Pattern**: `src/**/*.{test,spec}.{ts,tsx}` (excludes `tests/`, which is reserved for Playwright E2E tests)
- **Path Alias**: `@` resolves to `./src`

### How Frontend Unit Tests Work

1. **Pure Domain Logic (`src/lib/kanban.test.ts`)**:
   - Imports pure functions such as `moveCard()` directly from `@/lib/kanban`.
   - Passes synthetic `Column[]` fixtures and asserts that array transformations (reordering cards within the same column, moving a card to a specific position in another column, or dropping a card onto a column container) return the expected state without mutating inputs.

2. **Component & Interaction Tests (`src/components/KanbanBoard.test.tsx`)**:
   - Renders React client components into a virtual `jsdom` document using `render(<KanbanBoard />)`.
   - Queries elements using accessible roles, labels, placeholders, and `data-testid` attributes (`screen.getAllByTestId(/column-/i)` and `within(column)`).
   - Simulates real user interactions asynchronously via `userEvent` (`userEvent.click`, `userEvent.clear`, `userEvent.type`) and asserts the resulting DOM updates (e.g., column input value changes, newly added card appears in the column, removed card disappears from the DOM).
   - When backend API calls are introduced (Parts 7 and 10), `global.fetch` is mocked in unit tests so component state transitions can be tested deterministically without a running server.

### Running Frontend Unit Tests

```bash
cd frontend
npm run test:unit        # Run all unit tests once
npm run test:unit:watch  # Run Vitest in interactive watch mode
```

---

## Backend Unit Tests (`backend/`)

### Stack & Configuration

- **Test Runner**: `pytest` (managed via `uv` in `backend/pyproject.toml`)
- **HTTP Client**: FastAPI `TestClient` (powered by `httpx`)
- **File Pattern**: `backend/tests/test_*.py`

### How Backend Unit Tests Work

1. **Isolated Database Fixtures**:
   - Each test uses `pytest`'s `tmp_path` fixture and `monkeypatch` to point `DATABASE_PATH` to a fresh temporary SQLite file.
   - Verifies that the database file, schema tables (`users`, `boards`), and initial seed data (`user` / `password` and default 5-column Kanban board) are created automatically.

2. **API Route Testing**:
   - Uses `TestClient(app)` to issue synchronous HTTP requests (`GET /api/health`, `POST /api/auth/login`, `GET /api/kanban`, `PUT /api/kanban`, `POST /api/chat`) in-process without binding a network port.
   - Validates status codes (`200`, `401`, `422`), Pydantic response schemas, and SQLite state persistence across sequential calls.

3. **AI Service Testing**:
   - Unit tests mock the `google-genai` client to verify prompt construction, Structured Outputs parsing (`AIChatResponse`), and conditional database updates when `board` is present vs. `None`.

### Running Backend Unit Tests

```bash
cd backend
uv run pytest
```

