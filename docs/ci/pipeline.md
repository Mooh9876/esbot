# CI Pipeline Design (ESBot)

This document explains the configuration decisions in `.github/workflows/ci.yml`.

---

## Triggers

```yaml
on:
  push:
  pull_request:
```

**`push`** — runs the pipeline on every commit pushed to any branch. This catches broken commits immediately, regardless of whether a pull request exists. It also means commits on `main` are verified after merge.

**`pull_request`** — runs the pipeline when a pull request is opened or updated. This is the most important trigger: it ensures no change reaches `main` without passing tests and the security scan. The result is visible directly in the pull request before anyone reviews the code.

No branch filters are set intentionally — all branches should be verified, not only `main`. If the repository grows and branch noise becomes an issue, filtering to `main` and `develop` can be added later.

`workflow_dispatch` (manual trigger) is not included because there is no current need to manually trigger the pipeline outside of a push or PR. It could be added when integration tests against a staging environment are introduced.

---

## Runner

```yaml
runs-on: ubuntu-latest
```

`ubuntu-latest` is the standard choice for Python CI. It is fast, well-supported, and has Python available by default. There is no platform-specific code in ESBot that would require macOS or Windows runners.

---

## Environment and Setup

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install uv
```

Python 3.11 matches the minimum version declared in `pyproject.toml` (`requires-python = ">=3.11"`). Using the exact minimum ensures that the pipeline catches any accidental use of a newer language feature that would break on the declared minimum.

`uv` is used as the package manager because the project already uses it locally. It is installed via `pip` rather than a dedicated action to keep the setup minimal and transparent.

---

## Dependency Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('backend/pyproject.toml') }}
```

The uv download cache (`~/.cache/uv`) is cached using `pyproject.toml` as the cache key. When dependencies have not changed between runs, `uv sync` uses the cached packages and skips downloading them. This reduces install time from ~30s to ~3s on a warm cache.

The cache is invalidated automatically whenever `pyproject.toml` changes (e.g., a dependency is added or updated).

---

## Jobs and Steps

The pipeline has a single job (`test`) with the following steps:

| Step | Purpose |
|---|---|
| `actions/checkout@v4` | Check out the repository |
| `actions/setup-python@v5` | Install Python 3.11 |
| `pip install uv` | Install the uv package manager |
| `actions/cache@v4` | Restore/save the dependency cache |
| `uv sync --all-groups` | Install all dependencies including dev group |
| `uv run pytest` | Run the full test suite |
| `uv run bandit -r app/` | Run the security scan |

All `run` steps use `working-directory: backend` (set as a job-level default) because the Python project lives in the `backend/` subdirectory.

**What is intentionally NOT in CI:**

- **Live LLM (Ollama / vLLM):** All service tests use mocks (`ai_stubs.py`). There is no step that starts or connects to an inference engine. This keeps the pipeline fast and deterministic.
- **PostgreSQL:** Tests use SQLite in-memory via SQLAlchemy's `StaticPool`. No database service container is needed.
- **Radon (complexity):** Radon does not have a meaningful pass/fail criterion — complexity thresholds are subjective and fluctuate during active development. It is documented as a local-only informational tool in `docs/ci/local-verification.md`.

---

## Parity: Local vs. CI

| Local command | CI step |
|---|---|
| `uv run pytest` | `uv run pytest` (same command) |
| `uv run bandit -r app/` | `uv run bandit -r app/` (same command) |

The commands are identical. If a test fails in CI, running the same command locally will reproduce the failure.

**If CI fails but passes locally:**
The most likely cause is a dependency version difference. Locally the `.venv` may have a different version of a package than what `uv sync` installs on the CI runner. Check `uv.lock` and make sure it is committed and up to date. Running `uv sync --all-groups` locally (without the existing `.venv`) should reproduce the CI environment exactly.

**If CI passes but fails locally:**
This should not happen given that commands are identical and the database is in-memory. If it does, check that the local `.venv` is not stale — delete it and run `uv sync --all-groups` again.

---

## Exercise 9.2 Enhancements

### What was added: Python version matrix

The `test` job now uses a GitHub Actions **matrix strategy** to run the full test suite (pytest + Bandit) in parallel on three Python interpreter versions:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

All steps that previously referenced `"3.11"` now use `${{ matrix.python-version }}`. The dependency cache key was extended with the Python version (`${{ runner.os }}-${{ matrix.python-version }}-uv-...`) so that each version maintains its own isolated cache and there is no cross-version cache pollution.

---

### Why it fits ESBot

`pyproject.toml` declares `requires-python = ">=3.11"`, which means the package is intended to support any Python 3.11 or newer. The matrix validates this claim concretely:

- **3.10** — verifies that a user on the previous LTS release gets a clear failure message rather than a silent runtime error (expected to fail if 3.10-only syntax is used, which is caught early).
- **3.11** — the current baseline; matches the original CI and local development environment.
- **3.12** — verifies forward compatibility with the latest stable release, catching deprecations in the standard library or third-party packages before they silently break for users on newer interpreters.

Without the matrix, a syntax change or a dependency that drops support for an older version would only be discovered when a user reports a runtime crash — not in CI.

---

### Added value vs. cost

| Dimension | Assessment |
|---|---|
| **Security** | No direct impact; Bandit still runs on each matrix leg, so any security finding is caught on all three versions. |
| **Speed** | Three parallel jobs instead of one. Wall-clock time stays roughly the same as the slowest single job; GitHub Actions runs matrix legs concurrently on free-tier ubuntu-latest runners. Total runner-minutes consumed rises 3×, which is acceptable given the current short job duration (~1–2 min per leg). |
| **Maintenance** | Near-zero. Adding a new Python version later is a single-line change. Removing end-of-life versions (e.g., dropping 3.10 when it reaches EOL) is equally trivial. |
| **False positives** | Very low. Failures on a specific Python version indicate a real compatibility issue, not a flaky environment. |

---

### Local vs. CI parity

Locally, developers run pytest and Bandit against whichever Python version their `uv` virtual environment uses (typically 3.11 or 3.12). The CI matrix covers the versions that are not actively used day-to-day locally, which is exactly its purpose.

| Local command | CI equivalent |
|---|---|
| `uv run pytest` | `uv run pytest` on **3.10**, **3.11**, **3.12** |
| `uv run bandit -r app/` | `uv run bandit -r app/` on **3.10**, **3.11**, **3.12** |

To reproduce a specific matrix leg locally, switch the Python interpreter explicitly:

```bash
uv python pin 3.10
uv sync --all-groups
uv run pytest
```
