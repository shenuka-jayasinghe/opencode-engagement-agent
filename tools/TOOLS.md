# Tool Usage Guide for Project Agents

This document provides detailed information about available tools, their capabilities, limitations, and best practices for effective use.

## **SECURITY: Read-Only Operations**

**CRITICAL SAFETY GUARANTEE: All tools in this directory are READ-ONLY with the exception of creating NEW documents. NO tool can:**

- ❌ **Overwrite or update existing documents** (Confluence pages, Jira tickets, etc.)
- ❌ **Send emails** (Gmail tool is search-only)
- ❌ **Send Slack messages** (Slack tool can only read messages)
- ❌ **Modify code repositories** (Bitbucket tool is read-only)

**The ONLY write operation permitted is creating NEW documents:**
- ✅ Create new Confluence pages (cannot update existing ones)
- ✅ Create new Jira tickets (cannot update existing ones)

This design ensures the agent can gather information and generate new reports without risk of accidentally modifying or deleting existing data.

## **CRITICAL: Python Virtual Environment Requirement**

**ALL Python tools in this directory MUST be executed using the virtual environment specified in `config/engagement_agent_config.json` under `python.venv_path`.**

### Execution Pattern

```bash
cd /path/to/opencode-engagement-agent && source <venv_path>/bin/activate && python3 tools/<tool_name>.py <args>
```

### Example
```bash
cd /Users/shenuka/git/daemon/gen-ai-examples/opencode-engagement-agent && source venv/bin/activate && python3 tools/jira_tool.py get-summary --project-key SD --days 7
```

### Why This Matters
- The virtual environment contains all required dependencies (jira, atlassian-python-api, google-api-python-client, slack_sdk, etc.)
- Running tools without the virtual environment will result in `ModuleNotFoundError` exceptions
- The virtual environment is created during onboarding and configured in `engagement_agent_config.json`

### Quick Check
To verify the virtual environment path:
```bash
cat config/engagement_agent_config.json | grep -A 1 '"python"'
```

---

## Available Tools

### 1. Confluence Tool (`tools/confluence_tool.py`)

**Purpose:** Interact with Confluence spaces to fetch, search, and create documentation.

**Note:** All commands shown below assume you're in the opencode-engagement-agent directory with the virtual environment activated. Prepend `cd /path/to/opencode-engagement-agent && source <venv_path>/bin/activate &&` before each command if not already activated.

#### Commands

##### `get-page-content`
Fetches the HTML content of a Confluence page by URL.

```bash
python3 tools/confluence_tool.py get-page-content <url>
```

**Parameters:**
- `url` (required): Full Confluence page URL

**Returns:** HTML content of the page

**Limitations:**
- Requires valid Confluence URL with page ID
- Returns raw HTML in storage format

**Best Practice:** Use this to fetch templates, meeting notes, or any existing documentation.

---

##### `get-page-info`
Fetches metadata about a Confluence page (parent ID, space key).

```bash
python3 tools/confluence_tool.py get-page-info <url>
```

**Parameters:**
- `url` (required): Full Confluence page URL

**Returns:** JSON with `parent_id` and `space_key`

**Best Practice:** Use before creating child pages to get the correct parent_id.

---

##### `create-page`
Creates a new Confluence page.

```bash
python3 tools/confluence_tool.py create-page --space-key <key> --title <title> --content <html_content> [--parent-id <id>]
```

**Parameters:**
- `--space-key` (required): Confluence space key (e.g., "SDRY")
- `--title` (required): Page title
- `--content` (required): HTML content in Confluence storage format
- `--parent-id` (optional): Parent page ID for creating child pages

**Limitations:**
- Content must be valid Confluence storage format HTML
- Title must be unique within the space
- **SECURITY: Cannot update or overwrite existing pages** - this tool can only create new pages

**Best Practice:** Always fetch parent page info first if creating child pages.

---

##### `search`
Searches for pages in a Confluence space using CQL (Confluence Query Language).

```bash
python3 tools/confluence_tool.py search <space_key> <query> [--limit <n>] [--start <n>] [--labels <labels>] [--modified-after <date>] [--title-only]
```

**Parameters:**
- `space_key` (required): Space to search in (e.g., "SDRY", "EXTSUP")
- `query` (required): Search query text
- `--limit` (optional, default: 10): Maximum results to return
- `--start` (optional, default: 0): Offset for pagination
- `--labels` (optional): Comma-separated labels to filter by
- `--modified-after` (optional): Date filter in YYYY-MM-DD format
- `--title-only` (optional): Search only in page titles

