import { test, expect } from '@playwright/test'

/**
 * ESBot E2E Test Suite – Exercise 11.2
 *
 * Maps directly to the existing BDD scenarios in backend/features/.
 * All selectors use data-testid attributes exclusively, as required by the task.
 * The StubAIProvider is active on the backend – responses are deterministic.
 *
 * Prerequisites: backend on http://127.0.0.1:8000, frontend on http://127.0.0.1:5173
 */

// ---------------------------------------------------------------------------
// TC-E2E-01 – Create a session and send a message (Happy Path)
// BDD source: backend/features/ask_question.feature
// ---------------------------------------------------------------------------
test('TC-E2E-01: Create a session and send a message', async ({ page }) => {
  await page.goto('/')

  // 1. Verify the backend health indicator is shown
  const healthStatus = page.getByTestId('health-status')
  await expect(healthStatus).toBeVisible()
  await expect(healthStatus).toHaveText('Backend online')

  // 2. Create a new session
  await page.getByTestId('new-session-btn').click()

  // 3. Confirm the session appears in the session list
  const sessionList = page.getByTestId('session-list')
  await expect(sessionList.locator('button').first()).toBeVisible()

  // 4. Type and send a message
  const messageInput = page.getByTestId('message-input')
  await messageInput.fill('What is the difference between unit tests and integration tests?')
  await page.getByTestId('send-message-btn').click()

  // 5. Assert the assistant reply is visible and non-empty
  const assistantMessage = page.getByTestId('assistant-message')
  await expect(assistantMessage).toBeVisible()
  await expect(assistantMessage).not.toBeEmpty()
  await expect(assistantMessage).toContainText('Unit tests verify individual components in isolation')

  // 6. No error banner should be shown
  await expect(page.getByTestId('error-banner')).not.toBeVisible()
})

// ---------------------------------------------------------------------------
// TC-E2E-02 – Generate a quiz (Happy Path)
// BDD source: backend/features/quiz_generation.feature
// ---------------------------------------------------------------------------
test('TC-E2E-02: Generate a quiz for a topic', async ({ page }) => {
  await page.goto('/')

  // 1. Create a new session first
  await page.getByTestId('new-session-btn').click()

  // 2. Enter a quiz topic and generate
  await page.getByTestId('quiz-topic-input').fill('software testing')
  await page.getByTestId('generate-quiz-btn').click()

  // 3. A quiz question must appear
  const quizQuestion = page.getByTestId('quiz-question')
  await expect(quizQuestion).toBeVisible()
  await expect(quizQuestion).not.toBeEmpty()
  await expect(quizQuestion).toContainText('What does TDD stand for?')

  // 4. No error banner should be shown
  await expect(page.getByTestId('error-banner')).not.toBeVisible()
})

// ---------------------------------------------------------------------------
// TC-E2E-03 – Send an empty message (Error Scenario)
// BDD source: backend/features/ask_question.feature
// ---------------------------------------------------------------------------
test('TC-E2E-03: Empty message shows an error and does not send', async ({ page }) => {
  await page.goto('/')

  // 1. Create a session so the send button is active
  await page.getByTestId('new-session-btn').click()

  // 2. Leave the message input empty and click Send
  await page.getByTestId('message-input').fill('')
  await page.getByTestId('send-message-btn').click()

  // 3. An error banner must appear
  const errorBanner = page.getByTestId('error-banner')
  await expect(errorBanner).toBeVisible()
  await expect(errorBanner).toContainText('Message must not be empty')

  // 4. No assistant message must appear in the chat
  await expect(page.getByTestId('assistant-message')).not.toBeVisible()
})
