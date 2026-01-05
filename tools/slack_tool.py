import argparse
import json
import time
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_slack_client_and_channels(config_file="config/engagement_agent_config.json"):
    """Initializes and returns a Slack client and channel list."""
    with open(config_file, "r") as f:
        config = json.load(f)

    slack_config = config.get("slack", {})
    token = slack_config.get("token")

    agent_config = config.get("agent", {})
    channel_ids = agent_config.get("slack_channel_ids", [])

    if not token:
        raise ValueError("Slack token is not configured.")

    if not channel_ids:
        raise ValueError("Slack channel IDs are not configured.")

    return WebClient(token=token), channel_ids


def get_channel_name(client, channel_id):
    """Fetches and returns the name of a Slack channel."""
    try:
        response = client.conversations_info(channel=channel_id)
        if response["ok"]:
            return response["channel"]["name"]
    except SlackApiError as e:
        # Don't fail the whole script, just return the ID as name
        print(f"Error fetching channel info for {channel_id}: {e.response['error']}")
        return channel_id


def get_channel_summary(client, channel_id, start_date, end_date, limit=200):
    """Gets a summary of conversations from a channel for a given period."""
    try:
        response = client.conversations_history(
            channel=channel_id,
            latest=str(time.mktime(end_date.timetuple())),
            oldest=str(time.mktime(start_date.timetuple())),
            limit=limit,
        )
        if response["ok"]:
            messages = response.get("messages", [])
            summary = f"Summary for channel #{get_channel_name(client, channel_id)}:\n"
            for message in messages:
                user = message.get("user", "N/A")
                text = message.get("text", "").strip()
                summary += f' - User {user}: "{text}"\n'
            return summary
    except SlackApiError as e:
        return f"Error fetching channel history: {e.response['error']}"


def search_messages(client, channel_ids, query, count=20):
    """
    Searches for messages containing a query across project-specific channels.

    Args:
        client: Slack client
        channel_ids: List of channel IDs to search from the config
        query: Search query string
        count: Maximum number of results to return (default: 20)
    """
    results = []
    query_lower = query.lower()

    try:
        for channel_id in channel_ids:
            if len(results) >= count:
                break

            try:
                history_response = client.conversations_history(
                    channel=channel_id, limit=200
                )  # Limit history scan per channel
                if history_response["ok"]:
                    messages = history_response.get("messages", [])
                    for message in messages:
                        if query_lower in message.get("text", "").lower():
                            channel_name = get_channel_name(client, channel_id)
                            user = message.get("user", "N/A")
                            text = message.get("text", "").strip()
                            results.append(f'Found in #{channel_name} by {user}: "{text}"')
                            if len(results) >= count:
                                break
            except SlackApiError as e:
                channel_name = get_channel_name(client, channel_id)
                print(
                    f"Warning: Could not fetch history for channel {channel_name} ({channel_id}): {e.response['error']}"
                )
                continue

        if not results:
            return "No messages found matching the query in the configured project channels."

        return "\n".join(results)

    except SlackApiError as e:
        return f"An API error occurred: {e.response['error']}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-channel-summary command
    get_channel_summary_parser = subparsers.add_parser("get-channel-summary")
    get_channel_summary_parser.add_argument("channel_id", type=str)
    get_channel_summary_parser.add_argument("start_date", type=str)
    get_channel_summary_parser.add_argument("end_date", type=str)
    get_channel_summary_parser.add_argument(
        "--limit", type=int, default=200, help="Maximum number of messages (default: 200)"
    )

    # search-messages command
    search_messages_parser = subparsers.add_parser("search-messages")
    search_messages_parser.add_argument("query", type=str)
    search_messages_parser.add_argument("--count", type=int, default=20, help="Maximum number of results (default: 20)")

    args = parser.parse_args()
    client, channel_ids = get_slack_client_and_channels()

    if args.command == "get-channel-summary":
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        print(get_channel_summary(client, args.channel_id, start_date, end_date, limit=args.limit))
    elif args.command == "search-messages":
        print(search_messages(client, channel_ids, args.query, count=args.count))
