from campusflow.notes import add_note, get_notes
from campusflow.tickets import create_ticket, days_until_due, search_tickets
from campusflow.workflow import (
    stale_tickets,
    get_ticket,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    work_queue,
)
from campusflow.reports import (
    report_by_assignee,
    report_by_category,
    report_due,
    report_summary,
)
from campusflow.storage import export_tickets_csv, load_tickets, save_tickets


DATA_PATH = "data/tickets.json"


def display_ticket(ticket):
    print("\n--- Ticket Details ---")
    print(f"ID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}")
    due = days_until_due(ticket)
    if due is None:
        print("Due date: —")
    elif due < 0:
        print(f"Due date: {ticket['due_date']} (OVERDUE by {-due} day{'' if due == -1 else 's'})")
    elif due == 0:
        print(f"Due date: {ticket['due_date']} (due today)")
    else:
        print(f"Due date: {ticket['due_date']} (due in {due} day{'' if due == 1 else 's'})")

    notes = get_notes(ticket)
    if notes:
        print(f"Notes ({len(notes)}):")
        for note in notes:
            print(f"  - [{note['created_at']}] {note['text']}")


def list_tickets(tickets, page=1, per_page=10):
    """Print tickets one page at a time.

    WHY pagination: real helpdesks accumulate hundreds of tickets;
    printing them all makes the terminal scroll past the useful part.
    Pages are 1-indexed; an out-of-range page is clamped.
    """
    if not tickets:
        print("\nNo tickets found.")
        return

    total_pages = -(-len(tickets) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    for ticket in tickets[start:start + per_page]:
        display_ticket(ticket)

    print(f"\n[Page {page} of {total_pages}]")
    if page < total_pages:
        answer = input("Show next page? (y/N): ").strip().lower()
        if answer == "y":
            list_tickets(tickets, page + 1, per_page)


def create_new_ticket(tickets):
    title = input("Ticket title: ").strip()
    category = input(
        "Category (Network/Hardware/Software/Other): "
    ).strip().title()
    urgency = input("Urgency (low/medium/high): ").strip().lower()
    affected_users = int(input("Number of affected users: "))
    due_date = input("Due date (YYYY-MM-DD, blank for none): ").strip()

    ticket = create_ticket(
        title,
        category,
        urgency,
        affected_users,
        tickets,
        due_date=due_date,
    )

    save_tickets(tickets, DATA_PATH)
    print(f"\nTicket created successfully: {ticket['id']}")
    display_ticket(ticket)


def assign_existing_ticket(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    ticket = get_ticket(tickets, ticket_id)

    staff = input("Staff member's name: ")
    assign_ticket(ticket, staff)

    save_tickets(tickets, DATA_PATH)
    print(f"\nTicket {ticket_id} assigned successfully.")


def start_existing_ticket(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    ticket = get_ticket(tickets, ticket_id)

    start_ticket(ticket)

    save_tickets(tickets, DATA_PATH)
    print(f"\nTicket {ticket_id} is now in progress.")


def resolve_existing_ticket(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    ticket = get_ticket(tickets, ticket_id)

    resolve_ticket(ticket)

    save_tickets(tickets, DATA_PATH)
    print(f"\nTicket {ticket_id} has been resolved.")


def reopen_existing_ticket(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    ticket = get_ticket(tickets, ticket_id)

    reopen_ticket(ticket)

    save_tickets(tickets, DATA_PATH)
    print(f"\nTicket {ticket_id} has been reopened.")


def search_for_tickets(tickets):
    query = input("Search (title or category): ").strip()
    status = (
        input("Status filter (open/in_progress/resolved, blank for all): ")
        .strip()
        .lower()
        or None
    )

    results = search_tickets(tickets, query, status)

    if not results:
        print("\nNo tickets matched your search.")
        return

    print(f"\n{len(results)} ticket(s) matched:")
    for ticket in results:
        display_ticket(ticket)


def display_work_queue(tickets):
    queue = work_queue(tickets)

    if not queue:
        print("\nThe work queue is empty.")
        return

    print("\n--- Open Ticket Work Queue ---")

    for ticket in queue:
        print(
            f"{ticket['id']} | "
            f"{ticket['priority'].upper()} | "
            f"{ticket['title']} | "
            f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}"
        )


def display_reports(tickets):
    report = report_summary(tickets)

    print("\n--- CampusFlow Reports ---")
    print(f"Total tickets: {report['total']}")

    print("\nTickets by status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")

    print("\nTickets by category:")
    for row in report_by_category(tickets):
        print(f"  {row['category']}: {row['count']} ({row['share']}%)")


def export_tickets_to_csv(tickets):
    path = input("Export path (default data/tickets.csv): ").strip() or "data/tickets.csv"
    count = export_tickets_csv(tickets, path)
    print(f"\nExported {count} ticket(s) to {path}.")


def display_workload(tickets):
    rows = report_by_assignee(tickets)

    if not rows:
        print("\nNo assigned tickets — nothing to show for staff workload.")
        return

    print("\n--- Staff Workload (most loaded first) ---")
    for row in rows:
        active = row["open"] + row["in_progress"]
        print(f"\n{row['staff']}: {active} active "
              f"({row['open']} open, {row['in_progress']} in progress, "
              f"{row['resolved']} resolved)")


def display_stale_tickets(tickets):
    stale = stale_tickets(tickets)

    if not stale:
        print("\nNo stale tickets — nothing has been open for 7+ days.")
        return

    print(f"\n--- Stale Tickets (open {len(stale)}, 7+ days old) ---")
    for ticket in stale:
        print(f"\n{ticket['id']} [{ticket['priority']}] {ticket['title']}")
        print(f"   opened {ticket['created_at']} | category: {ticket['category']}")


def display_due_report(tickets):
    report = report_due(tickets)

    if report["overdue_count"] == 0 and report["due_soon_count"] == 0:
        print("\nNo overdue or due-soon tickets. Nothing urgent.")
        return

    if report["overdue"]:
        print("\n--- Overdue ---")
        for row in report["overdue"]:
            print(f"  {row['id']} [{row['priority']}] {row['title']} - "
                  f"due {row['due_date']} ({-row['days']} day(s) overdue)")

    if report["due_soon"]:
        print("\n--- Due soon (within 3 days) ---")
        for row in report["due_soon"]:
            when = "due today" if row["days"] == 0 else "due in %d day(s)" % row["days"]
            print(f"  {row['id']} [{row['priority']}] {row['title']} - {when}")


def display_unassigned(tickets):
    """CLI: tickets with no owner, oldest first."""
    report = report_unassigned(tickets)
    if report["count"] == 0:
        print("\nNo unassigned tickets. Everyone has work.")
        return
    print(f"\nUnassigned tickets ({report['count']}):")
    for row in report["tickets"]:
        print(
            f"  {row['id']} | {row['title']} | priority {row['priority']} "
            f"| {row['status']} | {row['affected_users']} affected "
            f"| created {row['created_at']}"
        )


def add_note_to_ticket(tickets):
    """CLI: append a note to a ticket by ID."""
    ticket_id = input("Ticket ID: ").strip().upper()
    ticket = get_ticket(tickets, ticket_id)

    text = input("Note text: ")
    add_note(ticket, text)

    save_tickets(tickets, DATA_PATH)
    print(f"\nNote added to ticket {ticket_id}.")


def display_menu():
    print("\n========== CAMPUSFLOW ==========")
    print("1. Create ticket")
    print("2. List all tickets")
    print("3. Search tickets")
    print("4. View work queue")
    print("5. Assign ticket")
    print("6. Start ticket")
    print("7. Resolve ticket")
    print("8. Reopen ticket")
    print("9. View reports")
    print("10. View stale tickets (open 7+ days)")
    print("11. View staff workload")
    print("12. Export tickets to CSV")
    print("13. View due report (overdue + due soon)")
    print("14. Add note to ticket")
    print("15. View unassigned tickets")
    print("16. Exit")
    print("================================")


def main():
    try:
        tickets = load_tickets(DATA_PATH)
    except (ValueError, OSError) as error:
        print(f"Could not load ticket data: {error}")
        return

    print("Welcome to CampusFlow Helpdesk!")

    while True:
        display_menu()
        choice = input("Choose an option (1-14): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)

            elif choice == "2":
                list_tickets(tickets)

            elif choice == "3":
                search_for_tickets(tickets)

            elif choice == "4":
                display_work_queue(tickets)

            elif choice == "5":
                assign_existing_ticket(tickets)

            elif choice == "6":
                start_existing_ticket(tickets)

            elif choice == "7":
                resolve_existing_ticket(tickets)

            elif choice == "8":
                reopen_existing_ticket(tickets)

            elif choice == "9":
                display_reports(tickets)

            elif choice == "10":
                display_stale_tickets(tickets)

            elif choice == "11":
                display_workload(tickets)

            elif choice == "12":
                export_tickets_to_csv(tickets)

            elif choice == "13":
                display_due_report(tickets)

            elif choice == "14":
                add_note_to_ticket(tickets)

            elif choice == "15":
                display_unassigned(tickets)

            elif choice == "16":
                print("Thanks for using CampusFlow. Goodbye!")
                break

            else:
                print("Invalid option. Choose a number from 1 to 16.")

        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()

