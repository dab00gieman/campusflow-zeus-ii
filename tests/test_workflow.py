from datetime import date
import unittest
from campusflow.workflow import (
    stale_tickets,
    get_ticket,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    work_queue
)

class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.ticket = {
            "id": "T001",
            "title": "WiFi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 10,
            "priority": "critical",
            "status": "open",
            "assigned_to": None
        }
        self.tickets = [self.ticket]

    def test_get_ticket(self):
        result = get_ticket(self.tickets, "T001")
        self.assertEqual(result["title"], "WiFi down")

    def test_unknown_ticket(self):
        with self.assertRaises(ValueError):
            get_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        assign_ticket(self.ticket, "Temple")
        self.assertEqual(self.ticket["assigned_to"], "Temple")

    def test_reject_empty_staff(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.ticket, " ")

    def test_start_ticket(self):
        assign_ticket(self.ticket, "Temple")
        start_ticket(self.ticket)
        self.assertEqual(self.ticket["status"], "in_progress")

    def test_cannot_start_unassigned_ticket(self):
        with self.assertRaises(ValueError):
            start_ticket(self.ticket)

    def test_resolve_ticket(self):
        assign_ticket(self.ticket, "Temple")
        start_ticket(self.ticket)
        resolve_ticket(self.ticket)
        self.assertEqual(self.ticket["status"], "resolved")

    def test_reopen_ticket(self):
        assign_ticket(self.ticket, "Temple")
        start_ticket(self.ticket)
        resolve_ticket(self.ticket)
        reopen_ticket(self.ticket)
        self.assertEqual(self.ticket["status"], "open")

    def test_work_queue(self):
        result = work_queue(self.tickets)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "T001")

    def test_work_queue_excludes_in_progress(self):
        assign_ticket(self.ticket, "Temple")
        start_ticket(self.ticket)
        self.assertEqual(work_queue(self.tickets), [])

if __name__ == "__main__":
    unittest.main()

class TestStaleTickets(unittest.TestCase):
    def _ticket(self, **over):
        base = {"id": "T001", "status": "open", "created_at": "2026-10-01"}
        base.update(over)
        return base

    def test_old_open_ticket_is_stale(self):
        stale = stale_tickets([self._ticket()], 7, today=date(2026, 10, 19))
        self.assertEqual([t["id"] for t in stale], ["T001"])

    def test_resolved_old_ticket_is_not_stale(self):
        stale = stale_tickets([self._ticket(status="resolved")], 7, today=date(2026, 10, 19))
        self.assertEqual(stale, [])

    def test_fresh_ticket_is_not_stale(self):
        stale = stale_tickets([self._ticket(created_at="2026-10-18")], 7, today=date(2026, 10, 19))
        self.assertEqual(stale, [])

    def test_tickets_without_date_are_never_stale(self):
        ticket = self._ticket()
        del ticket["created_at"]
        stale = stale_tickets([ticket], 7, today=date(2026, 10, 19))
        self.assertEqual(stale, [])

    def test_oldest_first_ordering(self):
        tickets = [self._ticket(id="T002", created_at="2026-09-20"),
                   self._ticket(id="T001", created_at="2026-10-05")]
        stale = stale_tickets(tickets, 7, today=date(2026, 10, 19))
        self.assertEqual([t["id"] for t in stale], ["T002", "T001"])
