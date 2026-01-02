# Engagement Agent

A proactive AI assistant for consultants working on client engagements. Seamlessly integrates with Jira, Confluence, Slack, Gmail, and Bitbucket to help you track project health, identify blockers, and generate weekly status reports.

## Architecture

![engagement-agent-3](https://github.com/user-attachments/assets/07954358-f861-4f5d-a254-4e8a5176c9ce)

## Features

- **Jira Integration**: Track ticket progress, identify blockers, analyze sprint velocity
- **Confluence Knowledge Management**: Search documentation, fetch meeting notes, generate Weekly Status Reports
- **Slack Monitoring**: Summarize channel activity, extract key decisions and action items
- **Gmail Analysis**: Search and summarize project-related emails
- **Bitbucket Integration**: Browse repositories, view pull requests, track commits, search code
- **AWS Environment Queries**: Read-only access to query AWS resources across multiple accounts
- **AWS Security Analysis (Skill)**: Advanced security auditing with CloudTrail Lake, Security Hub, GuardDuty, IAM Access Analyzer, and AWS Config
- **Intelligent Synthesis**: Connects the dots between platforms to provide actionable insights
- **Usage Tracking**: Monitor AI API calls, token consumption, and costs across sessions


## Cost Monitoring Dashboard

<img width="3362" height="1996" alt="image" src="https://github.com/user-attachments/assets/b25d5f55-c234-4dc4-ad69-ba5fd313ff1c" />

```
cd ./opencode-dashboard
npm start
```


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

**Setting up Google Gemini models:**

If using Google models (e.g., Gemini 2.5 Flash), you'll need to configure API access:

1. Get your API key from [Google AI Studio](https://aistudio.google.com/)

2. Store the API key securely in macOS Keychain:
   ```bash
   security add-generic-password -a $USER -s "GeminiAPICredential" -w "YOUR_API_KEY_HERE"
   ```

3. Add to your `~/.zshrc`:
   ```bash
   export GEMINI_API_KEY=$(security find-generic-password -s "GeminiAPICredential" -w)
   ```

4. Refresh your shell:
   ```bash
   source ~/.zshrc
   ```

**Setting up AWS Bedrock models:**

If using AWS Bedrock models (e.g., Claude 3.5 Sonnet via Bedrock), you'll need AWS account access:

1. Request admin AWS access to account: **144986566169**

2. Configure your AWS profile in `~/.aws/config` (if not already configured)

3. Ensure you have appropriate Bedrock model access in the AWS account

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

## Personal Knowledge Management

The Engagement Agent automatically builds a [**personal knowledge vector database**](https://github.com/NocturnLabs/opencode-personal-knowledge) from your conversations. This creates a searchable memory of technical patterns, configurations, and solutions specific to your projects.

### How It Works

The agent uses **two complementary systems** to preserve knowledge:

#### 1. **Automatic Knowledge Entries** (Default Behavior)

The agent **proactively saves** important technical information during conversations:

**What gets saved automatically:**
- ✅ Code patterns, commands, and configurations discussed
- ✅ Technical decisions and architectural approaches
- ✅ Problem-solving strategies and debugging steps
- ✅ API endpoints and integration patterns (no actual secrets)
- ✅ Solutions to resolved issues
- ✅ Best practices and optimization techniques
- ✅ Project-specific configurations and setup procedures

**What does NOT get saved:**
- ❌ Casual conversation or greetings
- ❌ Questions without answers
- ❌ Secrets, passwords, API keys, or credentials
- ❌ Personal or private information
- ❌ Trivial exchanges or clarifications
- ❌ Content already documented in Confluence (links to Confluence instead)

**When it saves:**
- After resolving a technical problem
- When discussing new patterns or approaches
- After explaining configuration or setup steps
- When making important technical decisions
- After 2+ exchanges about a technical topic with code/commands/configurations

**Example notification:**
```
📝 Stored in knowledge base: AWS Lambda Timeout Configuration Best Practices (Entry #42)
```

**Manual control:**
```
/store-knowledge          # Manually save the current conversation
/search-knowledge <query> # Search your saved knowledge
```

#### 2. **Session Logging** (Optional, On-Demand)

For complete conversation transcripts with turn-by-turn detail:

```
Start a logging session:
> /start-logging "debugging auth flow"

... conversation happens ...

End the session:
> /end-session "Fixed OAuth token refresh issue"
```

**Key differences:**

| Feature | Knowledge Entries | Session Logging |
|---------|------------------|-----------------|
| **Activation** | Automatic (always on) | Manual (explicit start) |
| **Granularity** | Key insights only | Every message turn |
| **Use case** | Quick reference, patterns | Complete conversation history |
| **Storage** | When insight detected | Continuous (every turn) |
| **Search** | By topic/technology | By conversation context |

### Searching Your Knowledge

**Simple search:**
```
What is the matillionhub DNS record?
```
The agent automatically searches its knowledge base when you ask factual questions.

**Explicit search:**
```
/search-knowledge AWS Lambda timeout
```
Returns top 5 most relevant entries with similarity scores.

**View specific entry:**
```
Show me knowledge entry #42
```

**List all entries:**
```
List my knowledge entries tagged with "aws" and "debugging"
```

### Knowledge Organization

**Automatic tagging:** The agent generates 3-5 relevant tags per entry:
- **Technology**: `aws`, `python`, `docker`, `kubernetes`, `typescript`
- **Activity**: `debugging`, `optimization`, `deployment`, `migration`, `testing`
- **Domain**: `security`, `performance`, `cost`, `networking`, `database`
- **Project-specific**: Terms from your `engagement_agent_config.json`

**Example entry structure:**
```
Title: Windcheater AWS Account and Matillion DNS Records
Tags: aws, windcheater, superdry, route53, dns, matillion, infrastructure, alb
Content: [Full technical details with commands, outputs, and context]
```

### Privacy & Security

- ✅ **Local storage**: All knowledge stored in your personal MCP server
- ✅ **No secrets**: Automatically filters out credentials, tokens, keys
- ✅ **No PII**: Excludes personal or private information
- ✅ **User control**: Manually trigger, search, or disable storage
- ✅ **Transparent**: You're notified when information is saved

### Best Practices

**To maximize value:**
1. Let the agent save automatically - it's trained to identify valuable content
2. Use descriptive language when discussing solutions ("This fixes X by doing Y")
3. Explicitly request storage for edge cases: `/store-knowledge`
4. Review stored knowledge periodically: `/search-knowledge recent configurations`
5. Use session logging for complex debugging sessions you'll reference later

**To maintain privacy:**
1. Don't paste API keys or credentials in chat (agent filters, but better to avoid)
2. Review entries if unsure: `Show me knowledge entry #X`
3. Delete sensitive entries if accidentally stored: `Delete knowledge entry #X`

### Example Workflow

```
You: How do I configure the Matillion ALB?
Agent: Let me check my knowledge base...
       [Returns DNS records from previous discussion]

You: What was that Python virtual environment issue we fixed last month?
Agent: [Searches knowledge base and finds the solution]

You: Start logging, I'm about to debug a complex CloudTrail Lake query
Agent: ✅ Started logging session #12 "CloudTrail Lake debugging"
You: [Work through the problem]
Agent: [Logs every turn automatically]
You: End session, we fixed the SQL syntax issue
Agent: ✅ Ended session #12 (23 messages logged)
```

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
- **Size**: ~16,500 characters / ~2,400 words
- **Estimated tokens**: ~4,100 tokens
- **Context budget**: 2.0% of typical 200K token limit
- **Leaves available**: ~195,900 tokens for conversation and tool outputs

**Why this matters:**
- ✅ Small overhead allows for longer conversations
- ✅ Plenty of room for large tool outputs (CloudTrail queries, Confluence pages, Jira summaries)
- ✅ Multi-turn conversations without context pressure
- ✅ Skill system keeps specialized knowledge out of base prompt

**Comparison:**
- Base prompt: ~4,100 tokens (2.0%)
- With 10-turn conversation: ~15,000-25,000 tokens (7-12%)
- Typical session: 50,000-100,000 tokens (25-50%)

The system prompt is designed to be detailed enough for consistent behavior while remaining token-efficient. The skill system (`.opencode/skill/*.md`) allows loading specialized knowledge on-demand without inflating the base prompt.

**Last updated**: 2026-01-02 (~440 lines, ~4,100 tokens)

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
