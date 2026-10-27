import unittest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from campusflow.storage import export_tickets_csv
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, start_ticket, resolve_ticket


class TestFilteredCsvExport(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        t1 = create_ticket("Open one", "Network", "low", 1, self.tickets)
        t2 = create_ticket("In progress one", "Network", "low", 1, self.tickets)
        assign_ticket(t2, "Ada")
        start_ticket(t2)
        t3 = create_ticket("Resolved one", "Network", "low", 1, self.tickets)
        assign_ticket(t3, "Ada")
        start_ticket(t3)
        resolve_ticket(t3)

    def export(self, status=None):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "out.csv"
        count = export_tickets_csv(self.tickets, path, status=status)
        with path.open() as f:
            rows = list(csv.DictReader(f))
        return count, rows

    def test_all_exported_without_filter(self):
        count, rows = self.export()
        self.assertEqual(count, 3)

    def test_open_filter(self):
        count, rows = self.export(status="open")
        self.assertEqual(count, 1)
        self.assertEqual(rows[0]["title"], "Open one")

    def test_resolved_filter(self):
        count, rows = self.export(status="resolved")
        self.assertEqual(count, 1)
        self.assertEqual(rows[0]["title"], "Resolved one")

    def test_unknown_status_raises(self):
        with self.assertRaises(ValueError):
            self.export(status="exploded")

    def test_filter_with_no_matches_writes_header_only(self):
        self.tickets.clear()
        create_ticket("only open", "Network", "low", 1, self.tickets)
        count, rows = self.export(status="resolved")
        self.assertEqual(count, 0)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
