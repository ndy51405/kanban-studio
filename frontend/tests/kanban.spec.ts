import { expect, test, type Page } from "@playwright/test";

async function loginAsDemoUser(page: Page) {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
}

test.describe("Authentication Flow", () => {
  test("shows login screen when visiting unauthenticated", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await expect(page.getByLabel("Username")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
  });

  test("rejects invalid credentials with an error message", async ({ page }) => {
    await page.goto("/");
    await page.getByLabel("Username").fill("invalid_user");
    await page.getByLabel("Password").fill("wrong_password");
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page.getByText(/invalid username or password/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).not.toBeVisible();
  });

  test("signs in successfully, persists across reload, and logs out", async ({ page }) => {
    await loginAsDemoUser(page);

    // Verify 5 columns are rendered
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);

    // Reload page to verify session persistence
    await page.reload();
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);

    // Log out
    await page.getByRole("button", { name: /log out/i }).click();
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).not.toBeVisible();
  });
});

const defaultBoardData = {
  columns: [
    { id: "col-backlog", title: "Backlog", cardIds: ["card-1", "card-2"] },
    { id: "col-discovery", title: "Discovery", cardIds: ["card-3"] },
    { id: "col-progress", title: "In Progress", cardIds: ["card-4", "card-5"] },
    { id: "col-review", title: "Review", cardIds: ["card-6"] },
    { id: "col-done", title: "Done", cardIds: ["card-7", "card-8"] },
  ],
  cards: {
    "card-1": {
      id: "card-1",
      title: "Align roadmap themes",
      details: "Draft quarterly themes with impact statements and metrics.",
    },
    "card-2": {
      id: "card-2",
      title: "Gather customer signals",
      details: "Review support tags, sales notes, and churn feedback.",
    },
    "card-3": {
      id: "card-3",
      title: "Prototype analytics view",
      details: "Sketch initial dashboard layout and key drill-downs.",
    },
    "card-4": {
      id: "card-4",
      title: "Refine status language",
      details: "Standardize column labels and tone across the board.",
    },
    "card-5": {
      id: "card-5",
      title: "Design card layout",
      details: "Add hierarchy and spacing for scanning dense lists.",
    },
    "card-6": {
      id: "card-6",
      title: "QA micro-interactions",
      details: "Verify hover, focus, and loading states.",
    },
    "card-7": {
      id: "card-7",
      title: "Ship marketing page",
      details: "Final copy approved and asset pack delivered.",
    },
    "card-8": {
      id: "card-8",
      title: "Close onboarding sprint",
      details: "Document release notes and share internally.",
    },
  },
};

test.describe("Kanban Board Operations", () => {
  test.beforeEach(async ({ page, request }) => {
    await request.put("/api/kanban", { data: defaultBoardData });
    await loginAsDemoUser(page);
  });

  test("renames a column", async ({ page }) => {
    const column = page.getByTestId("column-col-backlog");
    await column.getByLabel("Column title").fill("Ideas");
    await expect(column.getByLabel("Column title")).toHaveValue("Ideas");
  });

  test("adds, edits and deletes a card", async ({ page }) => {
    const firstColumn = page.locator('[data-testid^="column-"]').first();
    await firstColumn.getByRole("button", { name: /add a card/i }).click();
    await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
    await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
    await firstColumn.getByRole("button", { name: /add card/i }).click();
    await expect(firstColumn.getByText("Playwright card")).toBeVisible();

    await firstColumn
      .getByRole("button", { name: "Edit Playwright card", exact: true })
      .click();
    await firstColumn.getByLabel("Edit card title").fill("Edited card");
    await firstColumn.getByLabel("Edit card details").fill("Edited via e2e.");
    await firstColumn.getByRole("button", { name: "Save" }).click();
    await expect(firstColumn.getByText("Edited card")).toBeVisible();
    await expect(firstColumn.getByText("Edited via e2e.")).toBeVisible();

    await firstColumn
      .getByRole("button", { name: "Delete Edited card", exact: true })
      .click();
    await expect(firstColumn.getByText("Edited card")).toHaveCount(0);
  });

  test("moves a card between columns", async ({ page }) => {
    const card = page.getByTestId("card-card-1");
    const targetColumn = page.getByTestId("column-col-review");
    const cardBox = await card.boundingBox();
    const columnBox = await targetColumn.boundingBox();
    if (!cardBox || !columnBox) {
      throw new Error("Unable to resolve drag coordinates.");
    }

    await page.mouse.move(
      cardBox.x + cardBox.width / 2,
      cardBox.y + cardBox.height / 2
    );
    await page.mouse.down();
    await page.mouse.move(
      columnBox.x + columnBox.width / 2,
      columnBox.y + 120,
      { steps: 12 }
    );
    await page.mouse.up();
    await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
  });

  test("persists column renames, card additions, edits, and deletions across page reload", async ({
    page,
  }) => {
    // 1. Rename column
    const backlogCol = page.getByTestId("column-col-backlog");
    await backlogCol.getByLabel("Column title").fill("Sprint Backlog");

    // 2. Add card
    await backlogCol.getByRole("button", { name: /add a card/i }).click();
    await backlogCol.getByPlaceholder("Card title").fill("Persistent card");
    await backlogCol.getByPlaceholder("Details").fill("Verified after reload.");
    await backlogCol.getByRole("button", { name: /add card/i }).click();
    await expect(backlogCol.getByText("Persistent card")).toBeVisible();

    // 3. Edit card
    await backlogCol
      .getByRole("button", { name: "Edit Align roadmap themes", exact: true })
      .click();
    await backlogCol.getByLabel("Edit card title").fill("Updated Theme Card");
    await backlogCol.getByRole("button", { name: "Save" }).click();
    await expect(backlogCol.getByText("Updated Theme Card")).toBeVisible();

    // 4. Delete card
    await backlogCol
      .getByRole("button", { name: "Delete Gather customer signals", exact: true })
      .click();
    await expect(backlogCol.getByText("Gather customer signals")).toHaveCount(0);

    // Wait a brief moment for PUT to complete then reload
    await page.waitForTimeout(500);
    await page.reload();

    // Verify all changes persisted from backend SQLite
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
    const reloadedCol = page.getByTestId("column-col-backlog");
    await expect(reloadedCol.getByLabel("Column title")).toHaveValue("Sprint Backlog");
    await expect(reloadedCol.getByText("Persistent card")).toBeVisible();
    await expect(reloadedCol.getByText("Updated Theme Card")).toBeVisible();
    await expect(reloadedCol.getByText("Gather customer signals")).toHaveCount(0);
  });
});
