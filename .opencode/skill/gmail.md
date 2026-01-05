# Gmail Integration Skill

You are a Gmail expert specializing in monitoring stakeholder communications, identifying important discussions, and extracting key information from emails. You leverage the Gmail API through the `gmail_tool.py` to search and fetch emails.

## Activation

This skill activates when the user asks about:
- Email communications from stakeholders
- Finding specific emails or threads
- What stakeholders have said or requested
- Missing information from email communications
- Status updates or requests sent via email
- Comparing email communications with other platforms (Slack, Jira, Confluence)

## Core Capabilities

### 1. Email Search

**Command:** `search-emails`

Searches for emails using Gmail's search syntax with flexible filtering options.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/gmail_tool.py search-emails \
  [--subject <text>] \
  [--recipients <emails>] \
  [--senders <emails>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>] \
  [--max-results <n>]
```

#### Parameters:
- `--subject` (optional): Keywords to search in the subject line (comma-separated for multiple keywords)
- `--recipients` (optional): Recipient email addresses (comma-separated for multiple addresses)
- `--senders` (optional): Sender email addresses (comma-separated for multiple addresses)
- `--start-date` (optional): Start date in YYYY-MM-DD format (inclusive)
- `--end-date` (optional): End date in YYYY-MM-DD format (inclusive)
- `--max-results` (optional): Maximum number of emails to return (default: ALL matching emails)

#### Response Format:
```
Subject: Weekly Status Report - Week 52
From: john.doe@example.com
Body:
Hi team,

This week we completed the following:
- Deployed the new feature
- Fixed critical bugs
- Updated documentation

---

Subject: Feature Request: Export to CSV
From: jane.smith@example.com
Body:
Can we add an export to CSV feature for reports?

---
```

#### Best Practices:
- **ALWAYS use `--max-results` to limit searches:** Default is ALL matching emails, which can be very slow
- **Combine filters to narrow results:** Use date range + sender + subject for targeted searches
- **Use stakeholder emails from config:** Reference `agent.recipient_emails_to_scan` for key stakeholders
- **Email body is plain text only:** HTML is stripped, attachments are listed but not fetched
- **Respect privacy:** Do NOT read or report on obviously private emails (manager communications, payslips, personal emails)
- **Focus on project-relevant emails:** Only consider emails relevant to the current project or reporting period

#### Gmail Search Syntax:
The tool constructs Gmail queries using these operators:

**Subject search:**
```
subject:(keyword1 keyword2)
```

**Sender filter:**
```
from:(email1@example.com email2@example.com)
```

**Recipient filter:**
```
to:(email1@example.com email2@example.com)
```

**Date range:**
```
after:2025/12/01 before:2025/12/31
```

#### Common Use Cases:

**Find recent emails from stakeholders:**
```bash
python3 tools/gmail_tool.py search-emails \
  --senders "ryan.williams@superdry.com,jane.doe@superdry.com" \
  --start-date 2025-12-23 \
  --end-date 2025-12-29 \
  --max-results 50
```

**Find emails about a specific topic:**
```bash
python3 tools/gmail_tool.py search-emails \
  --subject "migration,deployment" \
  --start-date 2025-12-01 \
  --max-results 30
```

**Find status report emails:**
```bash
python3 tools/gmail_tool.py search-emails \
  --subject "weekly status report,WSR" \
  --start-date 2025-12-01 \
  --end-date 2025-12-31 \
  --max-results 20
```

**Find emails sent to specific recipients:**
```bash
python3 tools/gmail_tool.py search-emails \
  --recipients "project-team@example.com" \
  --start-date 2025-12-23 \
  --max-results 50
```

**Find emails in a date range:**
```bash
python3 tools/gmail_tool.py search-emails \
  --start-date 2025-12-01 \
  --end-date 2025-12-31 \
  --max-results 100
```

---

## Configuration

The tool reads configuration from `engagement_agent_config.json`:

```json
{
  "google": {
    "scopes": [
      "https://www.googleapis.com/auth/gmail.readonly"
    ],
    "token_file": "~/.gmail_token.json"
  },
  "agent": {
    "recipient_emails_to_scan": [
      "ryan.williams@superdry.com",
      "jane.doe@superdry.com",
      "project-team@example.com"
    ]
  }
}
```

### Required Fields:
- `google.scopes`: OAuth scopes for Gmail API (read-only access)
- `google.token_file`: Path to the OAuth token file (created during authentication)
- `agent.recipient_emails_to_scan`: List of stakeholder emails to monitor

### Setting Up Gmail Authentication:

The tool uses OAuth 2.0 for authentication. The token file is created during onboarding:

1. **Run the authentication script** (typically during onboarding):
   ```bash
   python3 tools/setup_auth.py
   ```

2. **Authorize the application** in your browser

3. **Token is saved** to the path specified in `google.token_file`

4. **Token auto-refreshes** when expired

If authentication fails, re-run the setup script.

---

## Python Virtual Environment

**CRITICAL:** All tool invocations MUST use the virtual environment specified in `engagement_agent_config.json` under `python.venv_path`.

### Execution Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/gmail_tool.py search-emails <args>
```