**Returns:** JSON array of search results

**Limitations:**
- Default limit is 10 results (increase with --limit for broader searches)
- Text search uses fuzzy matching (~), not exact match
- Label filtering requires exact label names

**Best Practices:**
- For finding recent WSRs: Use `--modified-after` with appropriate date
- For finding specific documents: Use `--title-only` with key terms
- For broad exploration: Increase `--limit` to 50 or 100
- Use pagination (--start) for large result sets

**Example:**
```bash
# Find latest WSR pages
python3 tools/confluence_tool.py search SDRY "Weekly Status Report" --title-only --modified-after 2025-12-01 --limit 20

# Find pages with specific label
python3 tools/confluence_tool.py search SDRY "architecture" --labels "design,review" --limit 30
```

---

### 2. Jira Tool (`tools/jira_tool.py`)

**Purpose:** Fetch, search, and manage Jira tickets.

#### Commands

##### `get-summary`
Gets a categorized summary of Jira tickets (New, In Progress, Done).

```bash
python3 tools/jira_tool.py get-summary [--project-key <key>] [--days <n>] [--max-results <n>] [--start-date <date>] [--end-date <date>]
```

**Parameters:**
- `--project-key` (optional): Project key (defaults to config if not provided)
- `--days` (optional, default: 7): Number of days to look back
- `--max-results` (optional, default: 50): Maximum tickets to return
- `--start-date` (optional): Start date in YYYY-MM-DD format
- `--end-date` (optional): End date in YYYY-MM-DD format

**Returns:** Formatted summary with tickets grouped by status

**Limitations:**
- Date filtering is based on "updated" field, not "created"
- Status categorization uses simple string matching (may need adjustment for custom workflows)

**Best Practices:**
- For weekly reports: Use default 7 days
- For custom periods: Use --start-date and --end-date
- For large projects: Increase --max-results to 100+

**Example:**
```bash
# Get summary for last 14 days
python3 tools/jira_tool.py get-summary --project-key SD --days 14 --max-results 100

# Get summary for specific date range
python3 tools/jira_tool.py get-summary --start-date 2025-12-01 --end-date 2025-12-15
```

---

##### `get-ticket`
Fetches detailed information about a specific Jira ticket.

```bash
python3 tools/jira_tool.py get-ticket <ticket_number>
```

**Parameters:**
- `ticket_number` (required): Ticket key (e.g., "SD-123")

**Returns:** Ticket key, summary, and description

**Best Practice:** Use this to get full context about specific tickets mentioned in discussions.

---

##### `search-tickets`
Searches for Jira tickets using JQL (Jira Query Language).

```bash
python3 tools/jira_tool.py search-tickets <jql_query> [--max-results <n>] [--start-at <n>]
```

**Parameters:**
- `jql_query` (required): JQL query string
- `--max-results` (optional, default: 50): Maximum results
- `--start-at` (optional, default: 0): Offset for pagination

**Returns:** List of ticket keys and summaries

**Limitations:**
- Requires knowledge of JQL syntax
- Returns only key and summary (use get-ticket for full details)

**Best Practices:**
- Use JQL for complex queries (assignee, labels, custom fields)
- For simple searches by date/status, prefer get-summary
- Use pagination for large result sets

**Example:**
```bash
# Find tickets assigned to specific user
python3 tools/jira_tool.py search-tickets 'project = "SD" AND assignee = "user@example.com"' --max-results 100

# Find high-priority bugs
python3 tools/jira_tool.py search-tickets 'project = "SD" AND type = Bug AND priority = High' --max-results 50
```

---

##### `create-ticket`
Creates a new Jira ticket.

```bash
python3 tools/jira_tool.py create-ticket --project-key <key> --summary <summary> --description <desc> [--type <type>]
```

**Parameters:**
- `--project-key` (required): Project key
- `--summary` (required): Ticket summary/title
- `--description` (required): Ticket description
- `--type` (optional, default: "Task"): Issue type (Task, Bug, Story, etc.)

**Returns:** Success message with created ticket key

**Note:** This tool can create new tickets but **cannot update or modify existing tickets**.

---

### 3. Slack Tool (`tools/slack_tool.py`)

**Purpose:** Fetch and search Slack messages from channels.

**SECURITY: This tool is READ-ONLY. It cannot send messages, post to channels, or modify any Slack content.**

#### Commands

##### `get-channel-summary`
Fetches messages from a specific Slack channel within a date range.

