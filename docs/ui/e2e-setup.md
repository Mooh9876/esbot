# E2E Test Setup – ESBot

**Exercise:** 11.2 – Automated E2E Tests

---

## Framework

**Playwright** (JavaScript) was chosen for the following reasons:

- The frontend is already written in JavaScript/React – no additional language
- Playwright provides `page.getByTestId()`, which directly matches the `data-testid` selectors already present in `App.jsx`
- Playwright has built-in auto-waiting for asynchronous UI interactions – no `sleep()` calls needed
- (Playwright runs on Windows 11 with Chromium)

---

## Installation

All commands are run from the `frontend/` directory.

```powershell
# 1. Install Playwright as a dev dependency (already added to package.json)
npm install

# 2. Install the Chromium browser used by the tests
npx playwright install chromium
```

---

## Starting the Application

The E2E tests require both the backend and the frontend to be running before executing the tests.

**Terminal 1 – Backend** (run from `backend/`):
```powershell
uv run uvicorn app.main:app --reload
```

**Terminal 2 – Frontend** (run from `frontend/`):
```powershell
npm run dev
```

---

## Running the Tests

Run from the `frontend/` directory:

```powershell
npm run test:e2e:playwright
```

This executes all tests in `playwright/esbot.spec.js` using Chromium in headless mode.

---

## Test Cases

| Test ID | BDD Source | Description | Type |
|---------|-----------|-------------|------|
| TC-E2E-01 | `ask_question.feature` – Happy Path | Create session, send message, verify assistant reply | Positive |
| TC-E2E-02 | `quiz_generation.feature` – Happy Path | Create session, generate quiz, verify question appears | Positive |
| TC-E2E-03 | `ask_question.feature` – Error Path | Send empty message, verify error banner, no chat entry | Negative |

---

## Test Structure

```
frontend/
├── playwright/
│   └── esbot.spec.js       # All three E2E tests
├── playwright.config.js    # Playwright configuration
└── package.json            # test:e2e:playwright script added
```

---

## LLM Mock Used

The backend uses the `StubAIProvider` (defined in `backend/app/ai_stubs.py`), which returns deterministic, hard-coded responses:

- **Chat:** Always returns `"Unit tests verify individual components in isolation"`
- **Quiz:** Always returns the question `"What does TDD stand for?"`

The E2E tests assert that replies are non-empty and contain the known stub prefix – not the exact full text – as recommended by the assignment guidance.

---

## Selectors

All test selectors use `data-testid` attributes exclusively. These attributes are already present in `frontend/src/App.jsx` and were not modified for the tests:

| `data-testid` | Element |
|--------------|---------|
| `health-status` | Backend status indicator |
| `new-session-btn` | "New session" button |
| `session-list` | Session list container |
| `message-input` | Message textarea |
| `send-message-btn` | "Send message" button |
| `assistant-message` | Bot reply in chat |
| `error-banner` | Error message display |
| `quiz-topic-input` | Quiz topic input field |
| `generate-quiz-btn` | "Generate quiz" button |
| `quiz-question` | Displayed quiz question |
