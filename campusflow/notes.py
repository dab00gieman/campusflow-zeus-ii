"""Ticket notes: append-only context log per ticket.

WHY a separate module: notes are pure library logic over the ticket
dict — no I/O — mirroring the repo's strict library/CLI separation.
Legacy tickets created before this feature have no "notes" key;
every reader tolerates that via .get with a default.
"""
from datetime import date


def add_note(ticket, text):
    """Append a dated note to a ticket. Returns the note.

    Library rule: raises ValueError on empty or non-string text;
    the CLI handles the I/O and recovery.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Note text cannot be empty")

    note = {
        "text": text.strip(),
        "created_at": date.today().isoformat(),
    }
    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(ticket):
    """Return the ticket's notes (empty list for legacy tickets)."""
    return list(ticket.get("notes", []))
