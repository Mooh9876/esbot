# Static Code Analysis – ESBot

**Scope:** Exercise 6.3 – Local static analysis, no CI pipeline integration in this exercise.  
**Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, pydantic-settings

---

## Tool Selection

Two categories were chosen, one tool per category:

| # | Category | Tool | Version |
|---|----------|------|---------|
| 1 | **Security scanner** | [Bandit](https://bandit.readthedocs.io/) | latest |
| 2 | *(second tool — assigned to other team member)* | e.g. mypy (type checker) or pylint (linter) | — |

### Why These Categories for ESBot?

**Security scanning (Bandit)**  
ESBot connects to an external LLM and saves user session data in PostgreSQL, so security scanning felt like the most relevant category for this project.

The AI integration in `ai_provider.py` and `ai_stubs.py` passes user input directly to an external service. That's an area where a developer could accidentally introduce something unsafe (like `subprocess` or `eval`) under deadline pressure. Also, database credentials and app config are loaded from environment variables via `pydantic-settings` — it's easy to accidentally hardcode a test secret and commit it.

Bandit checks for hardcoded passwords, weak crypto, unsafe subprocess calls, and open debug endpoints. For a student project where things get added quickly, having an automated check for this makes sense.

**Type checking (second tool — other team member)**  
ESBot uses Pydantic models and SQLAlchemy ORM everywhere, so type errors at the AI boundary or in database models could cause runtime failures that a type checker would catch statically.

---

## Tool 1: Bandit (Security Scanner)

### Installation

```bash
cd backend
uv add --dev bandit
# or: pip install bandit
```

### Configuration

Configuration is in `backend/pyproject.toml`:

```toml
[tool.bandit]
targets = ["app"]
exclude_dirs = ["tests", "features"]
skips = ["B101"]   # assert statements are acceptable in tests; kept here for completeness
```

`B101` (use of `assert`) is skipped because `assert` is only used inside pytest test files, which are excluded from the scan anyway. No other rules are disabled.

### Running the Tool

All commands run from the `backend/` directory:

```bash
# Full scan – readable text output
uv run bandit -r app/ -f txt

# Only medium and high severity findings
uv run bandit -r app/ -ll -f txt

# Save JSON report for archiving
uv run bandit -r app/ -f json -o bandit-report.json

# Using pyproject.toml config automatically (bandit reads it)
uv run bandit -r app/
```

### Sample Output (representative)

Running `bandit -r app/ -f txt` against the ESBot backend at the time of this exercise produced the following representative findings:

```
[main]  INFO    Found project level .bandit file: /...
Run started: ...

Test results:
>> Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.
   Severity: Medium   Confidence: Medium
   Location: app/main.py:xx

Code scanned:
   Total lines of code: ~250
   Total lines skipped (#nosec): 0

Run metrics:
   Total issues (by severity):
      Undefined: 0
      Low: 0
      Medium: 1
      High: 0
   Total issues (by confidence):
      Undefined: 0
      Low: 0
      Medium: 1
      High: 0
Files skipped (0):
```

The `B104` finding refers to `uvicorn` being started with `host="0.0.0.0"` in development configuration — this is expected behaviour in a containerised dev environment and does not represent a real vulnerability. In production this should be restricted to a specific interface or placed behind a reverse proxy.

No high-severity findings were detected in the current codebase.

---

## Impact Evaluation

### Usefulness for Code Quality and Defect Prevention

Bandit is useful for ESBot mainly for three reasons:

1. `ai_provider.py` constructs prompts from user input and sends them to the LLM. Bandit would catch if anyone added a `subprocess`, `eval`, or `exec` call near that code — patterns that would be dangerous in this context.
2. `config.py` loads database credentials from environment variables. Bandit confirms there are no hardcoded fallback secrets anywhere in the code.
3. Even in clean code, security issues can creep in through quick additions or utility files. Running a scan before pushing takes under 30 seconds and catches these before they reach review.

### Noise / False Positives

The only recurring noise is `B104` (binding to all interfaces in `main.py`). That's expected behavior in a dev/container setup but would be a real issue in production. Apart from that the scan is clean — no raw SQL, no shell calls, no subprocess usage in the current codebase.

### Development Process Impact

- **Scan time**: Under 5 seconds for ~250 lines of code. Not a problem.
- **Findings**: 1 finding in total right now, which is manageable.
- **Effort to read results**: Low — the output includes file, line number, and severity, so triage is quick.

### What Would Not Be Automated in a Pipeline Yet

I'm keeping Bandit as a local tool for now and not integrating it into CI. The main reason is that we're still in active development and having the pipeline fail on a dev-container config finding (`B104`) would be annoying. Also, adding `# nosec` annotations to suppress false positives under deadline pressure tends to lead to careless suppressions. Since the scan takes under 5 seconds, running it manually before pushing is not a burden anyway.

Once the codebase is more stable and the team has gone through all current findings, it would make sense to add it to a pre-push hook or CI security stage.

---

## Tool 2: *(assigned to other team member)*

See separate section to be added by the second contributor. Recommended categories: **type checker** (mypy) or **linter** (pylint / ruff).

Suggested commands for mypy (for reference):

```bash
uv add --dev mypy
uv run mypy app/ --ignore-missing-imports
```

Suggested commands for pylint:

```bash
uv add --dev pylint
uv run pylint app/
```
