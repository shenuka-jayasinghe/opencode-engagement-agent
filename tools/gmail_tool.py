import argparse
import os
import base64
import datetime
from typing import List, Dict
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_FILE = "config/engagement_agent_config.json"


def get_config():
    """Loads configuration from the JSON file."""
    # Look for the config file in the current directory, then parent directories
    config_path = CONFIG_FILE
    if not os.path.exists(config_path):
        config_path = os.path.join("..", CONFIG_FILE)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Could not find {CONFIG_FILE}")
    with open(config_path, "r") as f:
        return json.load(f)


config = get_config()
G_SCOPES = config["google"]["scopes"]
G_TOKEN_FILE = os.path.expanduser(config["google"]["token_file"])


class Email:
    def __init__(
        self, id: str, subject: str, body: str, sender: str, recipients: list[str], attachments: List[Dict[str, str]]
    ):
        self.id = id
        self.subject = subject
        self.body = body
        self.sender = sender
        self.recipients = recipients
        self.attachments = attachments

    def __repr__(self):
        return (
            f"Email(id={self.id}, subject={self.subject}, sender={self.sender}, "
            f"recipients={self.recipients}, attachments={len(self.attachments)})"
        )


def get_gmail_service():
    creds = None
    if os.path.exists(G_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(G_TOKEN_FILE, G_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the credentials for the next run
            with open(G_TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        else:
            raise RuntimeError(f"'{G_TOKEN_FILE}' not found or invalid. Please run setup_auth.py to authenticate.")

    return build("gmail", "v1", credentials=creds)


SERVICE = get_gmail_service()


def parse_email_body(msg) -> Email:
    payload = msg["payload"]
    headers = payload["headers"]
    subject, sender, to_header, cc_header = "", "", "", ""

    for h in headers:
        name = h["name"].lower()
        if name == "subject":
            subject = h["value"]
        elif name == "from":
            sender = h["value"]
        elif name == "to":
            to_header = h["value"]
        elif name == "cc":
            cc_header = h["value"]

    recipient_list = [r.strip() for r in f"{to_header},{cc_header}".split(",") if r.strip()]
    email_data = {
        "id": msg["id"],
        "subject": subject,
        "body": "",
        "attachments": [],
        "recipients": recipient_list,
        "sender": sender,
    }

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                email_data["body"] = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            if part.get("filename") and "attachmentId" in part["body"]:
                email_data["attachments"].append({"filename": part["filename"], "id": part["body"]["attachmentId"]})
    elif "data" in payload["body"]:
        email_data["body"] = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    return Email(**email_data)


def create_query(
    subject: str = None, recipients: str = None, senders: str = None, start_date: str = None, end_date: str = None
):
    query_parts = []
    if subject:
        query_parts.append(f"subject:({subject})")
    if recipients:
        query_parts.append(f"to:({recipients})")
    if senders:
        query_parts.append(f"from:({senders})")
    if start_date:
        from_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        query_parts.append(f"after:{from_time.strftime('%Y/%m/%d')}")
    if end_date:
        to_time = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        query_parts.append(f"before:{to_time.strftime('%Y/%m/%d')}")
    return " ".join(query_parts)


def search_emails(query: str, max_results: int = None) -> str:
    """Searches for emails matching the query.

    Args:
        query: Gmail search query string
        max_results: Maximum number of emails to return (default: None, returns all)
    """
    try:
        messages, page_token = [], None
        while True:
            response = SERVICE.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
            messages.extend(response.get("messages", []))
            page_token = response.get("nextPageToken")

            # Break if we've reached max_results or no more pages
            if max_results and len(messages) >= max_results:
                messages = messages[:max_results]
                break
            if not page_token:
                break

        if not messages:
            return "No messages found."

        summaries = []
        for msg_summary in messages:
            msg = SERVICE.users().messages().get(userId="me", id=msg_summary["id"], format="full").execute()
            email = parse_email_body(msg)
            summaries.append(f"Subject: {email.subject}\nFrom: {email.sender}\n{email.body}\n")
        return "\n---\n".join(summaries)
    except HttpError as error:
        return f"An error occurred: {error}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gmail Tool for searching emails.")
    parser.add_argument("command", choices=["search-emails"])
    parser.add_argument("--subject", type=str, help="Keywords to search in the subject.")
    parser.add_argument("--recipients", type=str, help="Emails of recipients, comma-separated.")
    parser.add_argument("--senders", type=str, help="Emails of senders, comma-separated.")
    parser.add_argument("--start-date", type=str, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", type=str, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--max-results", type=int, help="Maximum number of emails to return (default: all)")

    args = parser.parse_args()

    if args.command == "search-emails":
        query = create_query(
            subject=args.subject,
            recipients=args.recipients,
            senders=args.senders,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        print(search_emails(query, max_results=args.max_results))
