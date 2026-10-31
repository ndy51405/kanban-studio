import { expect, test } from "@playwright/test";

test("loads the kanban board", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("renames a column", async ({ page }) => {
  await page.goto("/");
  const column = page.getByTestId("column-col-backlog");
  await column.getByLabel("Column title").fill("Ideas");
  await expect(column.getByLabel("Column title")).toHaveValue("Ideas");
});

test("adds, edits and deletes a card", async ({ page }) => {
  await page.goto("/");
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
  await page.goto("/");
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
