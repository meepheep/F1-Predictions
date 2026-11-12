# F1-Predictions

F1 race prediction model in Python. Setup, commands and layout are in [README.md](README.md).

## Current status

@PROGRESS.md

## How to work with me

- **I write the code myself.** This is a learning project. Don't edit source or test files unless
  I explicitly ask. Explain the bug and give a hint, or show a small generic pattern, rather than
  the finished code.
- Reviewing my changes, running the script, tests, ruff and read-only database queries to check
  my work is fine and helpful.
- I'm on Windows. The terminal is PowerShell 5.1, which doesn't support `&&`, so use `;` or
  separate commands.

## Keeping PROGRESS.md current

When I finish a task or we agree on a new next step, update `PROGRESS.md`:
- tick off the checklist items
- update "Done" if the schema or commands changed
- add one line to the session log
- bump "Last updated"

This is the one file you may edit without asking. Keep it short; it's loaded into every session.

## Conventions

- All reusable code lives in `src/f1_predictions/`; paths come from `config.py`.
- Ruff with line length 100: run `ruff check .` and `ruff format .` before committing.
- Features must use only data from earlier races (no leakage). Evaluate with walk-forward
  backtests, never random splits.
