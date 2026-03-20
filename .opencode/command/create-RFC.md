---
description: Create a Request for Change (RFC) document in Confluence
---

## Overview

This command creates a Confluence RFC page populated from Jira ticket details and associated Bitbucket Pull Requests.

**Configuration**: All project-specific settings are stored in `config/engagement_agent_config.json` under the `rfc` section.

**Template**: The RFC HTML template is located at the path specified in `rfc.template_path` (default: `tools/templates/rfc_template.html`)

## Prerequisites

Before running this command, ensure:
1. `config/engagement_agent_config.json` has the `rfc` section configured with:
   - `confluence_space_key`: Target Confluence space
   - `parent_page_id`: Parent page/folder ID for RFCs
   - `template_path`: Path to RFC HTML template
   - `defaults`: Default values for RFC fields
2. *(Optional)* The RFC template file exists at the specified `template_path`. If not, you'll be prompted to provide a URL to an existing RFC to use as a template.
3. Python venv is available with required tools

## Steps

### Step 1: Ask for the Ticket Number

- **FIRST ACTION:** Ask the user: "Please provide the Jira ticket number for the RFC (e.g. SD-4614)."
- Accept both formats: `{PROJECT_KEY}-{NUMBER}` or just `{NUMBER}` (prepend project key from `agent.jira_project_key` if only a number is given).

### Step 1.5: Ask for the Risk Level

- **If the user has not already specified the Risk level**, ask: "What is the Risk level for this RFC? (Low / Medium / High)"
- Accept case-insensitive input: `low`, `Low`, `LOW`, etc.
- Store the normalized value (capitalize first letter: `Low`, `Medium`, or `High`) for use in Step 4.

### Step 2: Verify Template Exists

**Before loading configuration**, check if the RFC template file exists:

1. Load the config to get the template path: `config/engagement_agent_config.json` → `rfc.template_path`
2. Check if the file exists at that path (default: `tools/templates/rfc_template.html`)

**If template does NOT exist:**
1. Ask the user: "RFC template not found at `{template_path}`. Please provide a URL to an existing RFC page that can be used as a template (e.g., a Confluence page URL)."
2. Wait for the user to provide a URL
3. Fetch the content from the URL:
   - If it's a Confluence URL, use: `python3 tools/confluence_tool.py get-page {PAGE_ID} --format html`
   - If it's a web URL, use the WebFetch tool to retrieve the HTML
4. Extract the HTML content (if from Confluence, extract the body content)
5. Save the content to `tools/templates/rfc_template.html`:
   ```bash
   cat > tools/templates/rfc_template.html << 'EOF'
   {HTML_CONTENT}
   EOF
   ```
6. Inform the user: "✓ Template saved to `tools/templates/rfc_template.html`. You can customize this template as needed."
7. **IMPORTANT**: After saving, analyze the template HTML to identify all placeholder patterns and inform the user which placeholders were detected (e.g., fields, variables, or sections that should be replaced). Suggest updating the template to use standard placeholder format `{PLACEHOLDER_NAME}` if not already using this pattern.

**If template exists:**
- Proceed to Step 3

### Step 3: Load Configuration

Load settings from `config/engagement_agent_config.json`:

```python
# Pseudocode - actual implementation would use Python
config = load_config("config/engagement_agent_config.json")

rfc_config = config["rfc"]
agent_config = config["agent"]
jira_config = config["jira"]

# Extract needed values
confluence_space = rfc_config["confluence_space_key"]
parent_page_id = rfc_config["parent_page_id"]
template_path = rfc_config["template_path"]
defaults = rfc_config["defaults"]

jira_server = jira_config["server"]
jira_project_key = agent_config["jira_project_key"]
bitbucket_workspace = agent_config["bitbucket_workspace"]
bitbucket_project_key = agent_config["bitbucket_project_key"]
```

### Step 4: Fetch Jira Ticket Details

Activate venv: `cd $PWD && source venv/bin/activate`

Run: `python3 tools/jira_tool.py get-ticket {TICKET_ID}`

