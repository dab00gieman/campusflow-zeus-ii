import unittest
from datetime import date

from campusflow.notes import add_note, get_notes
from campusflow.tickets import create_ticket


def make_ticket():
    return create_ticket(
        "VPN broken", "Network", "high", 12, []
    )


class TestNotes(unittest.TestCase):

    def test_add_note_appends_dated_note(self):
        ticket = make_ticket()
        note = add_note(ticket, "Escalated to network team")
        self.assertEqual(note["text"], "Escalated to network team")
        self.assertEqual(note["created_at"], date.today().isoformat())
        self.assertEqual(get_notes(ticket), [note])

    def test_empty_text_raises(self):
        ticket = make_ticket()
        with self.assertRaises(ValueError):
            add_note(ticket, "   ")

    def test_non_string_text_raises(self):
        ticket = make_ticket()
        with self.assertRaises(ValueError):
            add_note(ticket, 42)

    def test_legacy_ticket_without_notes_key(self):
        legacy = {"id": "T001", "title": "old"}
        self.assertEqual(get_notes(legacy), [])

    def test_multiple_notes_preserve_order(self):
        ticket = make_ticket()
        first = add_note(ticket, "first")
        second = add_note(ticket, "second")
        self.assertEqual(get_notes(ticket), [first, second])

    def test_get_notes_returns_copy(self):
        ticket = make_ticket()
        add_note(ticket, "only")
        notes = get_notes(ticket)
        notes.clear()
        self.assertEqual(len(get_notes(ticket)), 1)

    def test_note_text_is_stripped(self):
        ticket = make_ticket()
        note = add_note(ticket, "  padded  ")
        self.assertEqual(note["text"], "padded")


if __name__ == "__main__":
    unittest.main()