```bash
python3 tools/slack_tool.py get-channel-summary <channel_id> <start_date> <end_date> [--limit <n>]
```

**Parameters:**
- `channel_id` (required): Slack channel ID (e.g., "C012Y0LJJA2")
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `--limit` (optional, default: 200): Maximum messages to retrieve

**Returns:** Summary with channel name and message list

**Limitations:**
- Returns only message text and user ID (not user names)
- Default limit is 200 messages (may not capture all activity in busy channels)
- Does not fetch thread replies

**Best Practices:**
- For busy channels: Increase --limit to 500 or 1000
- Channel IDs are in config file under `slack_channel_ids`
- Use human-readable channel names in reports (tool provides this)

**Example:**
```bash
# Get last week's messages from a channel
python3 tools/slack_tool.py get-channel-summary C012Y0LJJA2 2025-12-15 2025-12-22 --limit 500
```

---

##### `search-messages`
Searches for messages containing a query across the project-specific Slack channels defined in the configuration.

```bash
python3 tools/slack_tool.py search-messages <query> [--count <n>]
```

**Parameters:**
- `query` (required): Search query string
- `--count` (optional, default: 20): Maximum results to return

**Returns:** List of matching messages with channel name, user, and text

**Limitations:**
- Search is limited to the channels specified in `engagement_agent_config.json`.
- May not find messages if the bot has not been added to the specified channels.
- Default is only 20 results.

**Best Practices:**
- For faster, more targeted searches, use `get-channel-summary` if you know the specific channel.
- Use specific keywords to narrow results.

**Example:**
```bash
# Search for deployment-related messages
python3 tools/slack_tool.py search-messages "deployment" --count 100
```

---

### 4. Gmail Tool (`tools/gmail_tool.py`)

**Purpose:** Search and fetch emails from Gmail.

**SECURITY: This tool is READ-ONLY. It cannot send emails, reply to emails, or modify any email content.**

#### Commands

##### `search-emails`
Searches for emails using Gmail's search syntax.

```bash
python3 tools/gmail_tool.py search-emails [--subject <text>] [--recipients <emails>] [--senders <emails>] [--start-date <date>] [--end-date <date>] [--max-results <n>]
```

**Parameters:**
- `--subject` (optional): Keywords to search in subject
- `--recipients` (optional): Recipient email addresses (comma-separated)
- `--senders` (optional): Sender email addresses (comma-separated)
- `--start-date` (optional): Start date in YYYY-MM-DD format
- `--end-date` (optional): End date in YYYY-MM-DD format
- `--max-results` (optional): Maximum emails to return (default: all matching)

**Returns:** Email summaries with subject, sender, and body

**Limitations:**
- By default, fetches ALL matching emails (can be slow)
- Email body is plain text only (HTML stripped)
- Attachments are listed but not fetched

**Best Practices:**
- Always use --max-results to limit large searches
- Combine filters to narrow results (date range + sender + subject)
- For stakeholder communications: Use recipient_emails_to_scan from config

**Example:**
```bash
# Find recent emails from stakeholders
python3 tools/gmail_tool.py search-emails --senders "ryan.williams@superdry.com" --start-date 2025-12-01 --max-results 50

# Find emails about a specific topic
python3 tools/gmail_tool.py search-emails --subject "WSR,status report" --start-date 2025-12-15 --max-results 20
```

### 5. Bitbucket Tool (`tools/bitbucket_tool.py`)

**Purpose:** Interact with Bitbucket Cloud to browse repositories, pull requests, code, and commits.

**SECURITY: This tool is READ-ONLY. It cannot create branches, merge pull requests, commit code, or modify any repository content.**

#### Commands

##### `list-workspaces`
Lists all accessible Bitbucket workspaces.

```bash
python3 tools/bitbucket_tool.py list-workspaces
```

**Returns:** List of workspace names and slugs

**Best Practice:** Use this first to discover available workspaces if you're unsure of the workspace slug.

---

##### `list-projects`
Lists all projects in a workspace.

```bash
python3 tools/bitbucket_tool.py list-projects <workspace>
```

**Parameters:**
- `workspace` (required): Workspace slug (e.g., "daemonsolutions")

**Returns:** List of project names and keys

**Best Practice:** Use the project key from this list to filter repositories.

---

##### `list-repositories`
Lists repositories in a workspace, optionally filtered by project.

