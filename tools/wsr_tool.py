import argparse
import os
import re
from jinja2 import Environment, FileSystemLoader
from confluence_tool import get_confluence_client, create_confluence_page


def link_jira_tickets(text, jira_base_url="https://your-domain.atlassian.net"):
    """
    Converts plain text Jira ticket references (e.g., PROJ-1234) to HTML links.
    Only converts if the ticket reference is not already within an <a> tag.

    Args:
        text: The text containing potential Jira ticket references
        jira_base_url: Base URL for the Jira instance

    Returns:
        Text with Jira tickets converted to links
    """
    if not text:
        return text

    # First, protect existing links by temporarily replacing them
    # This prevents double-linking already-linked tickets
    protected_links = []
    link_pattern = r'<a\s+href="[^"]*">[^<]*</a>'

    def protect_link(match):
        index = len(protected_links)
        protected_links.append(match.group(0))
        return f"__PROTECTED_LINK_{index}__"

    # Replace all existing links with placeholders
    text = re.sub(link_pattern, protect_link, text)

    # Now link any unlinked Jira tickets
    ticket_pattern = r"\b([A-Z]+-\d+)\b"

    def replace_ticket(match):
        ticket = match.group(1)
        return f'<a href="{jira_base_url}/browse/{ticket}">{ticket}</a>'

    text = re.sub(ticket_pattern, replace_ticket, text)

    # Restore protected links
    for i, link in enumerate(protected_links):
        text = text.replace(f"__PROTECTED_LINK_{i}__", link)

    return text


def generate_wsr(
    space_key,
    title,
    parent_id,
    reporting_period,
    executive_summary,
    achievements,
    upcoming,
    blockers,
    client,
    programme,
    status_color,
    template_dir="tools/templates",
    template_file="wsr_full_template.html",
):
    try:
        # 1. Setup Jinja2 environment
        # Use absolute path for template_dir if not provided
        if not os.path.isabs(template_dir):
            template_dir = os.path.join(os.getcwd(), template_dir)

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)

        # 2. Process all text to link Jira tickets
        executive_summary = link_jira_tickets(executive_summary)
        achievements = [link_jira_tickets(item) for item in achievements]
        upcoming = [link_jira_tickets(item) for item in upcoming]
        blockers = [link_jira_tickets(item) for item in blockers]

        # 3. Render the template with data
        html_content = template.render(
            client=client,
            programme=programme,
            status_color=status_color,
            period=reporting_period,
            executive_summary=executive_summary,
            achievements=achievements,
            upcoming_activities=upcoming,
            blockers=blockers,
        )

        # 4. Create the page in Confluence
        client = get_confluence_client()
        result = create_confluence_page(client, space_key, title, html_content, parent_id)

        # Construct the page URL
        if result and "id" in result:
            page_id = result["id"]
            # Get the base URL from the client
            base_url = client.url.rstrip("/")
            page_url = f"{base_url}/wiki/spaces/{space_key}/pages/{page_id}/{title.replace(' ', '+')}"
            print(f"Successfully created WSR page: '{title}' in space '{space_key}'")
            print(f"Page URL: {page_url}")
        else:
            print(f"Successfully created WSR page: '{title}' in space '{space_key}'")
        return True

    except Exception as e:
        print(f"Error generating WSR: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WSR Generator Tool")
    parser.add_argument("--space-key", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--parent-id", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--summary", required=True)
    # Lists are passed as pipe-separated strings for simplicity in CLI: "Item 1|Item 2"
    parser.add_argument("--achievements", required=True)
    parser.add_argument("--upcoming", required=True)
    parser.add_argument("--blockers", required=True)
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--programme", required=True, help="Programme name")
    parser.add_argument("--status-color", required=True, help="Engagement status color (Green, Amber, Red)")

    args = parser.parse_args()

    generate_wsr(
        args.space_key,
        args.title,
        args.parent_id,
        args.period,
        args.summary,
        args.achievements.split("|"),
        args.upcoming.split("|"),
        args.blockers.split("|"),
        client=args.client,
        programme=args.programme,
        status_color=args.status_color,
    )
