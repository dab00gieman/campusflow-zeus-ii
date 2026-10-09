def report_summary(tickets):
    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0
    }

    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1

    return {
        "total": len(tickets),
        "by_status": status_counts,
        "by_priority": priority_counts
    }