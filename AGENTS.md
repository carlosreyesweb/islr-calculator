# AGENTS.md

Guidance for agentic coding tools working in this repository.

## Project Snapshot

- Project: `islr-calculator` (terminal app for Venezuelan ISLR calculations)
- Language: Python `>=3.12`
- Package/dependency manager: `uv`
- Runtime entrypoint: `main.py`
- Main code directory: `src/`
- UI stack: `rich` + `questionary`
- Config source: `.env` + `tax_brackets.csv`

## Repository Rules Discovery

Checked for extra agent instructions in:

- `.cursor/rules/**`
- `.cursorrules`
- `.github/copilot-instructions.md`

Status: none of these files currently exist in this repo.

If they are added later, treat them as higher-priority supplements to this file.

## Setup Commands

- Install dependencies: `uv sync`
- Create `.env` from sample: `cp .env.example .env`
- Run app (preferred): `uv run main.py`
- Alternate run: `python main.py`

## Build / Lint / Test Commands

This repository currently has no dedicated build system, linter config, or test suite committed.
Use the commands below as the operational baseline for agents.

### Build / Packaging

- There is no separate compile/build step for runtime.
- Smoke-check app startup: `uv run main.py`
- Optional syntax check: `uv run python -m compileall main.py src`

### Lint / Formatting

- No `ruff`, `black`, `mypy`, or other lint config is defined in `pyproject.toml` today.
- If linting is requested, first prefer tools already used by the repo owner.
- Do not introduce a formatter/linter config as a side effect unless asked.

### Tests

- No `tests/` directory currently exists.
- No `pytest` config is currently committed.
- If tests are added, use `pytest` via `uv run`.

Examples agents should use when tests exist:

- Run all tests: `uv run pytest`
- Run one file: `uv run pytest tests/test_calculator.py`
- Run one test (node id): `uv run pytest tests/test_calculator.py::test_calculate_tax_basic`
- Run one test class method: `uv run pytest tests/test_config.py::TestConfig::test_fallback_rate`
- Run by keyword: `uv run pytest -k "installment and not slow"`
- Stop after first failure: `uv run pytest -x`

Single-test execution rule for agents:

- Prefer a narrow test first (`file::test_name`) before running full suite.
- After targeted pass, run broader relevant scope if changes touch shared logic.

## Architecture and Module Boundaries

- `main.py`: app composition and top-level control flow.
- `src/config.py`: environment + CSV loading, runtime configuration, external USD rate fetch.
- `src/calculator.py`: core tax/business logic and installment/breakdown calculations.
- `src/console.py`: all terminal UI rendering and interactive prompts.
- `src/models.py`: shared typed dataclasses and enums.
- `src/i18n/`: translation loader + locale JSON files.

Boundary expectations:

- Keep business math in `calculator.py`, not in UI layer.
- Keep prompt/printing concerns in `console.py`, not in calculator/config.
- Keep reusable data contracts in `models.py`.
- Keep user-facing copy in locale JSON files and resolve through `t()`.

## Code Style Guidelines

Follow existing code conventions before introducing new patterns.

### Imports

- Use absolute imports from `src` (e.g., `from src.models import TaxBracket`).
- Group imports in this order:
  1) standard library
  2) third-party packages
  3) local `src` imports
- Avoid wildcard imports.
- Import only what is used.

### Formatting

- Follow PEP 8 and current repository style.
- Use 4-space indentation.
- Prefer readable multi-line calls with trailing commas.
- Keep line length reasonable (existing code is generally compact/readable).
- Preserve existing docstring style (triple double quotes).

### Types and Data Modeling

- Add type hints for function arguments and return values.
- Prefer modern union syntax (`X | None`) and built-in generics (`list[T]`).
- Use `@dataclass` for structured shared data.
- Use enums (`StrEnum`) for constrained string choices.
- Keep currency/unit suffixes explicit in names (`_ves`, `_usd`, `_ut`).

### Naming

- Modules/functions/variables: `snake_case`.
- Classes/enums: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE` (e.g., `BCV_API_URL`).
- Boolean flags should read clearly (`usd_rate_is_live`, `is_*`, `has_*`).
- Prefer descriptive names over abbreviations unless domain-standard (`UT`, `USD`, `VES`).

### Error Handling and Validation

- Startup/config failures: print clear user-facing error and exit non-zero.
- Recoverable input issues: re-prompt user in loops (current `ConsoleUI` pattern).
- External API calls: apply timeout and handle network/parse errors gracefully.
- Never allow negative income/dependents; validate and show localized error text.

### i18n and User-Facing Text

- Do not hardcode new user-facing strings in Python code.
- Add new strings to locale files (`src/i18n/locales/en.json` and `es.json`).
- Use `t("dot.notation.key")` for all display text.
- Keep interpolation placeholders stable and explicit (e.g., `{currency}`).

### Domain Logic Rules

- Keep all tax calculations in annual VES/UT math internally.
- Convert currencies only at clear boundaries.
- Avoid changing installment schedule semantics unless explicitly requested.
- Preserve bracket matching behavior and top-bracket fallback.

### Console/UI Conventions

- Use `rich` tables/panels consistently with existing style.
- Keep menu behavior safe on cancelled prompts (existing defaults exit or fallback).
- Keep summary output concise; detailed breakdown stays optional.

## Change Management Guidance for Agents

- Make focused, minimal diffs.
- Do not refactor unrelated files opportunistically.
- Preserve backward-compatible CLI flow unless asked to redesign.
- Update README when behavior/config/env variables change.
- If adding tests, mirror module names and keep test names behavior-focused.

## Quick Pre-PR Checklist

- `uv sync` completed successfully.
- `.env` requirements are documented for any new config.
- App starts with `uv run main.py`.
- Any added tests can run with targeted `pytest file::test_name` command.
- i18n keys updated in both English and Spanish when relevant.
