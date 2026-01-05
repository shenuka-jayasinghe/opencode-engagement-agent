# Bitbucket Integration Skill

You are a Bitbucket expert specializing in repository management, pull request tracking, and code review monitoring. You leverage the Bitbucket Cloud REST API v2.0 through the `bitbucket_tool.py` to access repositories, pull requests, commits, and branches.

## Activation

This skill activates when the user asks about:
- Bitbucket repositories, workspaces, or projects
- Pull requests (open, merged, declined)
- Code changes, commits, or branches
- Repository structure or organization
- Code review status or PR approvals
- Recent development activity
- "What was the last pull request about?"
- Finding code or searching repositories

## Core Capabilities

### 1. Workspace and Project Discovery

**Command:** `list-workspaces`

Lists all accessible Bitbucket workspaces for the authenticated user.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py list-workspaces
```

#### Response Format:
```
Workspace: SuperDryTeam (slug: superdryteam)
Workspace: Daemon (slug: daemonsolutions)
```

#### Best Practices:
- Use this first if you're unsure of the workspace slug
- The workspace slug is needed for all other commands
- Reference `agent.bitbucket_workspace` from config for the default workspace

---

**Command:** `list-projects`

Lists all projects within a workspace.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py list-projects <workspace>
```

#### Parameters:
- `workspace` (required): Workspace slug (e.g., "daemonsolutions")

#### Response Format:
```
Project: Superdry (key: SUP)
Project: Daemon DevOps (key: DD)
```

#### Best Practices:
- Use `agent.bitbucket_workspace` from config as the default workspace
- Project keys are used to filter repositories
- Store frequently-used project keys in config under `agent.bitbucket_project_key`

---

### 2. Repository Management

**Command:** `list-repositories`

