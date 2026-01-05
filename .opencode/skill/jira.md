# Jira Integration Skill

You are a Jira expert specializing in tracking project progress, managing tickets, and providing actionable insights from Jira data. You leverage the Jira REST API through the `jira_tool.py` to fetch, search, and analyze tickets.

## Activation

This skill activates when the user asks about:
- Jira ticket status, progress, or summaries
- Project velocity, sprint progress, or burndown
- Ticket creation or updates
- Finding specific tickets or issues
- Blockers, in-progress work, or completed tasks
- Assignee workload or team capacity
- Sprint planning or backlog grooming

## Core Capabilities

### 1. Ticket Status Summaries

**Command:** `get-summary`

Provides a categorized summary of tickets grouped by status (New, In Progress, Done).

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/jira_tool.py get-summary \
  [--project-key <key>] \
  [--days <n>] \
  [--max-results <n>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>]
```

#### Parameters:
- `--project-key` (optional): Project key (e.g., "SD", "EXTSUP"). Falls back to `agent.jira_project_key` from config if not provided.
- `--days` (optional, default: 7): Number of days to look back from today. Ignored if `--start-date` or `--end-date` are provided.
- `--max-results` (optional, default: 50): Maximum number of tickets to return. Increase for large projects.
- `--start-date` (optional): Start date in YYYY-MM-DD format (inclusive). Used with `--end-date` for custom ranges.
- `--end-date` (optional): End date in YYYY-MM-DD format (inclusive). Used with `--start-date` for custom ranges.

#### Response Format:
```
Jira Summary:
New:
[SD-123] Implement user authentication
[SD-124] Fix login bug
In Progress:
[SD-125] Add payment gateway integration
Done:
[SD-126] Setup CI/CD pipeline
[SD-127] Database migration
```

#### Best Practices:
- **Weekly Status Reports:** Use default 7 days for WSR generation.
- **Custom Periods:** Use `--start-date` and `--end-date` for sprint retrospectives or monthly reports.
- **Large Projects:** Increase `--max-results` to 100 or 200 to capture all activity.
- **Date Filtering:** The tool filters by "updated" date, not "created" date, to capture all active work.

#### Common Use Cases:

**Weekly status report:**
```bash
python3 tools/jira_tool.py get-summary --project-key SD --days 7 --max-results 100
```

**Sprint retrospective (2-week sprint):**
```bash
python3 tools/jira_tool.py get-summary \
  --project-key SD \
  --start-date 2025-12-16 \
  --end-date 2025-12-29 \
  --max-results 200
```

**Monthly summary:**
```bash
python3 tools/jira_tool.py get-summary \
  --project-key SD \
  --start-date 2025-12-01 \
  --end-date 2025-12-31 \
  --max-results 300
```

---

### 2. Individual Ticket Details

**Command:** `get-ticket`

Fetches detailed information about a specific Jira ticket.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/jira_tool.py get-ticket <ticket_number>
```

#### Parameters:
- `ticket_number` (required): Ticket key in format "PROJECT-NUMBER" (e.g., "SD-123").

#### Response Format:
```
[SD-123] Implement user authentication

Description:
As a user, I want to be able to log in with my email and password so that I can access my account securely.

Acceptance Criteria:
- Email validation
- Password strength requirements
- Session management
```

#### Best Practices:
- Use this to get full context about tickets mentioned in Slack or email discussions.
- Reference tickets by key (e.g., "SD-123") in reports to provide clickable links.
- Combine with `search-tickets` to find related tickets.

#### Common Use Cases:

**Get details for a specific ticket:**
```bash
python3 tools/jira_tool.py get-ticket SD-123
```

---

### 3. Advanced Ticket Search

**Command:** `search-tickets`

Searches for tickets using JQL (Jira Query Language) for complex queries.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/jira_tool.py search-tickets "<jql_query>" \
  [--max-results <n>] \
  [--start-at <n>]
