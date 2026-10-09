from campusflow.tickets import create_ticket
from campusflow.workflow import (
    get_ticket,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    work_queue,
)
from campusflow.reports import report_summary
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


def display_menu():
    print("\n========== CAMPUSFLOW ==========")
    print("1. Create ticket")
    print("2. List all tickets")
    print("3. View work queue")
    print("4. Assign ticket")
    print("5. Start ticket")
    print("6. Resolve ticket")
    print("7. Reopen ticket")
    print("8. View reports")
    print("9. Exit")
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
        choice = input("Choose an option (1-9): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)

            elif choice == "2":
                list_tickets(tickets)

            elif choice == "3":
                display_work_queue(tickets)

            elif choice == "4":
                assign_existing_ticket(tickets)

            elif choice == "5":
                start_existing_ticket(tickets)

            elif choice == "6":
                resolve_existing_ticket(tickets)

            elif choice == "7":
                reopen_existing_ticket(tickets)

            elif choice == "8":
                display_reports(tickets)

            elif choice == "9":
                print("Thanks for using CampusFlow. Goodbye!")
                break

            else:
                print("Invalid option. Choose a number from 1 to 9.")

        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()

