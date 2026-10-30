# End-to-End (E2E) Testing Guide

## Overview

End-to-End (E2E) tests validate the complete application in a real headless Chromium browser using **Playwright**. Unlike unit tests (`jsdom`), E2E tests verify actual browser rendering, CSS layout/bounding boxes, pointer drag-and-drop physics, network requests, and full-stack persistence.

---

## Stack & Configuration (`frontend/playwright.config.ts`)

- **Framework**: `@playwright/test`
- **Test Directory**: `frontend/tests/` (`*.spec.ts`)
- **Browser Project**: Desktop Chrome (`chromium`)
- **Base URL**: `http://127.0.0.1:3000` during standalone frontend development (or `http://127.0.0.1:8000` when testing against the unified FastAPI + static Next.js Docker container)
- **Web Server Hook**: Playwright automatically starts the dev server (`npm run dev -- --hostname 127.0.0.1 --port 3000`) if a server is not already listening on the target URL (`reuseExistingServer: true`), and retains execution traces on failure (`trace: "retain-on-failure"`).

---

## How E2E Tests Work (`frontend/tests/kanban.spec.ts`)

1. **Page Navigation & Initial Render**:
   - Each test receives an isolated browser `page` context and navigates to `await page.goto("/")`.
   - Asserts that key headings (`getByRole("heading", { name: "Kanban Studio" })`) and all 5 columns (`page.locator('[data-testid^="column-"]')`) are visible in the viewport.

2. **Form & Card Workflows**:
   - Scopes locators to a specific column (`page.locator('[data-testid^="column-"]').first()`).
   - Clicks buttons and fills inputs (`getByPlaceholder("Card title").fill(...)`) just as a user would, asserting that newly created or edited cards become visible in the DOM.

3. **Real Pointer Drag-and-Drop**:
   - Because `@dnd-kit` relies on pointer sensors (`PointerSensor` with a 6px activation distance) and layout geometry, drag-and-drop is tested in Playwright using real bounding-box coordinates:
     1. Resolves `card.boundingBox()` for the source card (`data-testid="card-card-1"`) and `targetColumn.boundingBox()` for the destination column (`data-testid="column-col-review"`).
     2. Moves the mouse to the center of the source card (`page.mouse.move`) and presses the button down (`page.mouse.down`).
     3. Moves the mouse smoothly across multiple steps (`{ steps: 12 }`) into the target column to exceed the drag activation threshold and trigger collision detection.
     4. Releases the mouse (`page.mouse.up`) and asserts the card now resides inside `targetColumn`.

4. **Full-Stack Flows (Parts 4, 7, and 10)**:
   - **Authentication (Part 4)**: Verifies that visiting `/` displays the sign-in screen, signing in with `user` / `password` reveals the Kanban board, and logging out returns to the sign-in screen.
   - **Database Persistence (Part 7)**: Performs board mutations, executes `await page.reload()`, and verifies that changes persist from the SQLite backend.
   - **AI Chat Sidebar (Part 10)**: Sends a natural-language instruction in the chat sidebar and verifies that both the assistant reply appears and the Kanban board updates automatically.

---

## Running E2E Tests

```bash
cd frontend
npm run test:e2e   # Run Playwright E2E suite in headless Chromium
npm run test:all   # Run Vitest unit tests followed by Playwright E2E tests
```