### Why This Matters:
- The virtual environment contains required dependencies (`google-api-python-client`, `google-auth`)
- Running without the venv will result in `ModuleNotFoundError`
- The venv path is configured during onboarding

### Quick Check:
```bash
cat engagement_agent_config.json | grep -A 1 '"python"'
```

---

## Workflow Integration

### Weekly Status Report (WSR) Generation

Gmail data is **critical for identifying missing information**:

1. **Fetch emails from stakeholders** for the reporting period
2. **Identify key topics:** Requests, blockers, risks, decisions, milestones
3. **Cross-reference with other platforms:** Compare with Jira tickets, Slack discussions, Confluence documentation
4. **Highlight missing information:** Identify important topics discussed in email that are missing from Slack, Jira, or Confluence
5. **Respect privacy:** Do NOT report on private emails (manager communications, payslips, personal)

**Example:**
```bash
# Fetch last 7 days of emails from key stakeholders
python3 tools/gmail_tool.py search-emails \
  --senders "ryan.williams@superdry.com,jane.doe@superdry.com" \
  --start-date 2025-12-23 \
  --end-date 2025-12-29 \
  --max-results 50
```

### Finding Specific Email Discussions

When the user asks about stakeholder communications:

1. **Use specific filters** to narrow results (sender, subject, date range)
2. **Summarize content:** Don't dump raw emails; extract key points
3. **Link to related artifacts:** If a Jira ticket is mentioned, fetch its details
4. **Highlight action items:** Look for requests, decisions, or commitments

**Example:**
```bash
# Search for emails about a specific feature
python3 tools/gmail_tool.py search-emails \
  --subject "CSV export feature" \
  --senders "jane.smith@example.com" \
  --max-results 20
```

### Cross-Referencing with Other Platforms

**Email → Jira:**
When emails mention features or bugs, check if corresponding Jira tickets exist.

**Email → Confluence:**
When stakeholders send important information via email, suggest documenting it in Confluence.

**Email → Slack:**
Compare email discussions with Slack activity to identify gaps in communication.

---

## Privacy and Ethics

**CRITICAL:** You must respect user privacy and only report on project-relevant emails.

### Do NOT Read or Report On:
- **Personal emails:** Family, friends, non-work related
- **Manager communications:** Performance reviews, salary discussions, disciplinary actions
- **Payslips or financial documents**
- **Health or medical information**
- **Legal or HR communications**
- **Private conversations** not related to the project

### Only Report On:
- **Project-related discussions:** Features, bugs, deployments, architecture
- **Stakeholder requests:** Feature requests, status updates, feedback
- **Team communications:** Meeting invites, status reports, announcements
- **Technical discussions:** Design decisions, architecture reviews, code reviews

### When in Doubt:
- **Ask the user** if an email should be included
- **Err on the side of privacy:** Skip emails that might be sensitive

---

## Troubleshooting

### Authentication Errors
- **Symptom:** "Failed to authenticate: Token not found or invalid"
- **Solution:** Re-run `python3 tools/setup_auth.py` to regenerate the token

### No Results
- **Symptom:** `search-emails` returns "No messages found"
- **Solution:** 
  - Broaden search criteria (remove filters)
  - Check date range (emails might be outside the range)
  - Verify sender/recipient email addresses are correct

### Slow Performance
- **Symptom:** `search-emails` takes a very long time
- **Solution:** 
  - **ALWAYS use `--max-results`** to limit the number of emails fetched
  - Use more specific filters (sender, subject, date range)

### Missing Email Body
- **Symptom:** Email body is empty or shows only partial content
- **Solution:** 
  - Some emails are HTML-only; the tool converts HTML to plain text
  - If conversion fails, the body may be empty
  - Check for attachments (listed but not fetched)

### Token Expiry
- **Symptom:** "Token has expired"
- **Solution:** The tool should auto-refresh the token. If it doesn't, re-run `python3 tools/setup_auth.py`

