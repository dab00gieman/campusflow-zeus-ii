import json
from pathlib import Path


def load_tickets(path):
    """Load tickets from a JSON file, returning an empty list if it is absent."""
    file_path = Path(path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid ticket data in {file_path}: {error}") from error

    if not isinstance(tickets, list) or any(
        not isinstance(ticket, dict) for ticket in tickets
    ):
        raise ValueError(f"Invalid ticket data in {file_path}: expected a list of tickets")

    return tickets


def save_tickets(tickets, path):
    """Save tickets as JSON, creating the destination directory if necessary."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=2)
        file.write("\n")
