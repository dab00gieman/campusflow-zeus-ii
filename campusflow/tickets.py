def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def next_id(tickets):
    if not tickets:
        return "T001"

    highest_id = max(
        int(ticket["id"][1:])
        for ticket in tickets
    )

    return f"T{highest_id + 1:03d}"


def create_ticket(title, category, urgency, affected_users, tickets):
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title cannot be empty")

    if category not in ["Network", "Hardware", "Software", "Other"]:
        raise ValueError("Invalid category")

    if urgency not in ["low", "medium", "high"]:
        raise ValueError("Invalid urgency")

    if (
        not isinstance(affected_users, int)
        or isinstance(affected_users, bool)
        or affected_users < 1
    ):
        raise ValueError("Affected users must be a positive integer")

    ticket_id = next_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": title.strip(),
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None
    }

    tickets.append(ticket)

    return ticket

