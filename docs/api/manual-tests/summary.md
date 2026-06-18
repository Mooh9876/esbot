# Manual API Testing – Summary

**Exercise:** 10.2
**Date:** 2026-06-16
**Tool used:** VS Code REST Client (`.http` files)
**Backend:** Python / FastAPI started with Uvicorn
**Base URL:** `http://localhost:8000`
**LLM Provider:** `StubAIProvider` (deterministic mock — no real AI inference)
**Database:** SQLite (`sqlite:////tmp/esbot_run.db`)

---

## Happy-Path Workflow Results

| Step | Request                          | Expected Status  | Actual Status    | Result |
| ---- | -------------------------------- | ---------------- | ---------------- | ------ |
| 1    | `GET /health`                    | `200 OK`         | `200 OK`         | ✅ Pass |
| 2    | `POST /sessions`                 | `201 Created`    | `201 Created`    | ✅ Pass |
| 3    | `GET /sessions`                  | `200 OK`         | `200 OK`         | ✅ Pass |
| 4    | `GET /sessions/1`                | `200 OK`         | `200 OK`         | ✅ Pass |
| 5    | `POST /sessions/1/messages`      | `201 Created`    | `201 Created`    | ✅ Pass |
| 6    | `GET /sessions/1/messages`       | `200 OK`         | `200 OK`         | ✅ Pass |
| 7    | `POST /sessions/1/quiz`          | `201 Created`    | `201 Created`    | ✅ Pass |
| 8    | `POST /sessions/1/quiz/1/answer` | `201 Created`    | `201 Created`    | ✅ Pass |
| 9    | `DELETE /sessions/1`             | `204 No Content` | `204 No Content` | ✅ Pass |

All happy-path requests were executed successfully. The backend responded with the expected status codes for creating, retrieving, updating through messages/quiz actions, and deleting a session.

---

## Error Scenario Results

| #  | Scenario                                                         | Expected Status            | Actual Status              | Result |
| -- | ---------------------------------------------------------------- | -------------------------- | -------------------------- | ------ |
| E1 | `GET /sessions/9999` — non-existent session                      | `404 Not Found`            | `404 Not Found`            | ✅ Pass |
| E2 | `POST /sessions/1/messages` with whitespace-only `content`       | `422 Unprocessable Entity` | `422 Unprocessable Entity` | ✅ Pass |
| E3 | `POST /sessions/1/messages` with missing `content` field         | `422 Unprocessable Entity` | `422 Unprocessable Entity` | ✅ Pass |
| E4 | `POST /sessions/1/quiz/9999/answer` — non-existent quiz question | `404 Not Found`            | `404 Not Found`            | ✅ Pass |
| E5 | `POST /sessions/9999/messages` — message to non-existent session | `404 Not Found`            | `404 Not Found`            | ✅ Pass |

All tested error scenarios behaved as expected. Invalid or missing resources returned `404 Not Found`, while invalid request bodies returned `422 Unprocessable Entity`.

---

## Observations and Reflections

### Were all status codes as expected?

Yes. All status codes matched the expected results. The API correctly returned:

* `200 OK` for successful read operations
* `201 Created` for successful resource creation
* `204 No Content` for successful deletion
* `404 Not Found` for missing sessions or quiz questions
* `422 Unprocessable Entity` for invalid request bodies

This shows that the implemented endpoints handle both normal requests and invalid inputs in a consistent way.

### Did the error messages provide useful feedback?

Yes, the error messages were mostly useful. The `404` responses clearly explained which resource was missing, for example when a session or quiz question could not be found.

The `422` validation responses were also helpful because they showed structured validation information, including the affected field and the reason for the validation failure.

One minor observation is that some validation details use English field names or default framework messages, while other messages are written in German. A fully consistent language style would make the API easier to understand for German-speaking users.

### Did any request behave unexpectedly?

No critical unexpected behavior was observed. The happy-path workflow worked from start to finish, and all error scenarios returned the expected status codes.

One minor difference compared to the exercise description is that the implemented `POST /sessions` endpoint does not require a `user_id` or `title`. The exercise describes creating sessions with user-specific data, but the current implementation creates sessions without requiring these fields. This is acceptable for the current prototype, but for a multi-user system it would be useful to include user identification and filtering.

During answer submission, a SQLAlchemy warning appeared in the backend logs:

```text
SAWarning: Object of type <EvaluationResult> not in session, add operation along
'SubmittedAnswer.evaluation' will not proceed
```

The API response was still successful, and the test itself passed. However, this warning should be checked later because it may indicate an ORM relationship or cascade configuration issue.

---

## Reproducibility

The manual tests can be reproduced by starting the backend locally and executing the `.http` files with the VS Code REST Client extension.

Backend start command used:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API was tested at:

```text
http://localhost:8000
```

The mock LLM provider was used so that chat and quiz responses were deterministic and did not depend on a real AI inference service.

---

## Files

| File                   | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `happy-path.http`      | Contains the documented happy-path API requests                             |
| `error-scenarios.http` | Contains the documented invalid request/error scenario tests                |
| `summary.md`           | Contains this manual testing summary                                        |
| Screenshot files       | Show executed requests and responses for the happy path and error scenarios |

---

## Conclusion

The manual API tests were successful. The ESBot backend handled the complete happy-path workflow correctly and returned meaningful error responses for invalid requests. The API is suitable for further automated and performance testing in the next exercise steps.

## Use of Artificial Intelligence

For this assignment, I used only **ChatGPT with the GPT-5.5 Thinking model** as AI support.
I mainly used the AI to receive suggestions for improving and structuring the manual API tests. This included suggestions for a complete **happy-path workflow** and suitable **error and negative test scenarios**.
I performed the actual API tests myself. I started the backend, executed the requests with the VS Code REST Client, checked the returned status codes and response bodies, and created the screenshots myself.
I also used ChatGPT to review my test cases, screenshot names, and written summary for completeness and clarity. The AI was therefore used as a support tool for suggestions, improvements, and verification. The execution, evaluation, and documentation of the test results were completed by me.


