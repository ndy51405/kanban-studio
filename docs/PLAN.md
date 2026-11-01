# Project Management MVP - Implementation Plan

## Architectural & Design Decisions

- **Frontend**: Next.js 16 (App Router) exported as static assets (`output: "export"`) and served by FastAPI at `/`.
- **Backend**: Python FastAPI managed with `uv`, serving `/api/*` endpoints and static frontend files.
- **Packaging**: Single multi-stage `Dockerfile` (Node build stage for Next.js static export + Python `uv` runtime stage for FastAPI).
- **Database**: Local SQLite database persisted to `./data/pm.db` on the host via a Docker bind mount; automatically created and seeded on startup if missing.
- **Authentication**: Hardcoded credentials (`user` / `password`) for MVP; starts as client-side state in Part 4 and connects to backend auth + user-scoped board endpoints in Parts 6-7, backed by a multi-user database table.
- **AI Chat**: Google Gemini API (`GEMINI_API_KEY` from `.env` using the `google-genai` SDK) with Structured Outputs to return a conversational response and an optional full Kanban board update. Conversation history is kept in frontend session state (resets on reload) and sent with each request.

---

## Part 1: Plan

Enrich this document to plan out each part in detail with checklists, tests, and success criteria, and document the existing frontend code in `frontend/AGENTS.md`.

### Checklist
- [x] Review root `AGENTS.md`, existing `docs/PLAN.md`, and the `frontend/` codebase
- [x] Clarify open design questions with the user (auth flow, SQLite volume persistence, chat history scope)
- [x] Create `frontend/AGENTS.md` documenting existing frontend architecture, components, types, and test commands
- [x] Enrich `docs/PLAN.md` with detailed checklists, test plans, and success criteria for Parts 1-10
- [x] Obtain user review and approval of the plan

### Tests & Success Criteria
- `frontend/AGENTS.md` exists and accurately describes the `frontend/` codebase.
- `docs/PLAN.md` covers Parts 1-10 with actionable checklists, test strategies, and clear success criteria.
- User explicitly approves the plan before Part 2 begins.

---

## Part 2: Scaffolding

Set up the Docker infrastructure, the FastAPI backend in `backend/`, and start/stop scripts in `scripts/`. Serve example static HTML at `/` that also makes an API call to the backend to confirm end-to-end local container execution.

### Checklist
- [x] Create `backend/pyproject.toml` configured for `uv` with `fastapi`, `uvicorn[standard]`, `pydantic`, `httpx`, and `pytest`
- [x] Create `backend/app/main.py` with:
  - `GET /api/health` returning `{"status": "ok", "message": "Hello from FastAPI"}`
  - Static file mounting at `/` serving a placeholder `backend/static/index.html` that fetches `/api/health` and displays the response
- [x] Create `Dockerfile` using `uv` to install Python dependencies and run `uvicorn` on port `8000`
- [x] Create `docker-compose.yml` (or standardized `docker run` flags in scripts) passing `.env` and mounting `./data:/app/data`
- [x] Create `scripts/start.sh` and `scripts/stop.sh` (Mac/Linux) and `scripts/start.ps1` and `scripts/stop.ps1` ( plus `scripts/start.bat` / `scripts/stop.bat` if helpful on Windows)
- [x] Write backend unit tests in `backend/tests/test_health.py`

### Tests & Success Criteria
- **Backend Unit Tests**: `pytest` verifies `GET /api/health` returns HTTP 200 with expected JSON and `GET /` returns HTML.
- **Container Smoke Test**: Starting the container via the start script serves the hello-world page at `http://localhost:8000`, and the page successfully fetches `/api/health`. Stopping via the stop script cleanly terminates the container.

---

## Part 3: Add in Frontend

Configure the Next.js frontend to build statically and be served by FastAPI at `/` inside the Docker container, and ensure card editing is supported alongside moving, adding, and deleting cards and renaming columns.

### Checklist
- [x] Update `frontend/next.config.ts` with `output: "export"` so `npm run build` outputs static assets to `frontend/out`
- [x] Add inline card editing support in `KanbanCard.tsx` and `KanbanBoard.tsx` (allowing card `title` and `details` to be edited, matching the business requirement that cards can be moved and edited)
- [x] Update `Dockerfile` to a multi-stage build:
  - Stage 1 (`node:22-alpine`): `npm ci && npm run build` in `frontend/`
  - Stage 2 (`python:3.12-slim` + `uv`): copy `frontend/out` into `/app/static` and serve at `/` via FastAPI `StaticFiles(html=True)`
- [x] Add unit tests for card editing in `frontend/src/components/KanbanBoard.test.tsx`
- [x] Add backend integration tests verifying `/` serves the built Next.js Kanban application
- [x] Update/run Playwright E2E tests against the served app (verified passing locally)

