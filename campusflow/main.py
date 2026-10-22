from campusflow.tickets import create_ticket, search_tickets
from campusflow.workflow import (
    stale_tickets,
    get_ticket,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    work_queue,
)
from campusflow.reports import report_summary, report_by_category, report_by_assignee
from campusflow.storage import load_tickets, save_tickets


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


def list_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        display_ticket(ticket)


def create_new_ticket(tickets):
    title = input("Ticket title: ").strip()
    category = input(
        "Category (Network/Hardware/Software/Other): "
    ).strip().title()
    urgency = input("Urgency (low/medium/high): ").strip().lower()
    affected_users = int(input("Number of affected users: "))

    ticket = create_ticket(
        title,
        category,
        urgency,
        affected_users,
        tickets,
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
    print("12. Exit")
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
        choice = input("Choose an option (1-12): ").strip()

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
                print("Thanks for using CampusFlow. Goodbye!")
                break

            else:
                print("Invalid option. Choose a number from 1 to 12.")

        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()

