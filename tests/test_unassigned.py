import unittest
from datetime import date, timedelta

from campusflow.reports import report_unassigned
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, resolve_ticket, start_ticket


class TestUnassignedReport(unittest.TestCase):

    def setUp(self):
        self.tickets = []

    def make(self, title="Broken laptop", days_ago=0):
        ticket = create_ticket(title, "Hardware", "low", 1, self.tickets)
        ticket["created_at"] = (date.today() - timedelta(days=days_ago)).isoformat()
        return ticket

    def test_no_tickets_is_empty_report(self):
        report = report_unassigned(self.tickets)
        self.assertEqual(report["count"], 0)

    def test_unassigned_open_ticket_listed(self):
        self.make()
        report = report_unassigned(self.tickets)
        self.assertEqual(report["count"], 1)

    def test_assigned_excluded(self):
        ticket = self.make()
        assign_ticket(ticket, "Ada")
        self.assertEqual(report_unassigned(self.tickets)["count"], 0)

    def test_resolved_excluded(self):
        ticket = self.make()
        assign_ticket(ticket, "Ada")
        start_ticket(ticket)
        resolve_ticket(ticket)
        self.assertEqual(report_unassigned(self.tickets)["count"], 0)

    def test_oldest_first(self):
        newer = self.make("new", days_ago=0)
        older = self.make("old", days_ago=5)
        rows = report_unassigned(self.tickets)["tickets"]
        self.assertEqual([r["id"] for r in rows], [older["id"], newer["id"]])

    def test_affected_users_breaks_ties_within_a_day(self):
        big = self.make("big")
        big["affected_users"] = 50
        small = self.make("small")
        rows = report_unassigned(self.tickets)["tickets"]
        self.assertEqual(rows[0]["id"], big["id"])


if __name__ == "__main__":
    unittest.main()
