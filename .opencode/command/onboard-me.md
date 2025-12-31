---
description: Setup credentials for Engagement Agent
agent: general
---

Guide me through setting up the necessary credentials to run the Engagement Agent. Check for an existing `engagement_agent_config.json` and help me fill in the missing values.

**Step 1: Initial Setup**
- First, check if I have a `engagement_agent_config.json` file. If not, create one by copying `engagement_agent_config.example.json`.

**Step 2: Python Virtual Environment Setup (CRITICAL)**
- Check if a Python virtual environment exists at the path specified in the config (default: `venv`)
- If it doesn't exist:
  1. Ask the user if they want to create it at the default location `venv` or specify a custom path
  2. Create the virtual environment: `python3 -m venv <path>`
  3. Update the config file with the venv path in `python.venv_path`
  4. Activate the virtual environment and install all requirements:
     ```bash
     source <venv_path>/bin/activate
     pip install -r tools/requirements.txt
     ```
- If it exists but requirements aren't installed:
  1. Activate and install: `source <venv_path>/bin/activate && pip install -r tools/requirements.txt`
- Verify installation by checking that `jira`, `atlassian-python-api`, `google-api-python-client`, and `slack_sdk` are installed
- **IMPORTANT**: All subsequent Python tool executions MUST use this virtual environment

**Step 3: Interactive Credential Onboarding**
- Read the configuration file and check for missing credentials for the following services:
  - **Atlassian (Jira & Confluence)**: Check for `atlassian_email`, `atlassian_api_token`, `atlassian_domain`, `confluence_space_keys`, `jira_project_keys`
  - **Bitbucket**: Check for `bitbucket_email`, `bitbucket_api_token`, `bitbucket_workspace`, `bitbucket_project_key`
  - **Slack**: Check for `slack_bot_token`, `slack_channel_ids`
  - **Google (Gmail)**: Check for `gmail_credentials_path`, `recipient_emails_to_scan`

- For each service with missing credentials:
  1. Provide precise, step-by-step instructions on how to generate the required API tokens or credentials.
  2. Prompt me to paste the required values (like API tokens, email addresses, or file paths).
  3. Update the `engagement_agent_config.json` file with the information I provide.

**Slack Setup Instructions (use "Create from Manifest"):**
When setting up Slack, guide the user through these steps:
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Select "From an app manifest"
4. Choose your workspace
5. Select JSON format
6. Suggest the following app details:
   - **Short description**: "AI assistant that helps consultants track project status across Jira, Confluence, Slack, and Gmail"
   - **Long description**: "Engagement Agent is a proactive project assistant that integrates with Jira, Confluence, Slack, and Gmail to help consultants efficiently monitor project health, track action items, identify blockers, and generate weekly status reports. It synthesizes information across platforms to provide clear, actionable insights."
7. Provide the following manifest JSON to paste:

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

8. After creating the app, go to "OAuth & Permissions"
9. Click "Install to Workspace"
10. Authorize the app
11. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

**CRITICAL: After configuring Slack channel IDs, verify the bot has been invited to all channels:**
- The bot MUST be invited to each channel configured in `slack_channel_ids` and `client_slack_channel_id`
- In each Slack channel, type `/invite @Engagement Agent` (or the bot name you chose)
- Verify the bot appears in the channel member list
- Without this step, the bot cannot read messages from those channels even with correct scopes
- Do NOT mark Slack configuration as complete until the bot has been invited to all channels

The manifest includes these scopes:
- `channels:history` - Read messages from public channels
- `channels:read` - View basic channel information
- `groups:history` - Read messages from private channels
- `groups:read` - View basic private channel information
- `im:history` - Read direct messages
- `im:read` - View DM information
- `users:read` - View people in the workspace
- `search:read.files` - Search workspace files
- `search:read.public` - Search content in public channels
- `search:read.users` - Search workspace users

**Bitbucket Setup Instructions:**
When setting up Bitbucket, guide the user through these steps:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token with scopes"
3. **IMPORTANT:** This is a DIFFERENT token than Jira/Confluence - Bitbucket requires its own scoped API token
4. Configure the token:
   - **Token name**: "Engagement Agent - Bitbucket" (or similar descriptive name)
   - **Expiry**: Choose appropriate expiration (recommend 1 year or No expiration for production use)
   - **Scope: Actions**: Select "Read" and then check ALL the read-only actions:
     - Account: Read
     - Workspace membership: Read
     - Projects: Read
     - Repositories: Read
     - Pull requests: Read
     - Issues: Read
     - Wikis: Read
     - Snippets: Read
     - Webhooks: Read
     - Pipelines: Read
     - Runners: Read
5. Click "Create" and copy the generated token (you won't see it again!)
6. When prompted, provide:
   - Your Atlassian email address (same as Jira/Confluence)
   - The Bitbucket API token you just created
   - Your Bitbucket workspace slug (visible in URLs like `bitbucket.org/YOUR-WORKSPACE/...`)
   - The project key(s) for your project(s) (e.g., "SUP" for Superdry project)

**Step 3: Statefulness**
- If I stop and restart this command at any time, automatically detect which credentials are still missing and pick up exactly where we left off.

**Step 4: Slack Bot Channel Invitation (CRITICAL)**
- After Slack configuration is complete and channel IDs are added to the config:
  1. List all configured channel IDs from `slack_channel_ids` and `client_slack_channel_id`
  2. For EACH channel, instruct the user to:
     - Open the channel in Slack
     - Type `/invite @Engagement Agent` (or the bot name they configured)
     - Verify the bot appears in the channel members
  3. Confirm with the user that the bot has been invited to ALL channels before proceeding
  4. If the user hasn't invited the bot yet, provide clear instructions and WAIT for confirmation

**Step 5: Gmail Token Refresh**
- After Gmail credentials are configured, verify the token is valid
- If `~/.agents/gmail_token.json` exists but is expired:
  1. Refresh it using the virtual environment:
     ```python
     import json, os
     from google.oauth2.credentials import Credentials
     from google.auth.transport.requests import Request
     
     config_file = 'engagement_agent_config.json'
     with open(config_file, 'r') as f:
         config = json.load(f)
     token_file = os.path.expanduser(config['google']['token_file'])
     scopes = config['google']['scopes']
     creds = Credentials.from_authorized_user_file(token_file, scopes)
     if creds and creds.expired and creds.refresh_token:
         creds.refresh(Request())
         with open(token_file, 'w') as token:
             token.write(creds.to_json())
     ```

**Step 6: Verification**
- After all credentials are filled in, verify the configuration is valid by attempting to read it.
- Test each tool using the configured virtual environment:
  1. Jira: `source <venv_path>/bin/activate && python3 tools/jira_tool.py get-summary --project-key <KEY> --days 7`
  2. Confluence: `source <venv_path>/bin/activate && python3 tools/confluence_tool.py search <SPACE_KEY> "test" --limit 1`
  3. Bitbucket: `source <venv_path>/bin/activate && python3 tools/bitbucket_tool.py list-workspaces`
  4. Slack: `source <venv_path>/bin/activate && python3 tools/slack_tool.py get-channel-summary <CHANNEL_ID> <START_DATE> <END_DATE> --limit 10`
  5. Gmail: `source <venv_path>/bin/activate && python3 tools/gmail_tool.py search-emails --max-results 1`
- Display a summary of the configured services.

Begin the onboarding process now.
