from campusflow.tickets import days_until_due


def report_due(tickets, within_days=3, today=None):
    """Due-date report: overdue tickets and tickets due within `within_days`.

    WHY resolved tickets are excluded: the report exists to surface
    work that still needs action; a resolved ticket needs none. Rows
    carry the days offset (negative = overdue) so the CLI can phrase
    each line. Mirrors the design shipped in campusflow-hades-ii #26.
    """
    rows = []
    for ticket in tickets:
        if ticket["status"] == "resolved":
            continue
        days = days_until_due(ticket, today=today)
        if days is None:
            continue
        rows.append({
            "id": ticket["id"],
            "title": ticket["title"],
            "priority": ticket["priority"],
            "status": ticket["status"],
            "due_date": ticket["due_date"],
            "days": days,
        })

    overdue = sorted(
        (row for row in rows if row["days"] < 0), key=lambda row: row["days"]
    )
    due_soon = sorted(
        (row for row in rows if 0 <= row["days"] <= within_days),
        key=lambda row: row["days"],
    )

    return {
        "overdue": overdue,
        "due_soon": due_soon,
        "overdue_count": len(overdue),
        "due_soon_count": len(due_soon),
    }


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


def report_by_assignee(tickets):
    """Per-staff workload: status counts for every assigned ticket.

    Rows are sorted by active load (open + in_progress) so the most
    loaded staff member is first. Unassigned tickets are excluded —
    the work queue is where those live.
    """
    load = {}
    for ticket in tickets:
        staff = ticket.get("assigned_to")
        if not staff:
            continue
        row = load.setdefault(
            staff, {"staff": staff, "open": 0, "in_progress": 0, "resolved": 0})
        if ticket["status"] in row:
            row[ticket["status"]] += 1
    rows = list(load.values())
    rows.sort(key=lambda row: (-(row["open"] + row["in_progress"]), row["staff"]))
    return rows

def report_unassigned(tickets):
    """Unassigned work report: actionable tickets nobody owns.

    WHY a report and not a filter: unassigned + unresolved tickets are
    exactly the ones that silently fall through the cracks; the view
    exists to make them impossible to miss. Oldest first, most-affected
    first within a day.
    """
    rows = []
    for ticket in tickets:
        if ticket["status"] == "resolved" or ticket.get("assigned_to"):
            continue
        rows.append(
            {
                "id": ticket["id"],
                "title": ticket["title"],
                "priority": ticket["priority"],
                "status": ticket["status"],
                "created_at": ticket["created_at"],
                "affected_users": ticket["affected_users"],
            }
        )
    rows.sort(
        key=lambda row: (row["created_at"], -row["affected_users"])
    )
    return {"count": len(rows), "tickets": rows}