### Tests & Success Criteria
- **Frontend Unit Tests**: `npm run test:unit` passes all existing tests plus card-editing tests.
- **Backend Integration Tests**: `pytest` confirms `GET /` serves the compiled Next.js HTML containing "Kanban Studio".
- **E2E Tests**: Playwright verifies loading `/`, renaming a column, adding, editing, deleting, and dragging a card across columns.

---

## Part 4: Add in a Fake User Sign-In Experience

Gate the Kanban board behind a login screen at `/` requiring username `"user"` and password `"password"`, and provide a logout action.

### Checklist
- [x] Create `frontend/src/components/LoginForm.tsx` styled with the project color palette (`#032147` navy headings, `#753991` purple submit button, `#209dd7` blue accents)
- [x] Manage authentication state in the frontend (persisted in `sessionStorage`/`localStorage` so page refreshes during a session stay signed in until logout)
- [x] Reject invalid credentials with a clear error message; accept `"user"` / `"password"`
- [x] Add a "Log out" button in the `KanbanBoard` header that clears auth state and returns to the login view
- [x] Update existing unit and Playwright E2E tests to account for login, and add dedicated auth tests

### Tests & Success Criteria
- **Frontend Unit Tests**: Verify unauthenticated users see the login form, invalid credentials show an error, valid credentials (`user` / `password`) render the Kanban board, and clicking "Log out" returns to the login form.
- **E2E Tests**: Playwright tests verify the full sign-in, Kanban interaction, and sign-out flow at `/`.

---

## Part 5: Database Modeling

Design the SQLite schema supporting multiple users and storing each user's Kanban board as JSON. Document the approach in `docs/DATABASE.md` and get user sign-off.

### Checklist
- [x] Draft `docs/DATABASE.md` defining:
  - Database file location (`data/pm.db`, configurable via `DATABASE_PATH` env var)
  - `users` table (`id INTEGER PRIMARY KEY AUTOINCREMENT`, `username TEXT UNIQUE NOT NULL`, `password_hash TEXT NOT NULL`, `created_at TEXT NOT NULL`)
  - `boards` table (`id INTEGER PRIMARY KEY AUTOINCREMENT`, `user_id INTEGER NOT NULL UNIQUE REFERENCES users(id)`, `board_json TEXT NOT NULL`, `updated_at TEXT NOT NULL`)
  - JSON structure for `board_json` matching frontend `BoardData` (`columns: Column[]`, `cards: Record<string, Card>`)
  - Auto-initialization and default user/board seeding strategy on startup
- [x] Request user review and sign-off on `docs/DATABASE.md` before starting Part 6

### Tests & Success Criteria
- `docs/DATABASE.md` is clear, minimal, and covers schema, JSON validation model, and seeding behavior.
- User approves the database design before Part 6 begins.

---

## Part 6: Backend

Implement SQLite database creation, seeding, authentication, and Kanban CRUD API routes in FastAPI with comprehensive backend unit tests.

### Checklist
- [x] Create `backend/app/schemas.py` with Pydantic models for `Card`, `Column`, `BoardData`, and `LoginRequest` / `LoginResponse`
- [x] Create `backend/app/db.py` using Python's built-in `sqlite3`:
  - Automatically create parent directory and tables (`users`, `boards`) if `pm.db` does not exist
  - Seed default user (`username="user"`, `password="password"`) and default `initialData` Kanban JSON if not present
  - Helper functions to verify user credentials, fetch `BoardData` for a username, and update `BoardData` for a username
- [x] Add FastAPI routes in `backend/app/main.py`:
  - `POST /api/auth/login`: validate credentials against `users` table and return user info
  - `GET /api/kanban`: return the user's `BoardData` JSON (defaulting to or scoped by authenticated user)
  - `PUT /api/kanban`: validate and persist updated `BoardData` JSON for the user
- [x] Write comprehensive backend unit tests in `backend/tests/test_kanban_api.py` using an isolated temporary SQLite database fixture

### Tests & Success Criteria
- **Backend Unit Tests**: `pytest` verifies:
  - Automatic database file and table creation when starting with an empty path
  - Default user and initial 5-column, 8-card board seeding
  - `POST /api/auth/login` succeeds for `user`/`password` and returns 401 for wrong credentials
  - `GET /api/kanban` returns valid `BoardData`
  - `PUT /api/kanban` persists column renames, card additions, edits, moves, and deletions across subsequent `GET /api/kanban` calls
  - Invalid payload shapes are rejected with HTTP 422

---

## Part 7: Frontend + Backend

Connect the frontend authentication and Kanban board state to the FastAPI backend so all changes persist in SQLite.

