# Review – Group 1 ESBot Repository

**Project / product:** ESBot (Group 1 – hse-st-group1)  
**Review object(s):** `docs/esbot.md`, `docs/spec/requirements.md`, `docs/spec/spec.md`, `docs/spec/data-model.md`, `application/backend/` (Java domain model, services, BDD tests)  
**Review type:** Technical Review  
**Date (planned / actual):** 2026-05-05 / 2026-05-05  
**Moderator:** Mohammed Al-otaibi  
**Author(s):** hse-st-group1  
**Reviewers:** Mohammed Al-otaibi

---

## 1. General Instructions

I used the technical review process from the course. I chose a technical review over a full inspection because the team is small and time was limited — a proper inspection with multiple formal phases would have been too much overhead here. The review also covered three different artefact types (docs, data model, code), so reading and comparing made more sense than a strict counting process.

No live meeting with Group 1 was possible since we're separate teams. Phases I completed: planning → individual preparation → written findings → this report.

---

## 2. Master Plan (MP)

### 2.1 Masterplan — Header

| Field | Value |
|-------|-------|
| Review No. | REV-2026-001 |
| Project | ESBot – Group 1 |
| Project manager | — |
| Quality expert / manager | — |
| Moderator | Mohammed Al-otaibi |
| Author(s) | hse-st-group1 (GitHub) |

### 2.2 Review Objects

| # | Review objects | Abbr. |
|---|----------------|-------|
| 1 | `docs/esbot.md` | EB |
| 2 | `docs/spec/requirements.md` | REQ |
| 3 | `docs/spec/spec.md` | SPEC |
| 4 | `docs/spec/data-model.md` | DM |
| 5 | `application/backend/src/main/java/hse_st_group1/esbot/` (model + services + controller) | CODE |
| 6 | `application/backend/src/test/resources/features/` (BDD feature files) | BDD |

### 2.3 Reference Documents

| # | Reference documents | Abbr. |
|---|---------------------|-------|
| 1 | `docs/esbot.md` (baseline ESBot case study description) | EB |
| 2 | `docs/spec/requirements.md` | REQ |
| 3 | `docs/spec/spec.md` (auto-generated spec) | SPEC |

### 2.4 Checklists / Scenarios

| # | Checklists / scenarios |
|---|------------------------|
| 1 | Requirements completeness: all FRs from `esbot.md` traceable to `requirements.md` and `spec.md` |
| 2 | Data model consistency: entities in `data-model.md` match Java model classes |
| 3 | Code–spec alignment: services and controller implement the FRs claimed in the spec |
| 4 | BDD scenario quality: scenarios test meaningful user-facing behaviour, not just stub wiring |
| 5 | REST API: at least the endpoints claimed in FRs 025–027 are present |

### 2.5 Reviewer Assignment

| Reviewer | Scope | Abbr. |
|----------|-------|-------|
| 1 | Mohammed Al-otaibi — REQ, SPEC, EB (completeness & consistency) | MA |
| 2 | [Team member 2] — DM, CODE (model vs data-model, services) | — |
| 3 | [Team member 3] — BDD, CODE (feature files, step definitions) | — |

### 2.6 Kick-off

| Date / time / location |
|------------------------|
| Async review; no live kick-off meeting held. Group 1's README and docs used as context material. |

### 2.7 Individual Preparation

| Individual preparation | Value | Unit |
|------------------------|-------|------|
| Submission of findings by | 2026-05-05 | — |
| Size of review objects | ~900 NLOC (Java) + ~12 pages docs | NLOC / pages |
| Optimal inspection rate | ~100–150 NLOC/h | NLOC/h |
| Optimal inspection time | ~1.5–2 h | h |

### 2.8 Review Meeting

| Date / time / location |
|------------------------|
| Async; findings consolidated and documented directly in this file. |

### 2.9 Additional Milestones

| Milestone | Planned date / time | Actual date / time |
|-----------|---------------------|--------------------|
| End of individual preparation | 2026-05-05 | 2026-05-05 |
| Rework deadline | — (Group 1 responsible) | — |
| Follow-up / closure | — | — |

---

## 3. List of Findings (LoF)

Severity scale: **blocking** > **major** > **minor** > **editorial**  
Types: **defect** (wrong/broken), **question** (unclear, needs clarification), **suggestion** (improvement)  
Status: **open** (all findings are open at time of this review)

