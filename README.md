# Engagement Agent

A proactive AI assistant for consultants working on client engagements. Seamlessly integrates with Jira, Confluence, Slack, Gmail, and Bitbucket to help you track project health, identify blockers, and generate weekly status reports.

## Features

- **Jira Integration**: Track ticket progress, identify blockers, analyze sprint velocity
- **Confluence Knowledge Management**: Search documentation, fetch meeting notes, generate Weekly Status Reports
- **Slack Monitoring**: Summarize channel activity, extract key decisions and action items
- **Gmail Analysis**: Search and summarize project-related emails
- **Bitbucket Integration**: Browse repositories, view pull requests, track commits, search code
- **AWS Environment Queries**: Read-only access to query AWS resources across multiple accounts
- **AWS Security Analysis (Skill)**: Advanced security auditing with CloudTrail Lake, Security Hub, GuardDuty, IAM Access Analyzer, and AWS Config
- **Intelligent Synthesis**: Connects the dots between platforms to provide actionable insights

## Quick Start

### 1. Install OpenCode

```bash
brew install opencode
```

### 2. Launch OpenCode In this Repo

```bash
opencode
```

This opens OpenCode in the engagement-agent directory.

### 3. Connect to AI Model & Prime with Context

Choose one of the following options to connect:

**Option A: Browse available models**
```
/models
```
Select your preferred model from the list (e.g., Claude 3.5 Sonnet, GPT-4, etc.)

**Option B: Connect directly**
```
/connect
```
Follow the prompts to connect to your AI provider.

### 4. Onboard Your Credentials

Run the onboarding command to set up your integrations:

```
/onboard-me
```

This interactive wizard will guide you through:
- ✅ Creating a Python virtual environment with all dependencies
- ✅ Configuring Atlassian (Jira & Confluence) API credentials
- ✅ Setting up Slack bot token with proper scopes
- ✅ Configuring Gmail OAuth credentials
- ✅ Adding project-specific settings (space keys, channel IDs, etc.)

**Important:** Make sure to:
- Invite the Slack bot to all configured channels (`/invite @Engagement Agent`)
- Complete Gmail OAuth authorization when prompted

### 5. Validate Your Setup

Test each integration to ensure everything is working:

**Test Jira:**
```
Show me SD tickets updated in the last week
```

**Test Confluence:**
```
Search SDRY space for "architecture" documentation
```

**Test Slack:**
```
Summarize the client channel from the last 3 days
```

**Test Bitbucket:**
```
List repositories in the SUP project
```
or
```
What was the last pull request about?
```

**Test Gmail:**
```
Find emails from david.holmes@superdry.com about deployment
```

**Test AWS (if configured):**
```
What is the CIDR range of the windcheater-prod VPC?
```

## Key Features & Commands

### Chat with Your Project Data

Simply ask questions in natural language:

- "What's blocking the team right now?"
- "What decisions were made in Slack this week?"
- "Find the latest meeting notes in Confluence"
- "Show me high-priority bugs in Jira"
- "Any risks mentioned in emails this week?"

### Generate Weekly Status Reports

Automatically compile project updates into a formatted Confluence page:

```
/generate-wsr
```

This command will:
1. Gather updates from Jira, Slack, Gmail, and Confluence
2. Synthesize key achievements, upcoming activities, and blockers
3. Create a new Weekly Status Report page in Confluence
4. Return the URL to the published report

### AWS Security Analysis (Advanced Skill)

For deep security auditing and threat detection, use natural language to activate the AWS Security Analysis skill:

**Example queries:**
- "Who was the last person to login to the production account?"
- "Show me all failed authentication attempts this week"
- "What are our critical Security Hub findings?"
- "Analyze CloudTrail for unusual API activity"
- "Check for overly permissive IAM policies"

**First-time setup:** The skill will prompt you for:
1. Delegated admin account profile (for Security Hub, GuardDuty, CloudTrail Lake)
2. Management account profile (for organization discovery)
3. Region (e.g., eu-west-1, us-east-1)

**Capabilities:**
- **CloudTrail Lake**: SQL-based queries for console logins, API calls, failed authentications
- **Security Hub**: Aggregated findings, compliance status, severity analysis
- **GuardDuty**: Threat intelligence and anomaly detection
- **IAM Access Analyzer**: External access findings, unused permissions
- **AWS Config**: Configuration compliance checking
- **Organization-wide**: Multi-account security posture assessment

**Note:** All operations are read-only. The skill automatically handles asynchronous CloudTrail Lake queries and caches frequently-used IDs.

See `.opencode/skill/aws-security.md` for detailed documentation.

### Other Useful Commands

- `/models` - Switch AI models
- `/help` - Show available commands
- `Ctrl+P` - List available actions
- `Ctrl+C` - Cancel current operation

## Configuration

Your settings are stored in `engagement_agent_config.json`:

