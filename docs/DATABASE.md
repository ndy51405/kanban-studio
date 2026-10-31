# Database Architecture & Modeling

## Overview

The application uses local SQLite as its persistence layer. The database file is located on the host at `./data/pm.db` and bind-mounted to `/app/data/pm.db` inside the Docker container.

The database supports multiple users while scoping each user to a single Kanban board for the MVP. The board state is stored as a validated JSON document matching the frontend `BoardData` structure, enabling atomic updates from drag-and-drop operations and Gemini AI structured outputs.

---

## Configuration

- **Default Location**: `data/pm.db` (relative to project root)
- **Environment Variable**: `DATABASE_PATH` (defaults to `data/pm.db` locally or `/app/data/pm.db` in Docker)
- **Pragmas**:
  - `PRAGMA foreign_keys = ON;` (enforces relational integrity)
  - `PRAGMA journal_mode = WAL;` (write-ahead logging for safe concurrent reads/writes)

---

## Schema Definition

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    board_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_boards_user_id ON boards(user_id);
```

### Table Descriptions

1. **`users`**:
   - `id`: Internal integer primary key.
   - `username`: Unique username (for MVP, default is `"user"`).
   - `password_hash`: Secure SHA-256 password hash with salt.
   - `created_at`: ISO 8601 UTC timestamp string.

2. **`boards`**:
   - `id`: Internal integer primary key.
   - `user_id`: Foreign key referencing `users.id` with a `UNIQUE` constraint (enforces 1 board per user for the MVP while supporting multiple users).
   - `board_json`: Serialized JSON payload containing the columns and cards.
   - `updated_at`: ISO 8601 UTC timestamp string of the last board mutation.

---

## Board JSON Structure

The `board_json` column stores serialized JSON strictly adhering to the frontend `BoardData` TypeScript model and Pydantic validation schema:

```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-discovery",
      "title": "Discovery",
      "cardIds": ["card-3"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-6"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-7", "card-8"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    },
    "card-2": {
      "id": "card-2",
      "title": "Gather customer signals",
      "details": "Review support tags, sales notes, and churn feedback."
    },
    "card-3": {
      "id": "card-3",
      "title": "Prototype analytics view",
      "details": "Sketch initial dashboard layout and key drill-downs."
    },
    "card-4": {
      "id": "card-4",
      "title": "Refine status language",
      "details": "Standardize column labels and tone across the board."
    },
    "card-5": {
      "id": "card-5",
      "title": "Design card layout",
      "details": "Add hierarchy and spacing for scanning dense lists."
    },
    "card-6": {
      "id": "card-6",
      "title": "QA micro-interactions",
      "details": "Verify hover, focus, and loading states."
    },
    "card-7": {
      "id": "card-7",
      "title": "Ship marketing page",
      "details": "Final copy approved and asset pack delivered."
    },
    "card-8": {
      "id": "card-8",
      "title": "Close onboarding sprint",
      "details": "Document release notes and share internally."
    }
  }
}
```

---

## Automatic Initialization & Seeding

On application startup, the database layer executes the following procedure:

1. **Directory Verification**: Verifies and creates the parent folder of `DATABASE_PATH` if missing.
2. **Table Creation**: Executes `CREATE TABLE IF NOT EXISTS` for `users` and `boards`.
3. **Default User Seeding**:
   - Queries `users` for `username = "user"`.
   - If not found, creates the user with password `"password"`.
4. **Default Board Seeding**:
   - Queries `boards` for the seeded user.
   - If no board exists for this user, seeds a new row containing the default 5-column, 8-card `initialData` JSON.

---

## Future Extensibility

- **Multiple Boards Per User**: The `UNIQUE` constraint on `boards.user_id` can be dropped, and a `name` column added to allow users to own multiple boards.
- **Relational Card Storage**: If fine-grained card-level querying is required later, the JSON payload can be migrated to dedicated `cards` and `columns` relational tables without breaking the high-level API.

