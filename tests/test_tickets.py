import unittest
from campusflow.tickets import calculate_priority, next_id, create_ticket

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