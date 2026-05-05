# Review Retrospective – Group 1 ESBot Technical Review

**Review conducted:** 2026-05-05  
**Review reference:** REV-2026-001 (`docs/reviews/review-group1-2026-05-05.md`)  
**Reviewed team:** hse-st-group1

---

## What Worked Well

The LoF table structure turned out to be more useful than I expected. It forced me to be specific — I couldn't just write "this is confusing", I had to write down the exact file, what the issue is, and how serious it is. That made the findings a lot more actionable.

Reviewing the docs, data model, and code at the same time also revealed inconsistencies I wouldn't have caught otherwise. The mismatch between `requirements.md` (5 FRs) and `spec.md` (30 FRs) was only visible because I was comparing both files at once.

The positive observations section was a good addition too. Noting what Group 1 did right (like the `AIService` interface design and the `UnitTestHelper` pattern) gave a more balanced picture and also gave me ideas for our own code.

---

## What Was Difficult

The biggest problem was the async format. I had no way to ask Group 1 whether something was intentional or just not done yet. For F-008 (the REST layer being just a "Hello, World" placeholder) I genuinely wasn't sure if that was a scope decision or something they didn't finish. In a real review you'd just ask in the meeting.

The different tech stack was also a challenge. Group 1 uses Java 21 + Spring Boot and I work with Python + FastAPI. Understanding how Lombok, JPA annotations, and `@ControllerAdvice` work in Spring required some extra reading — probably about 30 extra minutes of context-gathering.

---

## Are Formal Reviews Suitable for Our Team?

For a project at this scale, a technical review fits well. A full formal inspection with NLOC counting, defect density metrics, and mandatory re-inspection gates would take more time than the whole exercise is worth.

| Artefact type | Recommendation |
|---------------|----------------|
| Requirements / specification | Technical review |
| Data model | Technical review (together with requirements) |
| Domain model / entities | Technical review or walkthrough |
| Service / business logic | Technical review |
| Controller / API layer | Checklist-based review + API contract tests |
| BDD feature files | Walkthrough |

I wouldn't use formal inspection for normal pull requests — that's too much overhead for routine work.

---

## One Thing I Would Do Differently

Before starting individual preparation I'd ask the reviewed team to send a short "known limitations" note — just a few lines about what they intentionally left out or deferred. For this review, I spent time trying to figure out whether F-008 (missing REST layer) was an oversight or a known scope decision. A single sentence in their README would have cleared that up immediately and changed how I classified that finding.

For the next review round I'll suggest we ask for this before the preparation phase starts.
