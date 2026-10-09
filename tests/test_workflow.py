import unittest
from campusflow.workflow import (
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