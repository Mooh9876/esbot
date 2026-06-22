# Manual UI Test Report

**Exercise:** 11.1 – UI Setup and Manual Testing
**Date:** 22.06.2026
**Tester:** Mohammed

## Test Environment

* **Operating system:** macOS
* **Browser:** Safari
* **Frontend:** React with Vite
* **Frontend URL:** `http://127.0.0.1:5173`
* **Backend:** Python / FastAPI
* **Backend URL:** `http://127.0.0.1:8000`
* **Database:** Local SQLite database
* **LLM provider:** StubAIProvider / mock provider

Before starting the tests, I started the backend and checked the health endpoint. After opening the frontend in Safari, the UI showed the status “Backend online”.

---

## TC-UI-01 – Create a Session and Send a Message

### Preconditions

* Backend is running.
* Frontend is running and opened in Safari.
* The health status shows that the backend is online.

### Steps Performed

1. Opened the ESBot frontend in Safari.

2. Clicked the **New session** button.

3. Checked whether the new session appeared in the session list.

4. Selected the created session.

5. Entered the following message:

   `What is the difference between unit tests and integration tests?`

6. Clicked **Send message**.

7. Waited for the response from ESBot.

### Expected Result

* A new session is created and displayed in the session list.
* The entered user message is visible in the chat.
* A non-empty answer from ESBot is displayed.
* No error message is shown.

### Actual Result

A new session was created and appeared in the session list. The user message was shown in the chat. ESBot returned a visible answer: “Unit tests verify individual components in isolation”. No error message was displayed.

### Result

✅ Pass

### Evidence

`screenshots/tc-ui-01-chat-happy-path.png`

---

## TC-UI-02 – Send an Empty Message

### Preconditions

* Backend and frontend are running.
* A session is available and selected.

### Steps Performed

1. Opened an existing session.
2. Left the message input field empty.
3. Clicked **Send message**.

### Expected Result

* The application should not send an empty message.
* A clear error message should be displayed.
* No empty user message should appear in the chat.
* No assistant response should be created.

### Actual Result

The application displayed the error message “Message must not be empty.” No empty message was added to the chat and no assistant response was created.

### Result

✅ Pass

### Evidence

`screenshots/tc-ui-02-empty-message-error.png`

---

## Reflection

The manual UI tests were useful because I could check the application from the user’s point of view. It was easy to see whether the backend was reachable, whether the session was created, and whether the chat messages appeared correctly.

Manual testing took more time than API testing because every action had to be carried out in the browser. I also had to check the visible result after every step and make screenshots.

Automation could help by repeating the same user flows after each change. This would make it easier to find errors, for example when a button no longer works, the frontend cannot reach the backend, or messages are not displayed correctly.