Extract:
- **Summary** (ticket title)
- **Description** (detailed RFC description)
- **Assignee** (name + email — this is the Implementer/Requester)
- **Reporter**
- **Status**
- **Created date**
- **Labels / Components** (if any)

### Step 5: Find Associated Pull Request(s)

Look up PRs in Bitbucket linked to this ticket. The Jira ticket ID pattern to search is the ticket number (e.g. `SD-4614`).

Run the following to get all repositories:

```bash
python3 tools/bitbucket_tool.py list-repositories {bitbucket_workspace} --project-key {bitbucket_project_key}
```

For **each** repository, search for PRs matching the ticket ID:

```bash
python3 tools/bitbucket_tool.py list-pull-requests {bitbucket_workspace} {REPO_SLUG} --state ALL --limit 50
```

Filter results where the PR title or branch name contains the ticket ID. Extract from matched PRs:
- PR title
- PR URL
- PR state (OPEN / MERGED / DECLINED)
- Author (name + email)
- Target branch
- Description / commits summary (for implementation plan)

### Step 6: Load and Populate RFC Template

**Step 6.1: Read Template File**

Load the HTML template from the path specified in config:

```bash
cat {template_path}
```

**Step 6.2: Prepare Placeholder Values**

Build a dictionary of all placeholder values to replace in the template. Use values from:
1. **Jira ticket data** (Step 4)
2. **PR data** (Step 5)
3. **Config defaults** (`rfc.defaults` section)
4. **User input** (Risk level from Step 1.5)
5. **Calculated values** (today's date, dynamic text generation)

**Placeholder Mapping:**

| Placeholder | Source | Notes |
|------------|---------|-------|
| `{TICKET_ID}` | User input (Step 1) | |
| `{JIRA_SERVER}` | `jira.server` from config | |
| `{JIRA_SUMMARY}` | Jira ticket summary | |
| `{JIRA_DESCRIPTION}` | Jira ticket description | |
| `{ASSIGNEE_NAME}` | Jira ticket assignee | |
| `{ASSIGNEE_EMAIL}` | Jira ticket assignee email | |
| `{TODAY_DATE}` | Current date (YYYY-MM-DD) | |
| `{CLASSIFICATION}` | `defaults.classification` | |
| `{STATUS}` | `defaults.status` | |
| `{AUTHOR}` | `defaults.author` | |
| `{RELEASE_VERSION}` | Empty or from ticket | |
| `{CONTACT_NAME}` | `defaults.contact_name` | |
| `{CONTACT_TITLE}` | `defaults.contact_title` | |
| `{CONTACT_EMAIL}` | `defaults.contact_email` | |
| `{CONTACT_TELEPHONE}` | `defaults.contact_telephone` | |
| `{THIRD_PARTIES}` | Empty or from ticket | |
| `{THIRD_PARTIES_CONTACT}` | Empty | |
| `{RFC_SPONSOR}` | Empty or from ticket | |
| `{RFC_SPONSOR_CONTACT}` | Empty | |
| `{IMPL_START}` | PR merge date or ticket created date | Format: `DD MMM YYYY - HH:MM` |
| `{IMPL_END}` | Empty | |
| `{OUTAGE_DATETIME}` | Empty unless in ticket | |
| `{OUTAGE_DETAILS}` | `defaults.outage_details` | |
| `{ASSETS_IMPACTED}` | Empty or from ticket | |
| `{COMMUNICATIONS_REQUIRED}` | Empty or from ticket | |
| `{RFC_CATEGORISATION}` | `defaults.rfc_categorisation` | |
| `{RFC_REASON}` | `defaults.rfc_reason` | |
| `{RELATES_TO_OTHER}` | `defaults.relates_to_other` | |
| `{IMPL_PLAN}` | See logic below | |
| `{PRE_IMPL_TESTING}` | See logic below | |
| `{RISK_LEVEL}` | User input (Step 1.5) | |
| `{RISK_ASSESSMENT_TEXT}` | Generated from Risk level | |
| `{RISK_MITIGATION}` | `defaults.risk_mitigation` | |
| `{IMPACT_LEVEL}` | `defaults.impact_level` | |
| `{IMPACT_ASSESSMENT_TEXT}` | Generated from Impact level | |
| `{IMPACT_MITIGATION}` | `defaults.impact_mitigation` | |
| `{DELAY_IMPACT}` | Empty or from ticket | |
| `{POST_IMPL_TESTING}` | Empty or from ticket | |
| `{BACKOUT_PLAN}` | Empty or from ticket | |
| `{DOCUMENTATION_REQUIREMENTS}` | Empty or from ticket | |

**Special Logic:**

**`{IMPL_PLAN}`:**
- If PR exists: Use `defaults.impl_plan_with_pr` (e.g., "Deploy using code pipeline")
- Otherwise: Derive from ticket description or leave empty

**`{PRE_IMPL_TESTING}`:**
- Derive environment from PR branch name or ticket description
- Format: `{defaults.pre_impl_testing_prefix} [environment]` (e.g., "Services running successfully on staging")

**`{RISK_ASSESSMENT_TEXT}`:**
Generate based on user's Risk level input:
- If Risk = `Low`: `<strong>Low</strong> | Medium | High`
- If Risk = `Medium`: `Low | <strong>Medium</strong> | High`
- If Risk = `High`: `Low | Medium | <strong>High</strong>`

**`{IMPACT_ASSESSMENT_TEXT}`:**
Generate based on Impact level from config (default: `High`):
- If Impact = `Low`: `<strong>Low</strong> | Medium | High`
- If Impact = `Medium`: `Low | <strong>Medium</strong> | High`
- If Impact = `High`: `Low | Medium | <strong>High</strong>`

**Step 6.3: Replace All Placeholders**

Perform string replacement on the template content for each placeholder:

```python
# Pseudocode
html_content = template_content
for placeholder, value in placeholder_values.items():
    html_content = html_content.replace(placeholder, value or "")
```

### Step 7: Create Confluence Page

Run:
```bash
python3 tools/confluence_tool.py create-page \
  --space-key "{confluence_space}" \
  --title "RFC - {TICKET_ID} {JIRA_SUMMARY}" \
  --parent-id "{parent_page_id}" \
  --content "{ESCAPED_HTML_CONTENT}"
```

- The `--content` argument must be the fully rendered HTML from Step 6 with all placeholders replaced.
- Escape any special characters for command-line usage
- Capture the page ID from the output.

### Step 8: Verify and Return URL

- **DELEGATE to confluence-agent:** Search for the newly created page by title in the configured Confluence space.
- Build the full URL: `{jira_server}/wiki` + `_links.webui` from search result.
- If page not found: Report error — "RFC creation failed — page not found in Confluence space {confluence_space}"
- If found: Report success with the full URL.

### Step 9: Open Browser

- Run: `open {VERIFIED_CONFLUENCE_URL}`

## Summary Output to User

```
RFC created successfully:
  Ticket:     {TICKET_ID} — {JIRA_SUMMARY}
  Assignee:   {ASSIGNEE_NAME} ({ASSIGNEE_EMAIL})
  PR(s):      {PR_URL(s) or "None found"}
  Confluence: {CONFLUENCE_URL}
```

## Configuration Example

Add this section to your `config/engagement_agent_config.json`:

```json
{
  "rfc": {
    "confluence_space_key": "YOURSPACE",
    "parent_page_id": "123456789",
    "parent_page_title": "RFCs",
    "template_path": "tools/templates/rfc_template.html",
    "defaults": {
      "classification": "Confidential",
      "status": "Published",
      "author": "Your Name",
      "contact_name": "Contact Name",
      "contact_title": "Contact Title",
      "contact_email": "contact@example.com",
      "contact_telephone": "",
      "rfc_categorisation": "Normal",
      "rfc_reason": "Possible downtime for production services",
      "relates_to_other": "No",
      "outage_details": "No outage expected",
      "risk_mitigation": "Risks have been highlighted and mitigated.",
      "impact_level": "High",
      "impact_mitigation": "The impact is minor/localised.",
      "impl_plan_with_pr": "Deploy using code pipeline",
      "pre_impl_testing_prefix": "Services running successfully on"
    }
  }
}
```