| ID | Location | Summary | Type | Severity | Status | Owner | Notes |
|----|----------|---------|------|----------|--------|-------|-------|
| F-001 | REQ – `requirements.md` NF section | NF 3 label used twice: once for "Accessibility" and once for "Testability". Numbering is broken – two different requirements share the same identifier. | defect | major | open | Group 1 | Renumber NF 3 (Accessibility) and add NF 6 (Testability), or adjust numbering accordingly. |
| F-002 | REQ – `requirements.md` NF 3 (Accessibility) | The sentence "The system shall be usable for" is cut off mid-sentence. The requirement is incomplete and unverifiable. | defect | major | open | Group 1 | Complete the sentence; state the actual target group or accessibility standard. |
| F-003 | REQ vs SPEC – `requirements.md` (5 FRs) vs `spec.md` (30 FRs) | The two documents list requirements at completely different granularity levels with no cross-references. A reviewer or tester cannot determine which document is authoritative or whether all spec FRs are covered by the requirements baseline. | defect | major | open | Group 1 | Add a traceability note or cross-reference in both files, or consolidate into a single requirements document. |
| F-004 | REQ – `requirements.md` | Authentication/authorisation is not mentioned in `requirements.md` at all. `spec.md` FR-014 through FR-016 mandate OAuth2/Keycloak and session timeout. This omission leaves the security scope undefined. | defect | major | open | Group 1 | Add an authentication FR to `requirements.md` or explicitly reference `spec.md` for the full FR list. |
| F-005 | SPEC – `spec.md` footer | Document states it was auto-generated with spec-kit and Copilot. No record of human validation of the generated content. | question | minor | open | Group 1 | Document that content was reviewed and approved by the team, or add a validation note. |
| F-006 | SPEC – User Story 4 / `spec.md` SC-001–SC-010 | User Story 4 (Learning Progress / Analytics Dashboard) appears in the spec with acceptance scenarios and success criteria but has no corresponding implementation or test in the repository. The delta is not acknowledged anywhere. | question | minor | open | Group 1 | Mark User Story 4 as deferred (v2) explicitly in the spec, consistent with the spec's own Assumptions section. |
| F-007 | DM – `data-model.md`, `Message` entity | `Message.Sender` is typed as `BOOLEAN`, but the data model does not document what `true` and `false` represent (e.g., user = false, AI/bot = true). In the Java code `Message.sender` is also a raw `Boolean` with no Javadoc or constant. | defect | minor | open | Group 1 | Add a note in the data model specifying the boolean semantics, or replace with an enum (`SENDER_TYPE: USER \| BOT`). |
| F-008 | CODE – `controller/TestController.java` | The only REST controller in the repository returns `"Hello, World"` at `GET /`. No endpoints for sessions, messages, quizzes, or evaluations exist. `spec.md` FR-025 through FR-027 require a RESTful API with chat operations — these are entirely unimplemented. | defect | blocking | open | Group 1 | Implement the required REST endpoints, or explicitly scope them as out-of-scope for the current exercise deliverable. |
| F-009 | CODE – `model/Session.java`, `setUser()` and `setStartedAt()` | Both overriding setter methods throw `UnsupportedOperationException("Session: sessionID is not updateable")`. The error message always mentions `sessionID` regardless of which field triggered it, making debugging misleading. | defect | minor | open | Group 1 | Correct error messages to reference the actual field name (e.g., `"Session: user is not updateable"`). |
| F-010 | CODE – `services/QuizRequestService.java`, topic detection | Topic detection uses `content.contains("about") \|\| content.contains("Topic")`. The check for `"Topic"` is case-sensitive — a user writing `"topic"` (lowercase) would fail validation. The heuristic is fragile and undocumented. | defect | major | open | Group 1 | Use `content.toLowerCase().contains("topic")` at a minimum; document the expected prompt format in the API or via input validation. |
| F-011 | CODE – `services/QuizRequestService.java`, no-topic error | When no topic is detected, the service throws `AIServiceUnavailableException` with the message `"Error: No quiz topic provided."`. A missing topic is a *validation error*, not an AI service outage. Using the wrong exception type pollutes monitoring, logging, and error handling. | defect | major | open | Group 1 | Introduce a separate `InvalidQuizRequestException` (or use `IllegalArgumentException`) for input validation failures. |
| F-012 | CODE – `services/MessageService.java`, unhandled exception | `AIServiceUnavailableException` is a `RuntimeException` and is never caught by any `@ExceptionHandler` or `@ControllerAdvice`. Any AI failure will result in an HTTP 500 Internal Server Error response with a Java stack trace, rather than a structured, user-facing error message as required by `spec.md` FR-021 and FR-024. | defect | major | open | Group 1 | Add a `@ControllerAdvice` that maps `AIServiceUnavailableException` to HTTP 503 with a structured JSON body. |
| F-013 | CODE – `services/MessageService.java`, hardcoded string | `response.setMessageType("Message")` uses a plain string literal. No enumeration, constant class, or documentation defines the valid `messageType` values. | defect | minor | open | Group 1 | Define an enum or constant for message types to make the type system explicit and prevent typos. |
| F-014 | BDD – `askQuestion.feature` vs `fallback.feature` | Both feature files contain a scenario for "AI messaging is unavailable". The coverage is duplicated across two feature files without differentiation in scope. | suggestion | minor | open | Group 1 | Consolidate AI-fallback messaging scenarios into a single dedicated feature file, or clearly differentiate the scopes (e.g., `fallback.feature` covers both message and quiz, `askQuestion.feature` only covers the happy path). |
| F-015 | BDD – `reqestquiz.feature` filename | Filename contains a typo: `reqest` instead of `request`. | defect | editorial | open | Group 1 | Rename to `requestquiz.feature`. |
| F-016 | BDD – `askQuestion.feature`, test data | The question `"What is the most op animal in the world"` is unrelated to educational content. For a stakeholder walkthrough, domain-realistic test data is recommended. | suggestion | editorial | open | Group 1 | Replace with a course-relevant question, e.g., `"What is equivalence partitioning in software testing?"`. |