```bash
python3 tools/bitbucket_tool.py list-repositories <workspace> [--project-key <key>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `--project-key` (optional): Filter by project key (e.g., "SUP")

**Returns:** List of repository names, slugs, and associated projects

**Example:**
```bash
# List all repositories in workspace
python3 tools/bitbucket_tool.py list-repositories daemonsolutions

# List repositories in specific project
python3 tools/bitbucket_tool.py list-repositories daemonsolutions --project-key SUP
```

---

##### `get-repository`
Gets detailed information about a specific repository.

```bash
python3 tools/bitbucket_tool.py get-repository <workspace> <repo_slug>
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug

**Returns:** Repository details including description, project, main branch, size, language, and URLs

**Best Practice:** Use this to understand repository structure before browsing code or PRs.

---

##### `list-pull-requests`
Lists pull requests for a repository.

```bash
python3 tools/bitbucket_tool.py list-pull-requests <workspace> <repo_slug> [--state <state>] [--limit <n>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--state` (optional, default: "OPEN"): PR state (OPEN, MERGED, DECLINED, SUPERSEDED)
- `--limit` (optional, default: 10): Maximum results

**Returns:** List of PRs with ID, title, author, creation date, state, and URL

**Example:**
```bash
# List open PRs
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions audit --state OPEN --limit 20

# List recently merged PRs
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions audit --state MERGED --limit 10
```

---

##### `get-pull-request`
Gets detailed information about a specific pull request.

