import argparse
import json
from jira import JIRA


def get_jira_client(config_file="config/engagement_agent_config.json"):
    """Initializes and returns a Jira client."""
    with open(config_file, "r") as f:
        config = json.load(f)

    jira_config = config.get("jira", {})
    server = jira_config.get("server")
    email = jira_config.get("email")
    api_token = jira_config.get("api_token")

    if not all([server, email, api_token]):
        raise ValueError("Jira server, email, or api_token is not configured.")

    return JIRA(
        server=server,
        basic_auth=(email, api_token),
    )


def get_ticket(client, ticket_number):
    """Fetches and returns a Jira ticket."""
    try:
        issue = client.issue(ticket_number)
        return f"[{issue.key}] {issue.fields.summary}\n\n{issue.fields.description}"
    except Exception as e:
        return f"Failed to get Jira ticket {ticket_number}: {e}"


def search_tickets(client, jql_query, max_results=50, start_at=0):
    """Searches for Jira tickets using a JQL query.

    Args:
        client: Jira client
        jql_query: JQL query string
        max_results: Maximum number of results to return (default: 50)
        start_at: Offset for pagination (default: 0)
    """
    try:
        tickets = client.search_issues(jql_query, maxResults=max_results, startAt=start_at)
        results = [f"[{t.key}] {t.fields.summary}" for t in tickets]
        return "\n".join(results)
    except Exception as e:
        return f"Failed to search for Jira tickets: {e}"


def create_ticket(client, project_key, summary, description, issue_type="Task"):
    """Creates a new Jira ticket."""
    try:
        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
        new_issue = client.create_issue(fields=issue_dict)
        return f"Successfully created ticket {new_issue.key}"
    except Exception as e:
        return f"Failed to create ticket: {e}"


def transition_ticket(client, ticket_number, transition_name):
    """Transitions a Jira ticket to a new status.
    
    Args:
        client: Jira client
        ticket_number: Ticket key (e.g., "SD-123")
        transition_name: Name of the transition (e.g., "Done", "Resolved", "Close", "In Progress")
    
    Returns:
        Success or error message
    """
    try:
        issue = client.issue(ticket_number)
        
        # Get available transitions for this issue
        transitions = client.transitions(issue)
        
        # Find matching transition (case-insensitive)
        transition_id = None
        available_transitions = []
        for t in transitions:
            available_transitions.append(t['name'])
            if t['name'].lower() == transition_name.lower():
                transition_id = t['id']
                break
        
        if not transition_id:
            return f"Failed to transition {ticket_number}: Transition '{transition_name}' not found.\nAvailable transitions: {', '.join(available_transitions)}"
        
        # Perform the transition
        client.transition_issue(issue, transition_id)
        return f"Successfully transitioned {ticket_number} to '{transition_name}'"
        
    except Exception as e:
        return f"Failed to transition {ticket_number}: {e}"


def close_ticket_and_subtasks(client, ticket_number, transition_name="Done"):
    """Closes a ticket and all its subtasks.
    
    Args:
        client: Jira client
        ticket_number: Parent ticket key (e.g., "SD-123")
        transition_name: Name of the transition to apply (default: "Done")
    
    Returns:
        Summary of closed tickets
    """
    try:
        # Get parent issue
        parent = client.issue(ticket_number)
        
        results = []
        failed = []
        
        # Close all subtasks first
        if hasattr(parent.fields, 'subtasks') and parent.fields.subtasks:
            for subtask in parent.fields.subtasks:
                result = transition_ticket(client, subtask.key, transition_name)
                if "Successfully" in result:
                    results.append(f"✓ {subtask.key}")
                else:
                    failed.append(f"✗ {subtask.key}: {result}")
        
        # Close parent ticket
        parent_result = transition_ticket(client, ticket_number, transition_name)
        if "Successfully" in parent_result:
            results.append(f"✓ {ticket_number} (parent)")
        else:
            failed.append(f"✗ {ticket_number}: {parent_result}")
        
        # Build summary
        summary = f"Closed {len(results)} ticket(s):\n" + "\n".join(results)
        if failed:
            summary += f"\n\nFailed to close {len(failed)} ticket(s):\n" + "\n".join(failed)
        
        return summary
        
    except Exception as e:
        return f"Failed to close tickets: {e}"


