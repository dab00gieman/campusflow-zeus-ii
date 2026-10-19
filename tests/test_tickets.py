import unittest
from campusflow.tickets import (
    calculate_priority,
    next_id,
    create_ticket,
    search_tickets,
)

class TestTickets(unittest.TestCase):
    def test_critical_priority(self):
        result = calculate_priority("high", 10)
        self.assertEqual(result, "critical")

    def test_high_priority(self):
        result = calculate_priority("high", 2)
        self.assertEqual(result, "high")

    def test_medium_priority(self):
        result = calculate_priority("medium", 3)
        self.assertEqual(result, "medium")

    def test_low_priority(self):
        result = calculate_priority("low", 2)
        self.assertEqual(result, "low")

    def test_first_ticket_id(self):
        result = next_id([])
        self.assertEqual(result, "T001")

    def test_create_ticket(self):
        tickets = []
        ticket = create_ticket("WiFi down", "Network", "high", 10, tickets)
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(len(tickets), 1)

if __name__ == "__main__":
    unittest.main()
class TestSearchTickets(unittest.TestCase):
    def _sample(self):
        tickets = []
        create_ticket("WiFi down in lab", "Network", "high", 10, tickets)
        create_ticket("Broken laptop screen", "Hardware", "medium", 1, tickets)
        create_ticket("Python venv broken", "Software", "low", 1, tickets)
        create_ticket("Projector remote missing", "Other", "low", 2, tickets)
        return tickets

    def test_matches_title_case_insensitively(self):
        results = search_tickets(self._sample(), "WIFI DOWN")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "T001")

    def test_matches_category(self):
        results = search_tickets(self._sample(), "hardware")
        self.assertEqual([t["id"] for t in results], ["T002"])

    def test_status_filter_narrows(self):
        results = search_tickets(self._sample(), "e", status="open")
        self.assertTrue(results)
        self.assertTrue(all(t["status"] == "open" for t in results))

    def test_status_filter_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            search_tickets(self._sample(), "e", status="closed")

    def test_empty_query_raises(self):
        with self.assertRaises(ValueError):
            search_tickets(self._sample(), "   ")

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(self._sample(), "zebra"), [])
