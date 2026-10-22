import unittest
from campusflow.reports import (
    report_by_assignee, report_summary, report_by_category)

class TestReports(unittest.TestCase):
    def test_summary_with_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "WiFi down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 10,
                "priority": "critical",
                "status": "open",
                "assigned_to": None
            },
            {
                "id": "T002",
                "title": "Broken keyboard",
                "category": "Hardware",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "resolved",
                "assigned_to": "Temple"
            }
        ]

        result = report_summary(tickets)

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["by_status"]["open"], 1)
        self.assertEqual(result["by_status"]["resolved"], 1)
        self.assertEqual(result["by_priority"]["critical"], 1)
        self.assertEqual(result["by_priority"]["low"], 1)

    def test_summary_with_no_tickets(self):
        result = report_summary([])

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["by_status"]["open"], 0)
        self.assertEqual(result["by_status"]["in_progress"], 0)
        self.assertEqual(result["by_status"]["resolved"], 0)
        self.assertEqual(result["by_priority"]["critical"], 0)
        self.assertEqual(result["by_priority"]["high"], 0)
        self.assertEqual(result["by_priority"]["medium"], 0)
        self.assertEqual(result["by_priority"]["low"], 0)

if __name__ == "__main__":
    unittest.main()

class TestReportByCategory(unittest.TestCase):
    def test_counts_and_shares(self):
        tickets = [
            {"id": "T001", "category": "Network", "status": "open"},
            {"id": "T002", "category": "Network", "status": "resolved"},
            {"id": "T003", "category": "Hardware", "status": "open"},
        ]
        rows = report_by_category(tickets)
        self.assertEqual(rows[0], {"category": "Network", "count": 2, "share": 66.7})
        self.assertEqual(rows[1]["category"], "Hardware")
        self.assertEqual(rows[1]["share"], 33.3)

    def test_ties_break_alphabetically(self):
        tickets = [
            {"id": "T001", "category": "Other", "status": "open"},
            {"id": "T002", "category": "Hardware", "status": "open"},
        ]
        self.assertEqual(
            [row["category"] for row in report_by_category(tickets)],
            ["Hardware", "Other"],
        )

    def test_empty_list_returns_no_rows(self):
        self.assertEqual(report_by_category([]), [])


class ReportByAssigneeTest(unittest.TestCase):
    def _ticket(self, staff, status, title="t"):
        return {"id": 1, "title": title, "category": "access",
                "priority": "medium", "status": status,
                "assigned_to": staff, "created_at": "2026-10-01T00:00:00"}

    def test_counts_and_active_load_ordering(self):
        rows = report_by_assignee([
            self._ticket("ada", "open"), self._ticket("ada", "resolved"),
            self._ticket("bo", "open"), self._ticket("bo", "in_progress"),
            self._ticket("bo", "in_progress"),
        ])
        self.assertEqual([r["staff"] for r in rows], ["bo", "ada"])
        self.assertEqual(rows[0]["open"], 1)
        self.assertEqual(rows[0]["in_progress"], 2)
        self.assertEqual(rows[1]["resolved"], 1)

    def test_unassigned_excluded(self):
        t = self._ticket(None, "open")
        self.assertEqual(report_by_assignee([t]), [])

    def test_ties_break_alphabetically(self):
        rows = report_by_assignee([
            self._ticket("zoe", "open"), self._ticket("ada", "open")])
        self.assertEqual([r["staff"] for r in rows], ["ada", "zoe"])
