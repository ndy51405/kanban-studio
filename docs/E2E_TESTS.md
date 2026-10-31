# 端對端 (E2E) 測試指南

## 概述

端對端 (E2E) 測試使用 **Playwright** 在真實的無頭 Chromium 瀏覽器中驗證完整應用程式。與單元測試 (`jsdom`) 不同，E2E 測試會驗證實際的瀏覽器渲染、CSS 版面與邊界框、指標拖放行為、網路請求，以及全端資料持久化。

---

## 技術堆疊與設定 (`frontend/playwright.config.ts`)

- **框架**：`@playwright/test`
- **測試目錄**：`frontend/tests/` (`*.spec.ts`)
- **瀏覽器專案**：Desktop Chrome (`chromium`)
- **Base URL**：`http://127.0.0.1:8000` (由 FastAPI 提供靜態匯出的 Next.js 應用程式)
- **Web Server 掛鉤**：若 8000 埠上尚無伺服器 (例如 Docker 容器) 在監聽，Playwright 會先執行 `npm run build`，再以 `uv run uvicorn app.main:app` 啟動後端 (`reuseExistingServer: true`)，並在失敗時保留執行追蹤 (`trace: "retain-on-failure"`)。

---

## E2E 測試如何運作 (`frontend/tests/kanban.spec.ts`)

1. **頁面導覽與初始渲染**：
   - 每個測試取得獨立的瀏覽器 `page` 環境，並執行 `await page.goto("/")`。
   - 斷言關鍵標題 (`getByRole("heading", { name: "Kanban Studio" })`) 與全部 5 個欄位 (`page.locator('[data-testid^="column-"]')`) 都顯示在視窗中。

2. **表單與卡片流程**：
   - 將定位器限定在特定欄位 (`page.locator('[data-testid^="column-"]').first()`)。
   - 如同使用者一般點擊按鈕並填寫輸入框 (`getByPlaceholder("Card title").fill(...)`)，並斷言新建立或編輯後的卡片會顯示在 DOM 中。

3. **真實指標拖放**：
   - 由於 `@dnd-kit` 依賴指標感測器 (`PointerSensor`，啟動距離 6px) 與版面幾何，Playwright 以真實的邊界框座標測試拖放：
     1. 取得來源卡片 (`data-testid="card-card-1"`) 的 `card.boundingBox()` 與目標欄位 (`data-testid="column-col-review"`) 的 `targetColumn.boundingBox()`。
     2. 將滑鼠移到來源卡片中心 (`page.mouse.move`) 並按下按鍵 (`page.mouse.down`)。
     3. 分多個步驟 (`{ steps: 12 }`) 平滑地將滑鼠移入目標欄位，以超過拖曳啟動門檻並觸發碰撞偵測。
     4. 放開滑鼠 (`page.mouse.up`)，並斷言卡片現在位於 `targetColumn` 內。

4. **全端流程 (第 4、7、10 部分)**：
   - **身分驗證 (第 4 部分)**：驗證造訪 `/` 會顯示登入畫面，以 `user` / `password` 登入後會顯示看板，登出後會回到登入畫面。
   - **資料庫持久化 (第 7 部分)**：對看板進行變更後執行 `await page.reload()`，驗證變更已由 SQLite 後端保存。
   - **AI 聊天側邊欄 (第 10 部分)**：在聊天側邊欄送出自然語言指令，驗證助理回覆出現且看板自動更新。

---

## 執行 E2E 測試

```bash
cd frontend
npm run test:e2e   # 在無頭 Chromium 中執行 Playwright E2E 測試
npm run test:all   # 先執行 Vitest 單元測試，再執行 Playwright E2E 測試
```