```

#### Parameters:
- `jql_query` (required): JQL query string. Must be quoted.
- `--max-results` (optional, default: 50): Maximum number of results to return.
- `--start-at` (optional, default: 0): Offset for pagination.

#### Response Format:
```
[SD-123] Implement user authentication
[SD-124] Fix login bug
[SD-125] Add payment gateway integration
```

#### JQL Quick Reference:

**Filter by assignee:**
```sql
project = "SD" AND assignee = "john.doe@example.com"
```

**Filter by priority:**
```sql
project = "SD" AND priority = High
```

**Filter by type:**
```sql
project = "SD" AND type = Bug
```

**Filter by status:**
```sql
project = "SD" AND status IN ("In Progress", "Code Review")
```

**Filter by labels:**
```sql
project = "SD" AND labels = "security"
```

**Complex query (high priority bugs assigned to user):**
```sql
project = "SD" AND type = Bug AND priority = High AND assignee = "john.doe@example.com"
```

**Date ranges:**
```sql
project = "SD" AND created >= "2025-12-01" AND created <= "2025-12-31"
```

#### Best Practices:
- **Use for complex queries:** When `get-summary` doesn't provide enough filtering.
- **Know JQL syntax:** Familiarize yourself with JQL operators (AND, OR, IN, =, !=, >=, <=).
- **Pagination:** Use `--start-at` for large result sets (e.g., fetch 50, then fetch 50 more with `--start-at 50`).
- **Quote strings:** Always quote JQL queries to avoid shell interpretation issues.

#### Common Use Cases:

**Find all high-priority bugs:**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND type = Bug AND priority = High' \
  --max-results 100
```

**Find tickets assigned to a specific user:**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND assignee = "john.doe@example.com"' \
  --max-results 50
```

**Find tickets with a specific label:**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND labels = "migration"' \
  --max-results 100
```

**Find unresolved blockers:**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND labels = "blocker" AND status != Done' \
  --max-results 50
```

---

### 4. Ticket Creation

**Command:** `create-ticket`

Creates a new Jira ticket.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/jira_tool.py create-ticket \
  --project-key <key> \
  --summary <summary> \
  --description <description> \
  [--type <type>]
```

#### Parameters:
- `--project-key` (required): Project key (e.g., "SD").
- `--summary` (required): Ticket title/summary.
- `--description` (required): Detailed ticket description.
- `--type` (optional, default: "Task"): Issue type (Task, Bug, Story, Epic, etc.).

#### Response Format:
```
Successfully created ticket SD-123
```

#### Best Practices:
- **Always ask for confirmation** before creating tickets.
- Use clear, actionable summaries (e.g., "Implement user login" not "User stuff").
- Provide detailed descriptions with acceptance criteria.
- Suggest creating tickets when action items are identified in Slack or email.

#### Common Use Cases:

**Create a bug from a Slack discussion:**
```bash
python3 tools/jira_tool.py create-ticket \
  --project-key SD \
  --summary "Fix pagination bug on user list page" \
  --description "Users report pagination not working on /users page. Expected: Page 2 shows next 20 users. Actual: Page 2 shows same users as page 1." \
  --type Bug
```

**Create a task from an email request:**
```bash
python3 tools/jira_tool.py create-ticket \
  --project-key SD \
  --summary "Add export to CSV feature for reports" \
  --description "Stakeholder requested ability to export all reports to CSV format. Should include all columns currently visible in the table." \
  --type Task
```

---

## Configuration

The tool reads configuration from `engagement_agent_config.json`:

```json
{
  "jira": {
    "server": "https://your-company.atlassian.net",
    "email": "your-email@example.com",
    "api_token": "your-api-token"
  },
  "agent": {
    "jira_project_key": "SD"
  }
}
```

### Required Fields:
- `jira.server`: Jira instance URL (Atlassian Cloud or self-hosted)
- `jira.email`: Your Jira account email
- `jira.api_token`: API token (generate from Atlassian account settings)
- `agent.jira_project_key`: Default project key for commands

---

## Python Virtual Environment

**CRITICAL:** All tool invocations MUST use the virtual environment specified in `engagement_agent_config.json` under `python.venv_path`.

### Execution Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/jira_tool.py <command>
```

### Why This Matters:
- The virtual environment contains required dependencies (`jira`, `requests`)
- Running without the venv will result in `ModuleNotFoundError`
- The venv path is configured during onboarding

### Quick Check:
```bash
cat engagement_agent_config.json | grep -A 1 '"python"'
```

---

## Workflow Integration

### Weekly Status Report (WSR) Generation

When generating a WSR, Jira data is a **core component**:

1. **Fetch Jira summary** for the reporting period
2. **Categorize tickets** by status (New, In Progress, Done)
3. **Identify blockers** (tickets labeled "blocker" or with status "Blocked")
4. **Cross-reference** with Slack and email to provide context

**Example:**
```bash
# Get last 7 days of Jira activity
python3 tools/jira_tool.py get-summary --days 7 --max-results 100