```json
{
  "python": {
    "venv_path": "venv"
  },
  "google": {
    "credentials_file": "~/.agents/gmail_credentials.json",
    "token_file": "~/.agents/gmail_token.json"
  },
  "slack": {
    "token": "xoxb-..."
  },
  "jira": {
    "server": "https://your-domain.atlassian.net",
    "email": "your-email@example.com",
    "api_token": "..."
  },
  "confluence": {
    "server": "https://your-domain.atlassian.net",
    "email": "your-email@example.com",
    "api_token": "..."
  },
  "bitbucket": {
    "note": "Optional - uses Confluence credentials by default",
    "url": "https://api.bitbucket.org",
    "email": "your-email@example.com",
    "api_token": "...",
    "cloud": true
  },
  "aws_security": {
    "delegated_admin_profile": "audit",
    "management_account_profile": "management",
    "cloudtrail_lake_event_data_store_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "region": "us-east-1"
  },
  "agent": {
    "project_name": "Your Project",
    "jira_project_key": "PROJ",
    "confluence_space_key": ["SPACE1", "SPACE2"],
    "bitbucket_workspace": "your-workspace-slug",
    "bitbucket_project_key": "SUP",
    "slack_channel_ids": ["C01234567"],
    "pull_request_channel": "G01C28YBXQT",
    "recipient_emails_to_scan": ["colleague@example.com"],
    "stakeholder_emails": ["stakeholder@client.com"],
    "cloud_environments": ["AWS"],
    "regions": ["us-east-1"]
  }
}
```

## Architecture

- **Tools Directory** (`tools/`): Python scripts for API integrations
  - `jira_tool.py` - Jira API client
  - `confluence_tool.py` - Confluence API client
  - `slack_tool.py` - Slack API client
  - `gmail_tool.py` - Gmail API client
  - `bitbucket_tool.py` - Bitbucket API client
  - `wsr_tool.py` - Weekly Status Report generator
  - `requirements.txt` - Python dependencies

- **Templates** (`tools/templates/`): Confluence page templates
  - `wsr_full_template.html` - WSR template (auto-generated)

- **Documentation**:
  - `INSTRUCTIONS.md` - AI agent system prompt and guiding principles
  - `tools/TOOLS.md` - Detailed tool usage documentation

## System Prompt Efficiency

The `INSTRUCTIONS.md` system prompt is designed to be comprehensive yet efficient:

**Token Usage:**
- **Size**: 9,979 characters / 1,352 words
- **Estimated tokens**: ~1,400 tokens
- **Context budget**: 0.7% of typical 200K token limit
- **Leaves available**: ~198,600 tokens for conversation and tool outputs

**Why this matters:**
- ✅ Small overhead allows for longer conversations
- ✅ Plenty of room for large tool outputs (CloudTrail queries, Confluence pages, Jira summaries)
- ✅ Multi-turn conversations without context pressure
- ✅ Skill system keeps specialized knowledge out of base prompt

**Comparison:**
- Base prompt: ~1,400 tokens (0.7%)
- With 10-turn conversation: ~10,000-20,000 tokens (5-10%)
- Typical session: 50,000-100,000 tokens (25-50%)

The system prompt is designed to be detailed enough for consistent behavior while remaining token-efficient. The skill system (`.opencode/skill/*.md`) allows loading specialized knowledge on-demand without inflating the base prompt.

**Last updated**: 2025-12-23 (104 lines, ~1,400 tokens)

## Requirements

- **macOS** (Linux support available via manual installation)
- **Python 3.9+** with virtual environment support
- **AWS CLI & aws-vault** (optional, for AWS queries)
- **API Access**:
  - Atlassian account with API token
  - Slack workspace with bot app
  - Google Cloud project with Gmail API enabled

## Virtual Environment

All Python tools use a virtual environment (configured in `engagement_agent_config.json`):

```bash
# Activate manually if needed
source venv/bin/activate

# Run tools directly
python3 tools/jira_tool.py get-summary --project-key SD --days 7
```

The agent automatically handles virtual environment activation when executing tools.

## Security & Privacy

- ✅ **Read-only by default**: All operations are non-destructive
- ✅ **Credential isolation**: API tokens stored in local config file
- ✅ **Privacy-aware**: Filters out personal/sensitive emails
- ✅ **AWS read-only**: Only `describe`, `list`, `get` commands allowed
- ✅ **Local execution**: All data processing happens on your machine

## Troubleshooting

### Gmail Token Expired
```bash
cd engagement-agent
source venv/bin/activate
python3 tools/gmail_tool.py search-emails --max-results 1
```
Follow the browser prompt to re-authorize.

### Slack Bot Can't Read Channels
Make sure the bot is invited to each channel:
```
/invite @Engagement Agent
```

### Missing Python Dependencies
```bash
source venv/bin/activate
pip install -r tools/requirements.txt
```

### AWS Profile Not Found
Check your `~/.aws/config` file for the profile name and update `engagement_agent_config.json` if needed.

## Support

- **Issues & Feedback**: Report at [github.com/sst/opencode](https://github.com/sst/opencode)
- **OpenCode Docs**: [opencode.ai/docs](https://opencode.ai/docs)
- **Tool Documentation**: See `tools/TOOLS.md` for detailed usage

## Example Workflow

```
1. Launch OpenCode:
   $ opencode -c gen-ai-examples/engagement-agent

2. Connect to model:
   > /models
   (Select Claude 3.5 Sonnet)

3. Onboard:
   > /onboard-me
   (Follow setup wizard)

4. Validate:
   > Show me tickets updated this week
   > Summarize the client Slack channel

5. Generate WSR:
   > /generate-wsr
   
6. Ask questions:
   > What are the key blockers right now?
   > Find emails about the deployment timeline
   > Who is Chris Browne?
   > What is the CIDR range of the windcheater-prod VPC?

7. AWS Security Analysis:
   > Who was the last person to login to laguna-prod?
   > Show me failed authentication attempts in the last 24 hours
   > What are our critical Security Hub findings?
```

## License

This is an example project demonstrating OpenCode capabilities for engagement management.
