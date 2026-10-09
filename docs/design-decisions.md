# DESIGN DECISIONS — CampusFlow Zeus II

Team: Temple-Daemon (Partner A), Michael (Partner B)
Repo: dab00gieman/campusflow-zeus-ii
Status: FINAL — agreed by both partners on 2026-10-09.

## 1. Ticket Structure
Every ticket is a dictionary with exactly these eight fields:
- id
- title
- category
- urgency
- affected_users
- priority
- status
- assigned_to

## 2. Shared Ticket Collection
Tickets are stored in a list of dictionaries while the application runs.
Both partners use the same structure, passed explicitly between functions.

## 3. Ticket IDs
IDs follow the format T001, T002, T003, and so on. The next ID is one above
the highest existing numeric ID. IDs must remain unique after saving and
reloading.

## 4. Priority Rules
Apply these rules in order, first match wins:
1. High urgency AND at least 10 affected users: critical
2. High urgency OR at least 10 affected users: high
3. Medium urgency OR at least 3 affected users: medium
4. Otherwise: low

## 5. Status Workflow
New tickets start as open. The normal workflow is open -> in_progress ->
resolved. A ticket cannot move to in_progress unless it is assigned.
Resolved tickets must be explicitly reopened (back to open) before further
workflow changes.

## 6. Assignment
assigned_to starts as None. Assignment requires a valid ticket ID and a
non-empty staff name.

## 7. Work Queue (FINAL — team decision)
The work queue includes only tickets with status open, sorted by priority
(critical > high > medium > low), then by ascending numeric ticket ID.
In-progress tickets are excluded from the queue but remain accessible
through ticket listing/viewing and reports. We read the guide's "open,
unresolved tickets" and "open-ticket queue" as referring to the open status
defined in the workflow (open -> in_progress -> resolved).

## 8. JSON Persistence
Tickets are saved to and loaded from data/tickets.json (listed in
.gitignore). A missing file starts with an empty collection. Malformed JSON
must produce a clear error and must not silently erase data.

## 9. Integration Contracts
Function names, parameters, return values and error handling are agreed in
section 12 before anyone codes.

## 10. Testing
Python standard-library unittest. Test valid and invalid input, priority
boundaries, workflow transitions, queue sorting, reports, and
saving/reloading tickets.
Run with: python -m unittest discover -s tests -v

## 11. Module Ownership
- tickets.py (A): create_ticket, input validation, ID generation,
  calculate_priority. Tests: tests/test_tickets.py
- workflow.py (B): get_ticket, assign, start, resolve, reopen, work_queue.
  Tests: tests/test_workflow.py
- reports.py (B): report_summary. Tests: tests/test_reports.py
- storage.py (B writes, A reviews): load_tickets, save_tickets.
  Tests: tests/test_storage.py
- main.py (shared): menu loop only. No business logic there.

## 12. Function Contracts
- create_ticket(title, category, urgency, affected_users, tickets)
  -> new ticket dict, added to the list. Raises ValueError with a clear
  message on any invalid input.
- calculate_priority(urgency, affected_users) -> "critical" / "high" /
  "medium" / "low"
- next_id(tickets) -> "T001"-style next ID
- get_ticket(tickets, ticket_id) -> ticket dict, or
  ValueError("Unknown ticket ID: ...")
- assign_ticket(ticket, staff) -> updated ticket. ValueError if staff is
  blank.
- start_ticket(ticket): only from open AND assigned_to is set, else
  ValueError.
- resolve_ticket(ticket): only from in_progress, else ValueError.
- reopen_ticket(ticket): only from resolved, sets status back to open,
  else ValueError.
- work_queue(tickets) -> sorted list per section 7.
- report_summary(tickets) -> dict with total, counts by status, counts by
  priority. Works with zero tickets.
- load_tickets(path) -> list (empty if file missing; ValueError if
  malformed). save_tickets(tickets, path) -> writes JSON.

## 13. Error Handling Style
Library modules never call input() or print(). They raise ValueError with
a human-readable message. Only main.py reads input, catches errors and
prints them. This keeps all logic unit-testable without interaction.

## 14. Conventions
Urgency stored lowercase: low / medium / high.
Categories: Network, Hardware, Software, Other.
Statuses: open, in_progress, resolved.