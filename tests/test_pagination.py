import unittest
from io import StringIO
from unittest.mock import patch

from campusflow.main import list_tickets
from campusflow.tickets import create_ticket


def run_list(tickets, answers=None):
    out = StringIO()
    with patch("sys.stdout", out), patch(
        "builtins.input", side_effect=list(answers or [])
    ):
        list_tickets(tickets)
    return out.getvalue()


class TestPagination(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        for i in range(25):
            create_ticket(f"Ticket {i}", "Software", "low", 1, self.tickets)

    def test_first_page_shows_ten(self):
        text = run_list(self.tickets, ["n"])
        self.assertEqual(text.count("ID: "), 10)
        self.assertIn("[Page 1 of 3]", text)

    def test_next_page_advances(self):
        text = run_list(self.tickets, ["y", "n"])
        self.assertIn("[Page 1 of 3]", text)
        self.assertIn("[Page 2 of 3]", text)
        self.assertEqual(text.count("ID: "), 20)

    def test_page_clamped_to_last(self):
        out = StringIO()
        with patch("sys.stdout", out), patch(
            "builtins.input", side_effect=["n"]
        ):
            list_tickets(self.tickets, page=99)
        self.assertIn("[Page 3 of 3]", out.getvalue())

    def test_small_list_single_page(self):
        text = run_list(self.tickets[:4])
        self.assertIn("[Page 1 of 1]", text)
        self.assertEqual(text.count("ID: "), 4)

    def test_empty_list(self):
        text = run_list([])
        self.assertIn("No tickets found", text)


if __name__ == "__main__":
    unittest.main()
