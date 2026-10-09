def get_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise ValueError(f"Unknown ticket ID: {ticket_id}")

def assign_ticket(ticket, staff):
    if not staff or not staff.strip():
        raise ValueError("Staff name cannot be empty")
    ticket["assigned_to"] = staff.strip()
    return ticket

def start_ticket(ticket):
    if ticket["status"] != "open":
        raise ValueError("Only open tickets can be started")
    if not ticket["assigned_to"]:
        raise ValueError("Ticket must be assigned before starting")
    ticket["status"] = "in_progress"
    return ticket

def resolve_ticket(ticket):
    if ticket["status"] != "in_progress":
        raise ValueError("Only in-progress tickets can be resolved")
    ticket["status"] = "resolved"
    return ticket


def reopen_ticket(ticket):
    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened")
    ticket["status"] = "open"
    return ticket

def work_queue(tickets):
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3
    }

    queue = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(
        queue,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:])
        )
    )