---

## 4. Data Summary (DS)

| Metric | Value | Notes |
|--------|-------|-------|
| Size of review object | ~900 NLOC (Java), ~12 doc pages | Java counted manually; docs counted by page estimate |
| Preparation effort | ~2 h | Individual async review |
| Number of findings (initial) | 16 | — |
| Number of findings after meeting | 16 | No meeting with authors; count unchanged |
| Rework effort (author) | — | Not tracked (external team) |
| Re-inspection required? | no | Major findings should be fixed; follow-up via issue tracker recommended |

---

## 5. Review Report (RR)

### 5.1 Summary

I reviewed Group 1's ESBot repository: the description doc, requirements, spec, data model, and the Java backend including BDD feature files. In total I found 16 findings.

The documentation has some clear problems — `requirements.md` and `spec.md` are very inconsistent (5 vs 30 requirements, no link between them, duplicate NF numbering, one sentence that cuts off mid-way). The Java domain model is actually well done though — the entities match the data model and the JPA setup looks correct. The BDD setup with Cucumber/Spring is solid too.

The main issue is the REST layer: the only controller is a `TestController` returning `"Hello, World"` — none of the required API endpoints exist. On top of that the service layer throws `AIServiceUnavailableException` for both AI failures and input validation errors, which is confusing and would cause problems when debugging.

### 5.2 Review Outcome

- **Review object state after review:** accepted with required changes
- **Major risks or themes:**
  - No REST API: the backend can't be accessed externally as the spec requires
  - `AIServiceUnavailableException` is thrown for both AI failures and validation errors — these should be separate exception types
  - `requirements.md` and `spec.md` are out of sync and can't be used together as a test basis
  - One requirement is incomplete (sentence cuts off mid-way in `requirements.md`)

### 5.3 Decisions and Follow-up

| Topic | Decision | Responsible | Due date |
|-------|----------|-------------|----------|
| F-001, F-002 | Fix NF numbering and complete the truncated Accessibility requirement | Group 1 | — |
| F-003, F-004 | Add cross-references between requirements.md and spec.md; add authentication FR to requirements baseline | Group 1 | — |
| F-008 | Implement REST controllers or scope as deferred with explicit justification | Group 1 | — |
| F-010, F-011 | Fix case-sensitive topic detection; introduce dedicated validation exception | Group 1 | — |
| F-012 | Add `@ControllerAdvice` for `AIServiceUnavailableException` → HTTP 503 | Group 1 | — |

### 5.4 Positive Observations

- The Java domain model is well structured and closely matches the data model document. JPA cascade relationships are set up correctly.
- Using `AIService` as a Java interface is a good decision — it makes mocking in tests clean and easy.
- The `UnitTestHelper` class with factory methods for test data is a nice pattern that cuts down a lot of boilerplate in the test setup.
- The Cucumber/Spring integration with `CucumberSpringConfig` and a shared `SharedSession` context shows they thought about how to handle state between step definitions.
- Naming the exception `AIServiceUnavailableException` explicitly instead of just using `RuntimeException` is good practice, even if it ends up being used for the wrong cases too.

### 5.5 Lessons Learned

- Having one clear requirements document — or at least a note saying "this spec extends requirements.md" — would make reviewing a lot easier. The inconsistency between the two files was probably the most confusing part of this review.
- Fixing feature file naming and test data is fast and low-effort. It makes a real difference when someone else reads the tests for the first time.

### 5.6 Sign-off

| Role | Name | Signature / date |
|------|------|------------------|
| Moderator | Mohammed Al-otaibi | 2026-05-05 |
| Author | Group 1 (hse-st-group1) | — (external team, not present) |
