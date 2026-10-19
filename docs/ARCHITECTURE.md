# CampusFlow Architecture

## Module map

```
campusflow/
├── main.py      — CLI: menu loop, input handling, display helpers.
│                  Owns all print()/input() calls; the library stays pure.
├── tickets.py   — ticket creation: validation, priority engine, ID
│                  generation, search.
├── workflow.py  — lifecycle state machine: assign → start → resolve →
│                  reopen, plus the priority-sorted open work queue.
├── reports.py   — summaries: by status, by priority, by category.
└── storage.py   — JSON persistence. Loads (missing file = empty store),
                   saves atomically via write-to-temp + os.replace.
```

## Design rules

- **Library raises, CLI handles.** Every `campusflow/*.py` module raises
  `ValueError` on bad input and never prints. `main.py` catches
  `(ValueError, OSError)` at the menu loop and prints the message.
- **Single data structure.** One list of ticket dicts, passed explicitly;
  no module-level state, no globals.
- **Ticket schema.** `id` (T001…), `title`, `category`
  (Network/Hardware/Software/Other), `urgency` (low/medium/high),
  `affected_users` (positive int), `priority` (critical/high/medium/low,
  derived at creation), `status` (open/in_progress/resolved),
  `assigned_to` (None until assigned).
- **Status machine.** open → in_progress (requires an assignee) →
  resolved → open again on reopen. Any other transition raises.

## Data flow

`main` loads `data/tickets.json` once at startup, mutates the list in
memory through the library, and saves after every change. Because saves
are atomic, a crash mid-session loses at most the in-flight edit.

## Tests

`tests/` mirrors the module map: one test file per module, standard
library `unittest`, no fixtures on disk — every test builds its own
ticket lists in memory.

Run the suite:

```
python3 -m unittest discover -s tests
```