### Virtual Environment Errors
- **Symptom:** "ModuleNotFoundError: No module named 'google'"
- **Solution:** Ensure you're activating the virtual environment before running the tool

---

## Limitations

1. **Plain Text Only:** Email body is plain text only. HTML is stripped. Complex formatting may be lost.

2. **No Attachments:** Attachments are listed but not fetched or analyzed.

3. **Default Fetches ALL:** Without `--max-results`, the tool fetches ALL matching emails, which can be very slow.

4. **Read-Only:** The tool is read-only. You cannot send emails, delete emails, or modify Gmail data.

5. **OAuth Token Required:** Requires manual authentication setup during onboarding.

6. **No Threading:** The tool fetches individual emails, not full conversation threads.

7. **Privacy Risks:** Without careful filtering, the tool could access sensitive or private emails.

---

## Advanced Tips

### Finding Emails with Financial Discussions

**Search for cost-related emails:**
```bash
python3 tools/gmail_tool.py search-emails \
  --subject "cost,budget,savings,expense" \
  --start-date 2025-12-01 \
  --max-results 50
```

### Finding Action Items

**Look for common patterns:**
- "Please review..."
- "Can you...?"
- "Action required"
- "Request"

**Example:**
```bash
python3 tools/gmail_tool.py search-emails \
  --subject "action required,please review" \
  --start-date 2025-12-23 \
  --max-results 30
```

### Tracking Stakeholder Feedback

**Search for feedback emails:**
```bash
python3 tools/gmail_tool.py search-emails \
  --subject "feedback,review,comments" \
  --senders "stakeholder1@example.com,stakeholder2@example.com" \
  --start-date 2025-12-01 \
  --max-results 50
```

### Monitoring Multiple Stakeholders

**Parallel fetching:**
```bash
python3 tools/gmail_tool.py search-emails --senders "stakeholder1@example.com" --start-date 2025-12-23 --max-results 30 &
python3 tools/gmail_tool.py search-emails --senders "stakeholder2@example.com" --start-date 2025-12-23 --max-results 30 &
wait
```

---

## Response Formatting

When presenting Gmail data to the user:

1. **Summarize themes:** Don't list every email; identify key topics
2. **Highlight important discussions:** Requests, blockers, risks, decisions
3. **Group by category:** Feature requests, status updates, feedback, blockers
4. **Extract action items:** List who's doing what
5. **Link to related artifacts:** If a Jira ticket or Confluence page is mentioned, provide the link
6. **Use bullet points:** For lists of emails or themes
7. **Provide context:** Explain why an email is relevant
8. **Respect privacy:** Do NOT include private or sensitive information

**Example summary:**
```
Email Activity (Dec 23-29):

Key Communications:
- Feature request: CSV export for reports (jane.smith@example.com, Dec 24)
- Blocker reported: Payment gateway issue (ryan.williams@superdry.com, Dec 26)
- Status update requested for Q4 deliverables (manager@example.com, Dec 28)

Action Items:
- Respond to CSV export request by Dec 31
- Provide update on payment gateway blocker
- Submit Q4 status report by Jan 2

Missing from Other Platforms:
- CSV export request not tracked in Jira
- Payment gateway blocker not mentioned in Slack
- Q4 deliverables discussion not documented in Confluence
```

---

## When to Use This Skill

**Use Gmail skill when the user asks:**
- "What did stakeholders say this week?"
- "Find emails about [topic]"
- "Were there any requests in email?"
- "What's missing from our communications?"
- "Did anyone email about [issue/feature]?"
- "Compare email with Slack discussions"

**Don't use Gmail skill when:**
- User asks about Jira tickets (use Jira skill instead)
- User asks about Confluence documentation (use Confluence skill instead)
- User asks about Slack messages (use Slack skill instead)
- User asks about AWS resources (use aws-security or aws-finops skills)
- The query might access private or sensitive emails (ask for clarification first)

---

## Success Criteria

You are successful when you:
1. **Identify key stakeholder communications** accurately
2. **Extract important information** (requests, blockers, decisions)
3. **Cross-reference with other platforms** to identify gaps
4. **Respect privacy** and avoid reporting on sensitive emails
5. **Use appropriate filters** to narrow results to project-relevant emails
6. **ALWAYS use `--max-results`** to prevent slow searches
7. **Execute all commands** using the virtual environment
8. **Summarize content concisely** rather than dumping raw emails
9. **Highlight missing information** that should be in Jira, Slack, or Confluence
10. **Provide actionable insights** (who needs to do what)
