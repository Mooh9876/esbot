# Test Strategy for ESBot

## 1. Differences Between Unit Tests and BDD/Acceptance Tests

Unit tests and BDD (Behavior-Driven Development) acceptance tests serve different purposes and operate at different levels of the system.

### Unit Tests
- **Scope:** Very small (single functions, classes, or components)
- **Purpose:** Verify correctness of isolated logic
- **Execution Time:** Fast (milliseconds)
- **Dependencies:** Typically mocked or stubbed
- **Feedback:** Immediate and precise (helps pinpoint bugs quickly)

### BDD / Acceptance Tests
- **Scope:** Large (end-to-end behavior, user scenarios)
- **Purpose:** Validate that the system behaves according to business requirements
- **Execution Time:** Slower (seconds to minutes)
- **Dependencies:** Often involve multiple components working together
- **Feedback:** Higher-level (confirms features, not implementation details)

In short:

- Unit tests answer: **"Does the code work correctly?"**
- BDD tests answer: **"Does the system behave correctly from a user perspective?"**

---

## 2. When Should They Be Executed?

Running both test types together on every change is **not always optimal** due to differences in speed and purpose.

### Recommended Strategy for ESBot

### Unit Tests
- Run on **every commit / push**
- Run in **local development**
- Run in **every CI pipeline stage**
- Purpose: Fast feedback and early bug detection

### BDD / Acceptance Tests
- Run on:
  - **Pull Requests**
  - **Main branch merges**
  - **Scheduled CI runs (optional, e.g., nightly)**
- Not necessarily on every small commit to avoid slowing down development

### CI Pipeline Recommendation

A practical CI pipeline for ESBot could look like:

1. **Stage 1 – Fast Validation**
   - Run unit tests
   - Fail fast if something breaks

2. **Stage 2 – Acceptance Validation**
   - Run BDD/acceptance tests
   - Ensure user-level behavior is correct

This separation keeps the pipeline efficient while still maintaining high confidence in system behavior.

---

## 3. Impact of AI Mockability on Testing

A key factor in ESBot is the use of AI components. Normally, this introduces challenges such as:

- External API dependencies
- Network latency
- Non-deterministic responses
- Cost of API calls

### Why Mocking AI Is Important

By using **mock AI providers**, we can:

- Make responses **deterministic**
- Eliminate **network dependency**
- Reduce **execution time**
- Avoid **costs**

### Effect on Acceptance Tests

Because AI is mocked:

- BDD tests become **stable and reproducible**
- Tests can run **reliably in CI environments**
- No need for a live AI model during testing

### Conclusion on AI and CI

Without mocking, acceptance tests would be:

- Flaky
- Slow
- Unsuitable for CI

With mocking, acceptance tests:

- Become **CI-friendly**
- Can safely run in **automated pipelines**
- Provide **consistent validation of system behavior**

---

## 4. Final Recommendation

For ESBot:

- **Unit tests:** Run always (every commit, every pipeline)
- **BDD/acceptance tests:** Run in a **separate CI stage**, triggered on pull requests and merges
- **AI interactions:** Always use **mock providers in tests**

This approach balances:

- **Speed** (fast feedback for developers)
- **Reliability** (stable CI runs)
- **Confidence** (full system validation before integration)