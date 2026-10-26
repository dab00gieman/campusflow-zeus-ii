import json
import os
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import export_tickets_csv, load_tickets, save_tickets


class TestStorage(unittest.TestCase):
    def test_load_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

            self.assertEqual(load_tickets(path), [])

    def test_save_and_load_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "WiFi down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 10,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "tickets.json"

            save_tickets(tickets, path)

            self.assertEqual(load_tickets(path), tickets)

    def test_load_malformed_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid ticket data"):
                load_tickets(path)

    def test_load_non_list_data_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(json.dumps({"id": "T001"}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected a list of tickets"):
                load_tickets(path)


if __name__ == "__main__":
    unittest.main()

class TestAtomicSave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "data", "tickets.json")
        self.addCleanup(self.tmp.cleanup)

    def test_save_leaves_no_temp_file(self):
        save_tickets([], self.path)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_overwrite_keeps_data_valid(self):
        first = [{"id": "T001", "title": "old", "status": "open"}]
        save_tickets(first, self.path)
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])

    def test_roundtrip_preserves_every_field(self):
        ticket = {
            "id": "T001",
            "title": "WiFi down",
            "category": "Network",
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        }
        save_tickets([ticket], self.path)
        self.assertEqual(load_tickets(self.path)[0]["title"], "WiFi down")


class ExportTicketsCsvTest(unittest.TestCase):
    TICKET = {"id": 7, "title": "Wireless, room 4", "category": "network",
              "priority": "high", "status": "open", "assigned_to": "ada",
              "created_at": "2026-10-20T09:00:00", "extra_key": "ignored"}

    def test_round_trip_and_quoting(self):
        import csv as csv_mod
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "out.csv"
            count = export_tickets_csv([self.TICKET], path)
            self.assertEqual(count, 1)
            with path.open(encoding="utf-8", newline="") as file:
                rows = list(csv_mod.DictReader(file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "Wireless, room 4")
            self.assertEqual(rows[0]["id"], "7")
            self.assertNotIn("extra_key", rows[0])

    def test_export_includes_due_date_column(self):
        tickets = [{"id": "T001", "title": "t", "category": "Other", "priority": "low",
                    "status": "open", "assigned_to": None, "created_at": "2026-10-26",
                    "due_date": "2026-11-01"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            export_tickets_csv(tickets, path)
            with open(path, encoding="utf-8") as f:
                header = f.readline().strip().split(",")
        self.assertIn("due_date", header)

    def test_empty_export_writes_header_only(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sub" / "out.csv"
            self.assertEqual(export_tickets_csv([], path), 0)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines(),
                             ["id,title,category,priority,status,assigned_to,created_at,due_date"])
