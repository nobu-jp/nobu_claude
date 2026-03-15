# CLAUDE.md

This file provides guidance for AI assistants (Claude Code and similar tools) working in this repository.

## Repository Overview

- **Repository**: nobu-jp/nobu_claude
- **Status**: Newly initialized — no source code has been committed yet.
- **Primary branch**: `main` (or as configured by the project owner)

> When source code is added, update this file to reflect the actual project purpose, tech stack, and structure.

## Git Workflow

### Branch Naming

- Feature branches created by Claude must follow the pattern: `claude/<description>-<session-id>`
  - Example: `claude/add-claude-documentation-Tg7np`
- Human-led feature branches: `feature/<description>` or `<author>/<description>`

### Commit Conventions

Write clear, imperative commit messages:

```
Add CLAUDE.md with initial repository documentation
Fix authentication bug in login flow
Update dependencies to latest versions
```

- Keep the subject line under 72 characters
- Use present tense ("Add" not "Added")
- Reference issue numbers when applicable: `Fix login bug (#42)`

### Push Workflow

```bash
# Always set upstream on first push
git push -u origin <branch-name>
```

- **Never force-push to `main`/`master`**
- If a push fails due to network errors, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

## Development Setup

> This section should be populated once the project is initialized with source code.

Typical setup steps will include:

1. Clone the repository
2. Install dependencies (e.g., `npm install`, `pip install -r requirements.txt`, etc.)
3. Copy environment config: `cp .env.example .env` and fill in values
4. Run the development server or build

## Testing

> Populate once tests are configured.

Run tests before committing. Common commands:

```bash
# JavaScript/TypeScript
npm test
npm run test:watch

# Python
pytest
python -m pytest tests/

# Go
go test ./...
```

## Code Style & Linting

> Populate once linters/formatters are configured.

Always run the linter and formatter before committing:

```bash
# JavaScript/TypeScript (common)
npm run lint
npm run format

# Python (common)
ruff check .
black .
```

## Project Structure

> Update this section once source code is added.

```
nobu_claude/
├── CLAUDE.md          # This file
├── README.md          # Human-facing documentation (add when project is set up)
├── .gitignore         # Add appropriate ignores for the chosen tech stack
└── src/               # Source code (to be created)
```

## Key Conventions for AI Assistants

1. **Read before editing** — Always read a file before modifying it.
2. **Minimal changes** — Only change what is necessary to complete the task. Avoid refactoring unrelated code.
3. **No secrets in code** — Never commit API keys, passwords, or tokens. Use environment variables.
4. **Confirm destructive actions** — Ask before deleting files, dropping data, or force-pushing.
5. **Update this file** — When the project structure or workflows change, update CLAUDE.md to reflect reality.
6. **Security first** — Avoid introducing OWASP Top 10 vulnerabilities (SQL injection, XSS, command injection, etc.).

## Environment Variables

> Document required environment variables here once the project is set up.

```
# Example
DATABASE_URL=postgres://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
```

Never commit `.env` files. Use `.env.example` as a template with placeholder values.
