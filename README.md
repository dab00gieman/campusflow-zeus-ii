# CampusFlow-zeus-ii — Campus Helpdesk Ticket Manager

CampusFlow is a Python command-line ticket manager built for the Learn2Earn
AI-Native Engineering Sprint by Team Zeus II. Campus staff receive technical
support requests (Wi-Fi outages, faulty laptops, broken dev environments,
inaccessible platforms) that get lost in informal channels. CampusFlow records
those problems as tickets, prioritizes them automatically, assigns
responsibility, and tracks each one from open to resolved.

## Team and Contributions

- Michael (Partner B) — assignment, status workflow, work queue, reports,
  JSON persistence and their tests. Author of PR #2, reviewer of PR #1.
- Temple-Daemon (Partner A) — ticket creation, input validation, priority
  engine and their tests. Author of PR #1, reviewer of PR #2.

## Requirements and Setup

- Python 3.10 or newer (standard library only; no external packages).
- Clone the repository, then from the project root:

  python3 main.py

No virtual environment is strictly required, but if you prefer one:

  python3 -m venv .venv
  source .venv/bin/activate

## Running the CLI

Run `python3 main.py`. On startup, CampusFlow loads existing tickets from
data/tickets.json (a missing file starts a fresh, empty collection). The
menu offers:

1. Create ticket — enter title, category (Network/Hardware/Software/Other),
   urgency (low/medium/high) and affected users; the priority is calculated
   automatically and a unique ID (T001...) is assigned.
2. List all tickets — one-line summary of every ticket.
3. View a ticket — full details for one ticket ID.
4. Assign a ticket — set a non-empty staff name on a valid ticket.
5. Start work — move an assigned, open ticket to in_progress.
6. Resolve ticket — complete an in_progress ticket.
7. Reopen ticket — move a resolved ticket back to open.
8. Work queue — open tickets sorted by priority, then by ticket ID.
9. Reports — totals and breakdowns by status and priority.
0. Save and exit — writes tickets to JSON and closes.

Invalid input (blank title, zero/negative/text affected users, unknown
categories or urgency, bad workflow transitions) is rejected with a clear
error message; stored tickets are never corrupted.

## Tests

Run the full suite from the project root:

  python -m unittest discover -s tests -v

The tests cover: priority boundaries (high+12 -> critical, high+2 -> high,
low+4 -> medium, low+1 -> low), rejection of invalid inputs (zero affected
users, blank title, bad urgency/category), workflow rules (unassigned tickets
cannot start; open -> in_progress -> resolved; reopen works; invalid
transitions rejected), queue sorting (priority order, numeric ID tie-break,
in_progress excluded), report totals including the zero-ticket case, and
JSON persistence (save/reload preserves tickets, IDs stay unique after
reload, malformed JSON errors clearly without erasing data).

## How Priority and Status Work

Priority is calculated from urgency and affected users, first match wins:
1. high urgency AND 10+ affected users -> critical
2. high urgency OR 10+ affected users -> high
3. medium urgency OR 3+ affected users -> medium
4. otherwise -> low

Status flows open -> in_progress -> resolved. A ticket must be assigned
before it can move to in_progress. A resolved ticket can only change after
an explicit reopen, which returns it to open. The work queue shows open
tickets only, sorted critical > high > medium > low, ties by ascending
ticket ID; in_progress tickets remain visible via list/view and reports.

## Where Tickets Are Saved

Tickets persist to `data/tickets.json` on save/exit and reload on startup.
The file is ignored by Git. To start completely fresh, delete
data/tickets.json — the application then begins with an empty collection.
A malformed JSON file produces a clear error instead of silently erasing
data.

## Known Limitations and Future Improvements

- The work queue excludes in_progress tickets by design; interpretation of
  the guide's "open, unresolved tickets" is documented in
  docs/design-decisions.md.
- Tickets cannot be edited or deleted after creation (only status changes).
- A corrupted tickets.json is reported but not backed up or repaired.
- Single-user CLI with no authentication or concurrency handling.
- Future: CSV export, due dates, staff workload view, GUI.

## Pull Requests

- PR #1 — feat: ticket creation, validation and priority engine
  (Temple-Daemon; reviewed and approved by Michael)
  TODO: add PR link
- PR #2 — feat: assignment, workflow, queue, reports and persistence
  (Michael; reviewed and approved by Temple-Daemon)
  TODO: add PR link