### Checklist
- [x] Create `frontend/src/lib/api.ts` with typed client functions for `POST /api/auth/login`, `GET /api/kanban`, and `PUT /api/kanban`
- [x] Update `LoginForm` / auth flow to authenticate via `POST /api/auth/login`
- [x] Update `KanbanBoard.tsx` to load initial board data from `GET /api/kanban` on mount and persist board mutations (column rename, card add, card edit, card delete, drag-and-drop move) via `PUT /api/kanban`
- [x] Add loading and error handling states without cluttering the UI
- [x] Update frontend unit tests (mocking `fetch`) and E2E tests (verifying persistence across page reloads)

### Tests & Success Criteria
- **Frontend Unit Tests**: Verify board loads from API and every mutation triggers `PUT /api/kanban` with updated `BoardData`.
- **Full-Stack E2E Tests**: Sign in, rename a column, add/edit/move/delete a card, reload the browser page, and verify all changes remain persisted from SQLite.

---

## Part 8: AI Connectivity

Enable the backend to call Google Gemini using `GEMINI_API_KEY` from `.env` and verify connectivity with a simple `"2+2"` test.

### Checklist
- [x] Add `google-genai` and `python-dotenv` to `backend/pyproject.toml`
- [x] Configure model selection (`gemini-3.1-flash-lite` by default, configurable via `GEMINI_MODEL` env var) and load `GEMINI_API_KEY` from `.env`
- [x] Create `backend/app/ai.py` with a simple completion function
- [x] Add unit tests (with mocked Gemini client response) and a live connectivity test sending `"What is 2+2? Reply with just the number."` and asserting `"4"` in the response

### Tests & Success Criteria
- **Backend Unit Tests**: Fast unit test with mocked client verifies request formatting and error handling.
- **Live Connectivity Test**: Running the Gemini connectivity check with `.env` loaded returns `"4"` for `"2+2"`.

---

## Part 9: Structured Outputs for AI Kanban Updates

Extend the backend AI integration so each chat request sends the user's question, conversation history, and current Kanban JSON, and receives a Structured Output containing the assistant reply and an optional updated Kanban board.

### Checklist
- [ ] Define Pydantic schema `AIChatRequest` (`message: str`, `history: list[ChatMessage]`) and `AIChatResponse` (`reply: str`, `board: BoardData | None = None`) in `backend/app/schemas.py`
- [ ] Configure `backend/app/ai.py` to pass a system prompt instructing the model how to inspect and modify the user's `BoardData` (creating, editing, moving, deleting cards or renaming columns while preserving existing IDs unless creating new cards) and enforce Structured Outputs (`response_mime_type="application/json"`, `response_schema=AIChatResponse`)
- [ ] Implement `POST /api/chat` in `backend/app/main.py`:
  - Load current user's `BoardData` from SQLite
  - Call Gemini with current `BoardData`, `history`, and `message`
  - If the structured response includes an updated `board`, validate and save it to SQLite
  - Return `AIChatResponse` (`reply` and updated `board` if modified)
- [ ] Write backend unit and integration tests covering conversational-only replies (`board: null`) and board-mutating replies (creating/editing/moving cards)

### Tests & Success Criteria
- **Backend Unit Tests**: Verify `POST /api/chat` leaves the DB unchanged when `board` is `None`, and updates SQLite + returns the new `board` when the AI outputs board modifications.
- **Live AI Integration Test**: Prompting the endpoint to e.g. "Add a card titled 'Launch MVP' to Backlog" returns a confirmation `reply` and an updated `board` containing the new card in `col-backlog`, persisted in SQLite.

---

## Part 10: AI Chat Sidebar UI

Add a sidebar widget to the frontend supporting full AI chat and automatically refreshing the Kanban board whenever the AI updates it.

### Checklist
- [ ] Create `frontend/src/components/ChatSidebar.tsx` styled with the project palette (`#032147` header, `#753991` send button, `#209dd7` user bubble/accents, `#ecad0a` highlights)
- [ ] Integrate `ChatSidebar` alongside `KanbanBoard` in a responsive layout (toggleable or docked sidebar)
- [ ] Maintain conversation history in frontend state for the active session and send `message` + `history` to `POST /api/chat`
- [ ] Display loading indicator while waiting for the AI response
- [ ] When `AIChatResponse.board` is non-null, immediately update the `KanbanBoard` state in the UI
- [ ] Write unit tests for `ChatSidebar` and full E2E tests verifying that asking the AI to create/edit/move a card updates the visible Kanban board automatically

### Tests & Success Criteria
- **Frontend Unit Tests**: Verify sending a chat message renders user and assistant messages, passes conversation history, and updates the Kanban board when `board` is returned in the response.
- **Full-Stack E2E Tests**: User signs in, opens/uses the AI chat sidebar to request creating or moving a card, sees the assistant's reply in the sidebar, and sees the Kanban board immediately reflect the change.