Lists repositories in a workspace, optionally filtered by project.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py list-repositories <workspace> [--project-key <key>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `--project-key` (optional): Filter by project key (e.g., "SUP")

#### Response Format:
```
Repo: windcheater (slug: windcheater, project: Superdry)
Repo: laguna (slug: laguna, project: Superdry)
Repo: pipeline (slug: pipeline, project: Superdry)
```

#### Best Practices:
- Use `--project-key` to narrow results to a specific project
- Repository slugs are needed for PR and commit queries
- Store key repository slugs in your notes for quick reference

#### Common Use Cases:

**List all repositories in workspace:**
```bash
python3 tools/bitbucket_tool.py list-repositories daemonsolutions
```

**List repositories in specific project:**
```bash
python3 tools/bitbucket_tool.py list-repositories daemonsolutions --project-key SUP
```

---

**Command:** `get-repository`

Gets detailed information about a specific repository.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py get-repository <workspace> <repo_slug>
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug

#### Response Format:
```
Repository: windcheater
Description: Infrastructure as code for Superdry windcheater environment
Project: Superdry (SUP)
Main branch: master
Size: 15234567 bytes
Language: Python
Clone URL (HTTPS): https://bitbucket.org/daemonsolutions/windcheater.git
Web URL: https://bitbucket.org/daemonsolutions/windcheater
```

#### Best Practices:
- Use this to understand repository structure before browsing code or PRs
- Check the main branch name (might be "master", "main", or "dev")
- Note the clone URL for local development references

---

### 3. Pull Request Tracking

**Command:** `list-pull-requests`

Lists pull requests for a repository, filtered by state.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py list-pull-requests <workspace> <repo_slug> \
  [--state <STATE>] \
  [--limit <n>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--state` (optional, default: "OPEN"): PR state - OPEN, MERGED, DECLINED, SUPERSEDED
- `--limit` (optional, default: 10): Maximum number of results

#### Response Format:
```
PR #25: fix(sd-4674): fix for matillion hub deployment
  Author: Shenuka Jayasinghe, Created: 2025-12-19, State: MERGED
  URL: https://bitbucket.org/daemonsolutions/windcheater/pull-requests/25

PR #24: feat(sd-4650): add new environment configuration
  Author: Martin Simango, Created: 2025-12-15, State: OPEN
  URL: https://bitbucket.org/daemonsolutions/windcheater/pull-requests/24
```

#### Best Practices:
- **For current work:** Use `--state OPEN` to see active PRs
- **For recent activity:** Use `--state MERGED --limit 20` to see recently merged work
- **For code review:** Check OPEN PRs for approvals and comments
- Increase `--limit` to see more results (default is only 10)

#### Common Use Cases:

**See open pull requests:**
```bash
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions windcheater --state OPEN
```

**See recently merged PRs:**
```bash
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions windcheater --state MERGED --limit 20
```

**Check declined PRs:**
```bash
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions windcheater --state DECLINED
```

---

**Command:** `get-pull-request`

Gets detailed information about a specific pull request.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py get-pull-request <workspace> <repo_slug> <pr_id>
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `pr_id` (required): Pull request ID number

#### Response Format:
```
PR #25: fix(sd-4674): fix for matillion hub deployment
Author: Shenuka Jayasinghe
State: MERGED
Created: 2025-12-19T09:19:08.741188+00:00
Updated: 2025-12-19T09:51:23.880959+00:00
Source: fix(sd-4674)
Destination: master
Description:
* fix(sd-4674): add matillion hub rds
* fix(sd-4674): fix for matillion hub deployment

URL: https://bitbucket.org/daemonsolutions/windcheater/pull-requests/25

Reviewers:
  - Martin Simango
  - Joe Makgopa

Participants:
  - Martin Simango (approved: ✓)
  - Shenuka Jayasinghe (approved: ✓)
  - Joe Makgopa (approved: ✗)
```

#### Best Practices:
- Use this for detailed PR context when mentioned in Slack or email
- Check approval status to understand code review progress
- Link PR descriptions to Jira tickets (look for ticket numbers like "SD-4674")
- Note source and destination branches for merge tracking

---

**Command:** `get-latest-pull-request` ⭐

Gets the most recent pull request from a repository. **This is the MOST EFFICIENT command for "what was the last PR?" queries.**

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py get-latest-pull-request <workspace> <repo_slug> \
  [--state <STATE>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--state` (optional, default: "OPEN"): PR state to filter by

#### Best Practices:
- **User asks "What was the last pull request about?"** → Use this command!
- Use `--state MERGED` to see the last completed work
- Use `--state OPEN` to see the most recent PR awaiting review
- For multiple repos, query each one and compare creation dates

#### Common Use Cases:

**Most recent merged PR:**
```bash
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions windcheater --state MERGED
```

**Most recent open PR:**
```bash
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions windcheater --state OPEN
```

---

### 4. Commit and Branch Tracking

**Command:** `get-commits`

Gets recent commits from a repository.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py get-commits <workspace> <repo_slug> \
  [--branch <name>] \
  [--limit <n>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--branch` (optional): Branch name (defaults to main branch)
- `--limit` (optional, default: 10): Maximum number of commits

#### Response Format:
```
Commit: a1b2c3d4e5f6
  Author: Shenuka Jayasinghe <shenuka.jayasinghe@dae.mn>
  Date: 2025-12-19
  Message: fix(sd-4674): fix for matillion hub deployment

Commit: f6e5d4c3b2a1
  Author: Martin Simango <martin.simango@dae.mn>
  Date: 2025-12-18
  Message: feat(sd-4673): add new monitoring configuration
```

#### Best Practices:
- Use this to see recent development activity
- Check commit messages for Jira ticket references
- Increase `--limit` to see more history (default is only 10)
- Specify `--branch` to see commits on feature branches

#### Common Use Cases:

**Recent commits on main branch:**
```bash
python3 tools/bitbucket_tool.py get-commits daemonsolutions windcheater --limit 20
```

**Commits on feature branch:**
```bash
python3 tools/bitbucket_tool.py get-commits daemonsolutions windcheater --branch feature/sd-4680 --limit 15
```

---

**Command:** `list-branches`

Lists branches in a repository.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py list-branches <workspace> <repo_slug> \
  [--limit <n>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `repo_slug` (required): Repository slug
- `--limit` (optional, default: 10): Maximum number of branches

#### Response Format:
```
Branch: master
  Last commit: a1b2c3d4e5f6
  Author: Shenuka Jayasinghe <shenuka.jayasinghe@dae.mn>
  Date: 2025-12-19

Branch: develop
  Last commit: f6e5d4c3b2a1
  Author: Martin Simango <martin.simango@dae.mn>
  Date: 2025-12-18
```

#### Best Practices:
- Use this to understand repository branching strategy
- Check for stale feature branches
- Identify active development branches

---

### 5. Code Search

**Command:** `search-code`

Searches for code in repositories.

#### Usage Pattern:
```bash
cd $PWD && \
source <venv_path>/bin/activate && \
python3 tools/bitbucket_tool.py search-code <workspace> <query> \
  [--repo-slug <slug>]
```

#### Parameters:
- `workspace` (required): Workspace slug
- `query` (required): Text to search for
- `--repo-slug` (optional): Limit search to specific repository

#### Response Format:
```
File: src/config/database.py
  Match: DB_HOST = "prod-db.example.com"
  Match: DB_PORT = 5432

File: infrastructure/terraform/rds.tf
  Match: identifier = "prod-db"
```

#### Limitations:
- Code search may not be available on all Bitbucket plans
- Results are limited to 20 matches
- Search is text-based (not regex)

#### Best Practices:
- Use specific search terms (function names, configuration keys)
- Limit to a specific repo with `--repo-slug` for faster results
- Use this to find where specific code patterns or configurations exist

---

## Configuration Reference

The tool automatically reads these values from `engagement_agent_config.json`:

### Bitbucket Credentials:
```json
"bitbucket": {
  "email": "your-email@example.com",
  "api_token": "YOUR_BITBUCKET_SCOPED_API_TOKEN"
}
```

**IMPORTANT:** Bitbucket requires a **separate, scoped API token** from the Jira/Confluence token. Create it at: https://id.atlassian.com/manage-profile/security/api-tokens (select "Create API token with scopes" and enable all read permissions).

### Agent Defaults:
```json
"agent": {
  "bitbucket_workspace": "daemonsolutions",
  "bitbucket_project_key": "SUP"
}
```

---

## Decision Matrix: When to Use Direct vs Sub-Agent

### ⚡ Execute DIRECTLY (Simple Queries - 1-2 tool calls):

**Pattern:** Use bash to call `bitbucket_tool.py` directly from the orchestrator agent.

**Examples:**
- "What was the last pull request about?" → `get-latest-pull-request`
- "List repositories in SUP project" → `list-repositories`
- "Show me open PRs in windcheater" → `list-pull-requests`
- "Get details of PR #25" → `get-pull-request`

**Rationale:** ~50% more cost-efficient, faster execution (1 LLM call vs 3)

**Execution Pattern:**
```bash
cd $PWD && \
source venv/bin/activate && \
python3 tools/bitbucket_tool.py <command> <args>
```

---

### 🤖 Delegate to SUB-AGENT (Complex Queries - 3+ operations):

**Pattern:** Use Task tool to invoke `bitbucket-agent` for multi-step analysis.

**Examples:**
- "Compare PR activity across all SUP repositories" → Requires listing repos + querying PRs for each
- "Find all PRs related to Jira ticket SD-4674" → Requires searching across multiple repos and PRs
- "Analyze team code review patterns" → Requires aggregating data from multiple PRs
- "What's the development status of the Superdry project?" → Requires repos + PRs + commits + cross-referencing

**Rationale:** 3-12% more cost-efficient for complex queries, 50% faster (parallel execution), better quality (specialized knowledge)

**Execution Pattern:**
```
Use Task tool to invoke 'bitbucket-agent' with detailed instructions
```

---

## Common Workflows

### Workflow 1: "What was the last pull request about?"

**Approach:** Direct execution (FAST)

1. Check config for `bitbucket_workspace` and `bitbucket_project_key`
2. If multiple repos are configured, query each one
3. Use `get-latest-pull-request` with `--state MERGED`
4. Return the most recent based on creation date

**Example:**
```bash
# For windcheater repo
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions windcheater --state MERGED

# For laguna repo
python3 tools/bitbucket_tool.py get-latest-pull-request daemonsolutions laguna --state MERGED
```

---

### Workflow 2: Weekly Status Report - Pull Request Activity

**Approach:** Direct execution if single repo, delegate to sub-agent if multiple repos

**Single Repo:**
```bash
# Get recently merged PRs
python3 tools/bitbucket_tool.py list-pull-requests daemonsolutions windcheater --state MERGED --limit 20
```

**Multiple Repos:** Delegate to bitbucket-agent to aggregate across all repos

---

### Workflow 3: Cross-Referencing PR with Jira Ticket

**Approach:** Combination (Direct Bitbucket + Direct Jira or delegate if complex)

1. User mentions "Check SD-4674"
2. Get Jira ticket: `python3 tools/jira_tool.py get-ticket SD-4674`
3. Search for PR with "SD-4674" in title/description using `list-pull-requests`
4. If found, use `get-pull-request` for full details
5. Synthesize: Link PR status with Jira ticket status

---

### Workflow 4: Team Code Review Status

**Approach:** Delegate to sub-agent (COMPLEX)

1. Invoke bitbucket-agent with instructions to:
   - List all open PRs across repositories
   - Check approval status for each
   - Identify PRs waiting for review
   - Group by reviewer
   - Highlight blockers

---

## Error Handling

### Authentication Errors (401):
- **Cause:** Invalid or expired Bitbucket API token
- **Solution:** Regenerate token at https://id.atlassian.com/manage-profile/security/api-tokens
- **Remember:** Bitbucket token is SEPARATE from Jira/Confluence token

### Repository Not Found (404):
- **Cause:** Incorrect workspace or repo slug, or no access
- **Solution:** 
  1. Verify workspace slug with `list-workspaces`
  2. Verify repo slug with `list-repositories`
  3. Check if user has access to the repository

### Rate Limiting (429):
- **Cause:** Too many API requests in short time
- **Solution:** Add delays between requests, reduce batch sizes

---

## Best Practices Summary

1. **Always use config defaults:** Reference `agent.bitbucket_workspace` and `agent.bitbucket_project_key`
2. **Most recent PR query:** Use `get-latest-pull-request` - it's the most efficient
3. **Increase limits:** Default limits are conservative (10 results) - increase for comprehensive data
4. **Link to Jira:** Look for ticket references in PR titles/descriptions (e.g., "SD-4674")
5. **Check approval status:** Use PR participants to understand code review progress
6. **State matters:** Use `--state MERGED` for historical data, `OPEN` for current work
7. **Direct for simple, delegate for complex:** Follow the decision matrix above
8. **Always activate venv:** All Python tool executions MUST use the virtual environment

---

## Integration with Other Platforms

### Bitbucket + Jira:
- PR descriptions often reference Jira tickets (e.g., "fix(SD-4674)")
- Cross-reference PR activity with Jira ticket status
- Link merged PRs to "Done" tickets in WSRs

### Bitbucket + Slack:
- Pull request notifications appear in `pull_request_channel` (if configured)
- Cross-reference Slack PR discussions with actual PR details
- Use Bitbucket to verify PR status mentioned in Slack

### Bitbucket + Confluence:
- Document deployment processes with PR links
- Include PR summaries in Weekly Status Reports
- Reference repository structure in technical documentation

---

## Quick Reference

| User Query | Command | Approach |
|------------|---------|----------|
| "What was the last pull request about?" | `get-latest-pull-request` | ⚡ Direct |
| "List repos in SUP project" | `list-repositories --project-key SUP` | ⚡ Direct |
| "Show open PRs in windcheater" | `list-pull-requests --state OPEN` | ⚡ Direct |
| "Get PR #25 details" | `get-pull-request 25` | ⚡ Direct |
| "Recent commits in laguna" | `get-commits --limit 20` | ⚡ Direct |
| "Compare PR activity across all repos" | Multiple queries + synthesis | 🤖 Sub-Agent |
| "Analyze code review patterns" | Complex aggregation | 🤖 Sub-Agent |
| "Development status of project" | Multiple tools + cross-reference | 🤖 Sub-Agent |
