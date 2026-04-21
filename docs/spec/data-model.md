# Data Model Documentation: ESBot Backend

## 1. Selected Entities

Based on the implementation, six core entities have been identified:

| Entity | Description |
| :--- | :--- |
| **UserSession** | The entry point for every user interaction. Groups messages and quiz requests. |
| **Message** | Represents a chat message (either from the user or the bot) within a session. |
| **QuizRequest** | A specific request from the user to generate a quiz on a certain topic and difficulty level. |
| **QuizItem** | A single question within a quiz, including the correct answer. |
| **SubmittedAnswer** | The answer provided by the user for a specific `QuizItem`. |
| **EvaluationResult** | The evaluation result of a submitted answer (Correct/Incorrect including feedback). |

---

## 2. Relationship Cardinalities

The relationships in the system follow a hierarchical structure to preserve the context of the learning session:

* **UserSession 1 : N Message**: A session can contain many chat messages.
* **UserSession 1 : N QuizRequest**: A user can request multiple quizzes within a single session.
* **QuizRequest 1 : N QuizItem**: A quiz consists of several individual questions.
* **QuizItem 1 : N SubmittedAnswer**: A question can have multiple answer attempts (implemented as 1:N).
* **SubmittedAnswer 1 : 1 EvaluationResult**: Each submitted answer has exactly one corresponding result.

---

## 3. Persistence Mapping Strategy

A **Relational Mapping (RDBMS)** using **SQLAlchemy (ORM)** was chosen for this project.

### Justification:
1.  **Strict Structure**: The data (quizzes, questions, answers) is highly structured. A relational schema ensures that no `SubmittedAnswer` exists without an existing `QuizItem` (Referential Integrity).
2.  **ACID Compliance**: Since the system stores learning progress and evaluations, data consistency (e.g., when deleting a session via `cascade="all, delete-orphan"`) is of high importance.
3.  **Query Efficiency**: Relational databases like PostgreSQL allow for efficient joins to aggregate data, such as compiling all evaluations of an entire `UserSession`.

---

## 4. Entity-Relationship Diagram (ERD)

The following diagram uses Crow's Foot notation to visualize the database schema:

<img width="641" height="636" alt="Unbenanntes Diagramm drawio (2)" src="https://github.com/user-attachments/assets/d06bf5df-d5d3-4040-994d-e33e3d26eb8a" />
