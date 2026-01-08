---
description: Setup credentials for Engagement Agent
---

Guide user through credential setup for Engagement Agent. Check `engagement_agent_config.json` and fill missing values.

**Step 1: Initial Setup**
- Check for `engagement_agent_config.json`. If missing, copy from `engagement_agent_config.example.json`.

**Step 2: Python Virtual Environment (CRITICAL)**
- Check if venv exists at config path (default: `venv`)
- If missing:
  1. Ask user for path (default or custom)
  2. Create: `python3 -m venv <path>`
  3. Update `python.venv_path` in config
  4. Install requirements: `source <venv_path>/bin/activate && pip install -r tools/requirements.txt`
- If exists but requirements missing: `source <venv_path>/bin/activate && pip install -r tools/requirements.txt`
- Verify: `jira`, `atlassian-python-api`, `google-api-python-client`, `slack_sdk` installed
- **All Python tool executions MUST use this venv**

**Step 3: Credential Onboarding**
Check for missing credentials:
- **Atlassian (Jira/Confluence)**: `atlassian_email`, `atlassian_api_token`, `atlassian_domain`, `confluence_space_keys`, `jira_project_keys`
- **Bitbucket**: `bitbucket_email`, `bitbucket_api_token`, `bitbucket_workspace`, `bitbucket_project_key`
- **Slack**: `slack_bot_token`, `slack_channel_ids`
- **Gmail**: `gmail_credentials_path`, `recipient_emails_to_scan`

For each missing credential:
1. Provide token generation instructions
2. Prompt for values
3. Update config file

**Slack Setup (Create from Manifest):**
1. Go to https://api.slack.com/apps → "Create New App" → "From an app manifest"
2. Choose workspace, select JSON format
3. Paste manifest:

```json
{
  "display_information": {
    "name": "Engagement Agent",
    "description": "AI assistant that helps consultants track project status across Jira, Confluence, Slack, and Gmail",
    "background_color": "#2c2d30"
  },
  "features": {
    "bot_user": {
      "display_name": "Engagement Agent",
      "always_online": true
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "channels:history",
        "channels:read",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "users:read",
        "search:read.files",
        "search:read.public",
        "search:read.users"
      ]
    }
  },
  "settings": {
    "org_deploy_enabled": false,
    "socket_mode_enabled": false,
    "token_rotation_enabled": false
  }
}
```

4. After creation: "OAuth & Permissions" → "Install to Workspace" → Authorize
5. Copy "Bot User OAuth Token" (starts with `xoxb-`)

**CRITICAL: Bot Channel Invitation**
- Bot MUST be invited to each channel in `slack_channel_ids` and `client_slack_channel_id`
- In each channel: `/invite @Engagement Agent`
- Verify bot appears in member list
- Configuration incomplete until bot invited to ALL channels

**Bitbucket Setup:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. "Create API token with scopes" (**DIFFERENT from Jira/Confluence token**)
3. Configure:
   - Name: "Engagement Agent - Bitbucket"
   - Expiry: 1 year or No expiration (production)
   - Scope: Select "Read" for ALL actions (Account, Workspace, Projects, Repositories, PRs, Issues, Wikis, Snippets, Webhooks, Pipelines, Runners)
4. Copy token (shown once only)
5. Provide: Atlassian email, token, workspace slug, project key(s)

**Step 4: Statefulness**
- Auto-detect missing credentials and resume where left off if interrupted

**Step 5: Gmail Token Refresh**
- Verify token validity after Gmail setup
- If `~/.agents/gmail_token.json` expired, refresh using venv:
```python
import json, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

with open('engagement_agent_config.json') as f:
    config = json.load(f)
token_file = os.path.expanduser(config['google']['token_file'])
creds = Credentials.from_authorized_user_file(token_file, config['google']['scopes'])
if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(token_file, 'w') as token:
        token.write(creds.to_json())
```

**Step 6: Verification**
Test each tool in venv:
1. Jira: `source <venv>/bin/activate && python3 tools/jira_tool.py get-summary --project-key <KEY> --days 7`
2. Confluence: `source <venv>/bin/activate && python3 tools/confluence_tool.py search <SPACE> "test" --limit 1`
3. Bitbucket: `source <venv>/bin/activate && python3 tools/bitbucket_tool.py list-workspaces`
4. Slack: `source <venv>/bin/activate && python3 tools/slack_tool.py get-channel-summary <CH_ID> <START> <END> --limit 10`
5. Gmail: `source <venv>/bin/activate && python3 tools/gmail_tool.py search-emails --max-results 1`

Display configured services summary and begin onboarding.