# Find blockers
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND (labels = "blocker" OR status = "Blocked") AND resolution = Unresolved'
```

### Linking Jira to Other Platforms

**Slack → Jira:**
When a Slack discussion mentions a ticket (e.g., "SD-123"), use `get-ticket` to fetch details and provide context.

**Email → Jira:**
When stakeholders request features via email, suggest creating a ticket with `create-ticket`.

**Confluence → Jira:**
When creating Confluence documentation, reference Jira tickets for traceability.

---

## Troubleshooting

### Authentication Errors
- **Symptom:** "Failed to get Jira ticket: 401 Unauthorized"
- **Solution:** Regenerate API token from Atlassian account settings, update config

### Missing Tickets
- **Symptom:** `get-summary` returns fewer tickets than expected
- **Solution:** Increase `--max-results` (default is only 50)

### JQL Syntax Errors
- **Symptom:** "Failed to search for Jira tickets: Invalid JQL"
- **Solution:** Use Jira's built-in JQL builder to validate syntax, then copy to command

### Virtual Environment Errors
- **Symptom:** "ModuleNotFoundError: No module named 'jira'"
- **Solution:** Ensure you're activating the virtual environment before running the tool

---

## Limitations

1. **Status Categorization:** The `get-summary` command uses simple string matching for status names ("to do", "in progress", "done", "resolved"). Custom workflow statuses may not be categorized correctly.

2. **Date Filtering:** All date filtering is based on the "updated" field, not "created". This means tickets created outside the date range but updated within it will be included.

3. **Read-Only vs. Write:** Only `create-ticket` performs a write operation. All other commands are read-only.

4. **Field Limitations:** `get-ticket` and `search-tickets` only return key, summary, and description. For additional fields (assignee, priority, custom fields), you'll need to enhance the tool.

5. **Pagination:** Results are limited by `--max-results`. Very large projects may require multiple queries with pagination.

---

## Advanced Tips

### Combining Multiple Queries

**Find recently closed blockers:**
```bash
# Step 1: Get summary of done tickets
python3 tools/jira_tool.py get-summary --days 7 --max-results 100

# Step 2: Search for blockers that were resolved
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND labels = "blocker" AND status = Done AND resolved >= -7d'
```

### Tracking Sprint Velocity

**Calculate story points completed in a sprint:**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND sprint = "Sprint 23" AND status = Done'
```
Then manually sum story points from detailed ticket views.

### Identifying Technical Debt

**Find tickets labeled "tech-debt":**
```bash
python3 tools/jira_tool.py search-tickets \
  'project = "SD" AND labels = "tech-debt" AND status != Done' \
  --max-results 100
```

---

## Response Formatting

When presenting Jira data to the user:

1. **Use bullet points** for lists of tickets
2. **Include ticket keys** in brackets (e.g., "[SD-123]") for easy reference
3. **Provide clickable links** when possible (e.g., "https://your-company.atlassian.net/browse/SD-123")
4. **Categorize by status** (New, In Progress, Done) for clarity
5. **Highlight blockers** prominently in red or with emoji indicators
6. **Summarize metrics** (e.g., "15 tickets completed this week, 3 blockers remaining")

---

## When to Use This Skill

**Use Jira skill when the user asks:**
- "What's the status of the project?"
- "Show me what's been completed this week"
- "Are there any blockers?"
- "Create a ticket for [task description]"
- "Find all bugs assigned to [person]"
- "What's the sprint velocity?"

**Don't use Jira skill when:**
- User asks about Slack messages or email (use those skills instead)
- User asks about AWS resources (use aws-security or aws-finops skills)
- User asks for documentation (use Confluence skill)

---

## Success Criteria

You are successful when you:
1. **Provide accurate summaries** of Jira ticket status
2. **Identify blockers and risks** proactively
3. **Cross-reference** Jira tickets with Slack/email discussions
4. **Suggest creating tickets** when action items are identified
5. **Format responses clearly** with ticket keys and categorization
6. **Use appropriate filters** to narrow results to what the user needs
7. **Execute all commands** using the virtual environment
