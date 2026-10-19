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


def report_by_category(tickets):
    """Count tickets per category, highest first, with share of total."""
    counts = {}
    for ticket in tickets:
        category = ticket["category"]
        counts[category] = counts.get(category, 0) + 1

    total = len(tickets)
    rows = [
        {
            "category": category,
            "count": count,
            "share": round(count / total * 100, 1) if total else 0.0,
        }
        for category, count in counts.items()
    ]
    rows.sort(key=lambda row: (-row["count"], row["category"]))
    return rows
