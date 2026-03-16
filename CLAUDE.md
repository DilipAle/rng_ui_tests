# Auto360 — Claude Code Instructions

## Test Generation

When asked to generate or update tests for this project:

1. Read `contexts/pytest-tester-agent.md` carefully before writing any code.
2. Follow every rule in that file — architecture, fixtures, markers, file placement.
3. If the request references a `.md` file under `/prompts`, read that file first.
   It contains the acceptance criteria that define what the test must prove.
4. After generating the test, add a comment at the top of the prompt `.md` file:
   `<!-- File: <project>/tests/ui/<feature>/test_<feature>.py -->`
   This links the acceptance criteria to the generated test permanently.
   Make NO other changes to the prompt file.

## Project Structure Reminder

```
AuotmationAuto360/
├── shared/                   ← BasePage, Config — shared by all UI projects
├── renegade-ui-tests/        ← Salesforce Lightning UI tests
├── agency-height-tests/      ← Agency Height portal UI tests
├── customer-portal-tests/    ← Customer self-service portal UI tests
├── salesforce-api-tests/     ← Salesforce REST API tests
├── prompts/
│   ├── renegade-ui-tests/    ← Acceptance criteria for Renegade Salesforce tests
│   ├── agency-height-tests/  ← Acceptance criteria for Agency Height tests
│   ├── customer-portal-tests/← Acceptance criteria for Customer Portal tests
│   └── salesforce-api-tests/ ← Acceptance criteria for Salesforce API tests
├── contexts/                 ← Agent context files (framework rules for AI)
└── CLAUDE.md                 ← This file
```

## Data Rules (Always Enforce)

- Creating new data → always use unique/generated values (faker, timestamps)
- Every test that creates data must clean it up at the end
- Never delete data that was not created in the same test
- Never commit `.env` files or credentials

## Running Tests

```bash
# Smoke — every deploy
cd renegade-ui-tests && venv/bin/pytest -m smoke -v

# Regression — nightly
cd renegade-ui-tests && venv/bin/pytest -m regression -v

# Single file
cd renegade-ui-tests && venv/bin/pytest tests/ui/login/test_login.py -v
```

## Commit Rules

- Never auto-commit — always ask before committing
- Never commit .env files, venv/, screenshots/, allure-results/
