# Test Design – ESBot

## 7.1 Black-Box Testing Techniques

We used black-box techniques here, so we only looked at the spec — no source code.
The relevant validation rules for `QuizRequest` are:

- `topic`: 3–100 characters
- `count`: integer, 1–10
- `difficulty`: must be `easy`, `medium`, or `hard`

---

### Step 1 – Equivalence Classes

#### `topic`

| Parameter | Class ID | Type    | Description                        | Test Value         |
|-----------|----------|---------|------------------------------------|--------------------|
| `topic`   | EC-T-1   | Valid   | 3–100 characters                   | `"Python"`         |
| `topic`   | EC-T-2   | Invalid | shorter than 3 chars               | `"ab"`             |
| `topic`   | EC-T-3   | Invalid | longer than 100 chars              | `"a" * 101`        |
| `topic`   | EC-T-4   | Invalid | empty string or null               | `""` / `null`      |

#### `count`

| Parameter | Class ID | Type    | Description                        | Test Value  |
|-----------|----------|---------|------------------------------------|-------------|
| `count`   | EC-C-1   | Valid   | integer between 1 and 10           | `5`         |
| `count`   | EC-C-2   | Invalid | 0 or negative                      | `0`         |
| `count`   | EC-C-3   | Invalid | 11 or more                         | `11`        |
| `count`   | EC-C-4   | Invalid | wrong type (string, float, etc.)   | `"five"`    |
| `count`   | EC-C-5   | Invalid | null / not provided                | `null`      |

#### `difficulty`

| Parameter    | Class ID | Type    | Description                         | Test Value   |
|--------------|----------|---------|-------------------------------------|--------------|
| `difficulty` | EC-D-1   | Valid   | `"easy"`                            | `"easy"`     |
| `difficulty` | EC-D-2   | Valid   | `"medium"`                          | `"medium"`   |
| `difficulty` | EC-D-3   | Valid   | `"hard"`                            | `"hard"`     |
| `difficulty` | EC-D-4   | Invalid | anything else                       | `"extreme"`  |
| `difficulty` | EC-D-5   | Invalid | empty or null                       | `""` / `null`|

---

### Step 2 – Justification + Boundary Value Analysis

**EC-T-1** – `"Python"` is a typical valid topic, nothing special about it, just a normal case. Represents all inputs that are within the allowed length. → FR3

Boundaries for `topic`:

| Position       | Value        | Length | Result   |
|----------------|--------------|--------|----------|
| just below min | `"ab"`       | 2      | rejected |
| minimum        | `"abc"`      | 3      | accepted |
| just above min | `"abcd"`     | 4      | accepted |
| just below max | `"a" * 99`   | 99     | accepted |
| maximum        | `"a" * 100`  | 100    | accepted |
| just above max | `"a" * 101`  | 101    | rejected |

**EC-T-2** – `"ab"` is one char below the minimum. All inputs in this class fail for the same reason, so one value is enough to represent them. → FR3

**EC-T-3** – `"a" * 101` is one char above the upper bound. Also relevant for NFR7 (security) since unbounded string inputs are a known risk.

**EC-T-4** – Empty/null is its own class, not the same as "too short". A missing topic means the whole request can't be processed. → FR3

**EC-C-1** – `5` is a mid-range valid value, no edge case involved. → FR3

Boundaries for `count`:

| Position       | Value | Result   |
|----------------|-------|----------|
| just below min | `0`   | rejected |
| minimum        | `1`   | accepted |
| just above min | `2`   | accepted |
| just below max | `9`   | accepted |
| maximum        | `10`  | accepted |
| just above max | `11`  | rejected |

**EC-C-2** – `0` is the most interesting boundary here — zero questions is semantically pointless. → FR3

**EC-C-3** – `11` is directly over the limit. → FR3

**EC-C-4** – `"five"` as a string where an integer is expected. The type check should happen before any range validation. → FR3, NFR7

**EC-C-5** – A missing count is different from 0 — the field just isn't there. → FR3

**EC-D-1/2/3** – The three accepted values each form their own class since the spec defines them as an explicit enum. All three need to work. → FR3

**EC-D-4** – `"extreme"` is a representative for all undefined difficulty values. Needs to be rejected so the AI doesn't get garbage input. → FR3, NFR7

**EC-D-5** – Same idea as EC-T-4: no value at all is different from a wrong value. → FR3

---

### Step 3 – Decision Table for Answer Evaluation (FR4)

Three conditions affect what happens when a student submits an answer:

| # | Condition | Values |
|---|-----------|--------|
| C1 | answer is empty/blank | yes / no |
| C2 | quiz item exists in session | yes / no |
| C3 | correctness (from AI) | correct / partial / incorrect |

C3 only matters when C1=No and C2=Yes. Otherwise it's a don't-care (–).

| Rule | C1: Empty | C2: Item exists | C3: Correctness | Output                                             | Req.       |
|------|-----------|-----------------|-----------------|----------------------------------------------------|------------|
| R-01 | yes       | yes             | –               | error: answer is empty                             | FR4, NFR7  |
| R-02 | yes       | no              | –               | error: answer is empty                             | FR4, NFR7  |
| R-03 | no        | no              | –               | error: quiz item not found / session expired       | FR4, FR6   |
| R-04 | no        | yes             | correct         | positive feedback                                  | FR4        |
| R-05 | no        | yes             | partial         | partial feedback + explanation                     | FR4        |
| R-06 | no        | yes             | incorrect       | corrective feedback + explanation                  | FR4        |

- R-01 and R-02: empty check comes first regardless of whether the item exists.
- R-03: happens when a session expired while the user was still on the quiz page — realistic edge case.
- R-05: partial correctness is important for open-ended answers, a pure yes/no would lose information there.
