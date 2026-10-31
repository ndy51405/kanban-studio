# 單元測試指南

## 概述

單元測試用來快速驗證獨立的函式、元件與 API 路由，不需要真實瀏覽器或外部網路服務。本專案前端 (Next.js) 使用 **Vitest + React Testing Library**，後端 (Python) 使用 **pytest + FastAPI TestClient**。

---

## 前端單元測試 (`frontend/`)

### 技術堆疊與設定

- **測試執行器**：[Vitest](https://vitest.dev/) (`vitest.config.ts`)
- **DOM 環境**：`jsdom`
- **斷言與輔助工具**：`@testing-library/jest-dom` (透過 `src/test/setup.ts` 載入)、`@testing-library/react`、`@testing-library/user-event`
- **檔案規則**：`src/**/*.{test,spec}.{ts,tsx}` (排除 `tests/`，該目錄保留給 Playwright E2E 測試)
- **路徑別名**：`@` 對應 `./src`

### 前端單元測試如何運作

1. **純領域邏輯 (`src/lib/kanban.test.ts`)**：
   - 直接從 `@/lib/kanban` 匯入 `moveCard()` 等純函式。
   - 傳入模擬的 `Column[]` 資料，斷言陣列轉換結果符合預期 (同欄位內重新排序、移動卡片到另一欄的指定位置、將卡片拖放到欄位容器上)，且不會修改輸入資料。

2. **元件與互動測試 (`src/components/KanbanBoard.test.tsx`)**：
   - 使用 `render(<KanbanBoard />)` 將 React 用戶端元件渲染到虛擬的 `jsdom` 文件中。
   - 以可存取性角色 (role)、標籤、placeholder 與 `data-testid` 屬性查詢元素 (`screen.getAllByTestId(/column-/i)` 與 `within(column)`)。
   - 透過 `userEvent` (`userEvent.click`、`userEvent.clear`、`userEvent.type`) 非同步模擬真實使用者操作，並斷言 DOM 的更新結果 (例如欄位輸入框的值改變、新增的卡片出現在欄位中、刪除的卡片從 DOM 消失)。
   - 加入後端 API 呼叫後 (第 7 與第 10 部分)，單元測試會 mock `global.fetch`，讓元件狀態轉換可以在沒有伺服器的情況下穩定測試。

### 執行前端單元測試

```bash
cd frontend
npm run test:unit        # 執行一次所有單元測試
npm run test:unit:watch  # 以互動式監看模式執行 Vitest
```

---

## 後端單元測試 (`backend/`)

### 技術堆疊與設定

- **測試執行器**：`pytest` (透過 `backend/pyproject.toml` 以 `uv` 管理)
- **HTTP 用戶端**：FastAPI `TestClient` (底層為 `httpx`)
- **檔案規則**：`backend/tests/test_*.py`

### 後端單元測試如何運作

1. **隔離的資料庫 fixture**：
   - 每個測試使用 `pytest` 的 `tmp_path` fixture 與 `monkeypatch`，將 `DATABASE_PATH` 指向全新的暫存 SQLite 檔案。
   - 驗證資料庫檔案、資料表結構 (`users`、`boards`) 與初始種子資料 (`user` / `password` 以及預設的 5 欄看板) 會自動建立。

2. **API 路由測試**：
   - 使用 `TestClient(app)` 在行程內發送同步 HTTP 請求 (`GET /api/health`、`POST /api/auth/login`、`GET /api/kanban`、`PUT /api/kanban`、`POST /api/chat`)，不需綁定網路埠。
   - 驗證狀態碼 (`200`、`401`、`422`)、Pydantic 回應結構，以及連續呼叫之間 SQLite 狀態的持久化。

3. **AI 服務測試**：
   - 單元測試會 mock `google-genai` 用戶端，驗證提示詞的組成、結構化輸出 (`AIChatResponse`) 的解析，以及 `board` 存在與為 `None` 時資料庫的條件式更新。

### 執行後端單元測試

```bash
cd backend
uv run pytest
```
