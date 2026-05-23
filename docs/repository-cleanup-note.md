# Repository Cleanup Note

This cleanup prepares the project for publication as a lean GitHub repository.

Removed local artifacts:

- `backend/.venv`
- Python `__pycache__` folders and compiled bytecode
- `frontend/node_modules`
- Vite build output in `frontend/dist`
- local SQLite database `backend/triage.db`

These files were removed because they are generated locally, environment-specific, or potentially sensitive. They are not needed to understand, run, or evaluate the project from source.

The `.gitignore` now covers Python, FastAPI runtime files, React/Vite artifacts, SQLite databases, virtual environments, editor files, macOS files, and common temporary files.

Risks avoided:

- publishing local dependencies instead of reproducible install files
- exposing local database contents
- committing machine-specific virtual environments
- adding compiled caches and build output to the repository history
- making the repository heavier and harder to review

Note: this workspace is not currently initialized as a Git repository, so no tracked files could be removed with `git rm --cached`. If the project is initialized later and any ignored artifact is already tracked, remove it from the index without deleting the local file:

```bash
git rm --cached <path>
```