```bash
python3 tools/bitbucket_tool.py get-pull-request <workspace> <repo_slug> <pr_id>
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `pr_id` (required): Pull request ID number

**Returns:** Full PR details including title, description, author, state, branches, reviewers, and participants

**Best Practice:** Use this to get full context about PRs mentioned in Slack or email.

---

##### `get-latest-pull-request`
Gets the most recent pull request from a repository.

```bash
python3 tools/bitbucket_tool.py get-latest-pull-request <workspace> <repo_slug> [--state <state>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--state` (optional, default: "OPEN"): PR state to filter by

**Returns:** Full details of the latest PR

**Best Practice:** Use this when users ask "what was the last pull request about?"

**Example:**
```bash
# Get latest open PR
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions audit

# Get latest merged PR
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions audit --state MERGED
```

---

##### `list-branches`
Lists branches in a repository.

```bash
python3 tools/bitbucket_tool.py list-branches <workspace> <repo_slug> [--limit <n>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--limit` (optional, default: 10): Maximum results

**Returns:** List of branches with last commit hash, author, and date

---

##### `get-commits`
Gets recent commits from a repository.

```bash
python3 tools/bitbucket_tool.py get-commits <workspace> <repo_slug> [--branch <name>] [--limit <n>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--branch` (optional): Branch name (defaults to main branch)
- `--limit` (optional, default: 10): Maximum results

**Returns:** List of commits with hash, author, date, and message

**Best Practice:** Use this to understand recent development activity.

**Example:**
```bash
# Get recent commits from main branch
python3 tools/bitbucket_tool.py get-commits daemonsolutions audit --limit 20

# Get commits from specific branch
python3 tools/bitbucket_tool.py get-commits daemonsolutions audit --branch develop --limit 15
```

---

##### `search-code`
Searches for code in repositories.

```bash
python3 tools/bitbucket_tool.py search-code <workspace> <query> [--repo-slug <slug>]
```

**Parameters:**
- `workspace` (required): Workspace slug
- `query` (required): Text to search for
- `--repo-slug` (optional): Limit search to specific repository

**Returns:** List of file paths and matching code snippets

**Limitations:**
- Code search may not be available on all Bitbucket plans
- Search is limited to text files
- Results are paginated (max 20 results)

**Best Practice:** Use specific search terms to narrow results. Code search works best for finding function names, configuration keys, or unique identifiers.

---

### 6. WSR Tool (`tools/wsr_tool.py`)

**Purpose:** Generate and create Weekly Status Reports (WSRs) in Confluence using a local template.

#### Command

```bash
python3 tools/wsr_tool.py --space-key <key> --title <title> --parent-id <id> --period <text> --summary <text> --achievements "<items>" --upcoming "<items>" --blockers "<items>"
```

**Parameters:**
- `--space-key` (required): Confluence space key.
- `--title` (required): Title for the new WSR page.
- `--parent-id` (required): The ID of the parent page under which the new WSR will be created.
- `--period` (required): The reporting period text (e.g., "Week 52 (2025-12-16 - 2025-12-23)").
- `--summary` (required): The executive summary text.
- `--achievements` (required): A pipe-separated string of key achievements (e.g., "Achievement 1|Achievement 2").
- `--upcoming` (required): A pipe-separated string of upcoming activities.
- `--blockers` (required): A pipe-separated string of blockers.

**Best Practice:** This tool is the standard, most efficient way to generate WSRs. It should be used in favor of manual HTML manipulation. It relies on a Jinja2 template at `tools/templates/wsr_template.html`.

---

## General Best Practices

### 1. Asking Clarifying Questions

When a user request is ambiguous, ALWAYS ask clarifying questions:

- **For searches:** "Which Confluence space should I search? (SDRY or EXTSUP?)"
- **For date ranges:** "What date range should I use? Last 7 days, or a specific period?"
- **For limits:** "How many results do you need? (default limits may be too small)"

### 2. Using Configuration

The `config/engagement_agent_config.json` file contains project-specific defaults:
- `confluence_space_key`: Default Confluence spaces to search
- `jira_project_key`: Default Jira project
- `slack_channel_ids`: Monitored Slack channels
- `recipient_emails_to_scan`: Key email addresses to monitor

Always reference these when the user doesn't specify.

### 3. Data Synthesis

Don't just fetch data - synthesize it:
- Link related information across platforms (Slack discussion → Jira ticket)
- Identify patterns and key themes
- Provide actionable summaries

### 4. Pagination and Limits

- **Start conservative:** Use default limits first
- **Expand as needed:** If results seem incomplete, increase limits
- **Use pagination:** For very large datasets, fetch in batches using --start or --start-at

### 5. Error Handling

If a tool command fails:
- Check authentication (credentials may have expired)
- Verify input format (dates, IDs, URLs)
- Try alternative approaches (e.g., search instead of direct fetch)

---

## Common Workflows

### Weekly Status Report (WSR) Creation

1. Fetch Confluence template: `get-page-content` with wsr_template_url
2. Get Jira summary: `get-summary` with appropriate date range
3. Get Slack summaries: `get-channel-summary` for each channel in config
4. Search emails: `search-emails` with recipient_emails_to_scan
5. Synthesize data and create new page: `create-page`

### Finding Latest Project Documentation

1. Search Confluence: `search` with `--modified-after` and `--title-only`
2. Sort results by modification date
3. Return top 5 most recent pages

### Tracking Project Progress

1. Get Jira summary: `get-summary` for ticket status
2. Search Slack: `search-messages` for key topics
3. Cross-reference: Link Slack discussions to Jira tickets
4. Identify blockers and risks

---

## Quick Reference

| Tool | Best For | Key Limitation | Pro Tip |
|------|----------|----------------|---------|
| Confluence search | Finding documents | Default 10 results | Use --limit 50+ for thorough searches |
| Jira get-summary | Weekly reports | Fixed 7-day window | Use --start-date/--end-date for custom ranges |
| Jira search-tickets | Complex queries | Needs JQL knowledge | For simple queries, use get-summary |
| Slack get-channel-summary | Channel activity | 200 msg limit | Increase --limit for busy channels |
| Slack search-messages | Project channel search | Configured channels only | Use specific keywords; prefer get-channel-summary |
| Gmail search-emails | Email analysis | Fetches all by default | Always use --max-results |
| Bitbucket list-pull-requests | PR overview | Default 10 results | Use --state MERGED to see recent merges |
| Bitbucket get-latest-pull-request | Find latest PR | Single result only | Most efficient for "what's the latest PR?" |
| Bitbucket get-commits | Development activity | Default 10 commits | Increase --limit for detailed history |

---

## When to Use Which Tool

**User asks for "latest WSR":**
→ Use Confluence `search` with space_key, "Weekly Status Report" query, --title-only, --modified-after

**User asks for "project status":**
→ Use Jira `get-summary` for tickets + Slack `get-channel-summary` for discussions

**User asks about "what stakeholders said":**
→ Use Gmail `search-emails` with stakeholder emails from config

**User wants to "create WSR":**
→ Use all tools in WSR workflow (see above)

**User asks about specific ticket:**
→ Use Jira `get-ticket` with ticket number

**User asks about team communications:**
→ Use Slack `get-channel-summary` for known channels, or `search-messages` for specific topics

**User asks "what was the last pull request about?":**
→ Use Bitbucket `get-latest-pull-request` with workspace and repo from config

**User asks about pull requests or code changes:**
→ Use Bitbucket `list-pull-requests` for overview, or `get-pull-request` for specific PRs

**User asks about recent development activity:**
→ Use Bitbucket `get-commits` to see recent commits and changes
