import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets


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