def get_summary(client, project_key, days=7, max_results=50, start_date=None, end_date=None):
    """Gets a summary of Jira tickets for the project.

    Args:
        client: Jira client
        project_key: Project key to search
        days: Number of days to look back (default: 7, ignored if start_date/end_date provided)
        max_results: Maximum number of results (default: 50)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
    """
    if start_date and end_date:
        jql_query = (
            f'project = "{project_key}" AND updated >= "{start_date}" AND updated <= "{end_date}" ORDER BY updated DESC'
        )
    elif start_date:
        jql_query = f'project = "{project_key}" AND updated >= "{start_date}" ORDER BY updated DESC'
    else:
        jql_query = f'project = "{project_key}" AND updated >= -{days}d ORDER BY updated DESC'

    tickets = client.search_issues(jql_query, maxResults=max_results)

    if not tickets:
        return "No recently updated tickets found."

    summary = {"new": [], "in_progress": [], "done": []}
    for ticket in tickets:
        status = ticket.fields.status.name.lower()
        ticket_info = f"[{ticket.key}] {ticket.fields.summary}"
        if "to do" in status:
            summary["new"].append(ticket_info)
        elif "in progress" in status:
            summary["in_progress"].append(ticket_info)
        elif "done" in status or "resolved" in status:
            summary["done"].append(ticket_info)

    summary_str = "Jira Summary:\n"
    summary_str += "New:\n" + "\n".join(summary["new"]) + "\n"
    summary_str += "In Progress:\n" + "\n".join(summary["in_progress"]) + "\n"
    summary_str += "Done:\n" + "\n".join(summary["done"]) + "\n"
    return summary_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jira Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-summary command
    get_summary_parser = subparsers.add_parser("get-summary")
    get_summary_parser.add_argument("--project-key", type=str)
    get_summary_parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    get_summary_parser.add_argument(
        "--max-results", type=int, default=50, help="Maximum number of results (default: 50)"
    )
    get_summary_parser.add_argument("--start-date", type=str, help="Start date in YYYY-MM-DD format")
    get_summary_parser.add_argument("--end-date", type=str, help="End date in YYYY-MM-DD format")

    # get-ticket command
    get_ticket_parser = subparsers.add_parser("get-ticket")
    get_ticket_parser.add_argument("ticket_number", type=str)

    # search-tickets command
    search_tickets_parser = subparsers.add_parser("search-tickets")
    search_tickets_parser.add_argument("jql_query", type=str)
    search_tickets_parser.add_argument(
        "--max-results", type=int, default=50, help="Maximum number of results (default: 50)"
    )
    search_tickets_parser.add_argument("--start-at", type=int, default=0, help="Offset for pagination (default: 0)")

    # create-ticket command
    create_ticket_parser = subparsers.add_parser("create-ticket")
    create_ticket_parser.add_argument("--project-key", type=str, required=True)
    create_ticket_parser.add_argument("--summary", type=str, required=True)
    create_ticket_parser.add_argument("--description", type=str, required=True)
    create_ticket_parser.add_argument("--type", type=str, default="Task")

    # transition-ticket command
    transition_parser = subparsers.add_parser("transition-ticket")
    transition_parser.add_argument("ticket_number", type=str, help="Ticket key (e.g., SD-123)")
    transition_parser.add_argument("transition_name", type=str, help="Transition name (e.g., Done, Resolved, Close)")

    # close-ticket-and-subtasks command
    close_parser = subparsers.add_parser("close-ticket-and-subtasks")
    close_parser.add_argument("ticket_number", type=str, help="Parent ticket key (e.g., SD-123)")
    close_parser.add_argument("--transition", type=str, default="Done", help="Transition name (default: Done)")

    args = parser.parse_args()
    client = get_jira_client()

    if args.command == "get-summary":
        project_key = args.project_key
        if not project_key:
            with open("config/engagement_agent_config.json", "r") as f:
                config = json.load(f)
            project_key = config["agent"]["jira_project_key"]
        print(
            get_summary(
                client,
                project_key,
                days=args.days,
                max_results=args.max_results,
                start_date=args.start_date,
                end_date=args.end_date,
            )
        )

    elif args.command == "get-ticket":
        print(get_ticket(client, args.ticket_number))

    elif args.command == "search-tickets":
        print(search_tickets(client, args.jql_query, max_results=args.max_results, start_at=args.start_at))

    elif args.command == "create-ticket":
        print(create_ticket(client, args.project_key, args.summary, args.description, args.type))

    elif args.command == "transition-ticket":
        print(transition_ticket(client, args.ticket_number, args.transition_name))

    elif args.command == "close-ticket-and-subtasks":
        print(close_ticket_and_subtasks(client, args.ticket_number, args.transition))
