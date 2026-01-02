# Slide Window Command

When this command is called with `/slide-window`, perform a "sliding window" operation that preserves context while starting fresh in a new session.

## Purpose

This command helps manage long conversations by:
1. Summarizing the current session's key information
2. Saving it to your personal knowledge base for future reference
3. Starting a new session with the summary injected, allowing you to continue where you left off without the full conversation history

## Configuration (Optional)

To enable auto-execution of session transitions, configure your session start command:

### Method 1: Environment Variable
```bash
export OPENCODE_SESSION_CMD="unset AWS_VAULT && aws-vault exec daemon-ml -- opencode"
```

Add this to your `~/.bashrc`, `~/.zshrc`, or shell profile.

### Method 2: Config File
Add to `engagement_agent_config.json`:
```json
{
  "opencode_session_command": "unset AWS_VAULT && aws-vault exec daemon-ml -- opencode"
}
```

### Without Configuration
If no session command is configured, the command will display the full bash command for you to copy and run manually.

## Usage

```
/slide-window
```

Or with a custom title:

```
/slide-window "AWS Lambda Debugging Session"
```

## Command Execution Steps

### 1. Analyze Current Session

Analyze the entire current conversation and extract:
- **Key decisions made:** Technical choices, architectural decisions, problem resolutions
- **Important discoveries:** Bugs found, root causes identified, insights gained
- **Action items:** TODOs, follow-up tasks, pending work
- **Context needed for continuation:** Current state, what you're working on, next steps
- **Technical details:** Code snippets, commands, configurations, file paths
- **Learnings:** Best practices, gotchas, patterns to remember

### 2. Generate Session Summary

Create a comprehensive summary structured as follows:

```markdown
## Session Overview
[1-2 sentence overview of what this session was about]

## Key Decisions & Changes
- [Decision 1 with rationale]
- [Decision 2 with rationale]
- [Code/config changes made]

## Important Discoveries
- [Discovery 1]
- [Discovery 2]
- [Root causes, bugs, insights]

## Technical Details
- File paths: [relevant files worked on]
- Commands used: [important commands]
- Configuration: [key config changes]
- Code snippets: [critical code if needed]

## Current State
- What's working: [completed items]
- What's pending: [unfinished work]
- Next steps: [what to do next]

## Action Items
- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]

## Context for Continuation
[Any additional context needed to pick up where you left off - current problems, blockers, questions to investigate]
```

### 3. Determine Title

**If user provided a title in quotes:**
- Use the provided title

**If no title provided:**
- Generate a descriptive title based on the session content
- Format: "[Technology/Component] - [Main Activity/Topic]"
- Examples:
  - "AWS Lambda - Error Handling Implementation"
  - "OpenCode Dashboard - Port Configuration Debugging"
  - "Jira API - Authentication Setup"
- Show the generated title and ask for confirmation

### 4. Generate Tags

Auto-generate 3-7 relevant tags based on:
- Technologies mentioned (aws, python, docker, opencode, etc.)
- Activities performed (debugging, implementation, configuration, etc.)
- Domain/context (backend, frontend, devops, etc.)
- Project-specific terms from `engagement_agent_config.json` if relevant

Always include the tag: `session-summary`

Example tags: `aws, lambda, debugging, error-handling, session-summary`

### 5. Store to Knowledge Base

Use the `personal-knowledge_store_knowledge` tool with:
- `title`: The determined title
- `content`: The complete session summary in markdown format
- `tags`: Array of generated tags
- `source`: Optional - could include session ID if available

**Show confirmation:**
```
✅ Session summary stored to knowledge base
📝 Entry ID: #[id]
🏷️  Tags: [tags]
📊 You can retrieve this later with: /search-knowledge [key terms]
```

### 6. Create Continuation Context

Generate a concise handoff message for the new session:

```
Continuing from previous session: [Title]

Quick context:
- Working on: [main focus]
- Current state: [what's done]
- Next steps: [what to do next]
- Blockers: [any issues or questions]

[Include 2-3 most critical technical details needed immediately]

Full session details saved to knowledge base (Entry #[id])
Search with: /search-knowledge [relevant terms]
```

### 7. Determine Session Start Command

Check if there's a custom session start command configured:

1. **Read from config** (if exists): Check `engagement_agent_config.json` for `opencode_session_command`
2. **Read from environment**: Check `$OPENCODE_SESSION_CMD` environment variable
3. **Default**: Use `opencode` or `claude` as the base command

Common patterns:
- Simple: `opencode`
- With AWS Vault: `unset AWS_VAULT && aws-vault exec daemon-ml -- opencode`
- With environment: `ENV=prod opencode`

### 8. Execute Session Transition

**Option A: Auto-execute with Bash (Recommended)**
1. Format the continuation context as a single-line string (escape quotes)
2. Build the full command:
   ```bash
   [session_start_command] "Continuing from previous session: [Title]

   Quick context:
   - Working on: [main focus]
   - Current state: [what's done]
   - Next steps: [what to do next]

   Full session details saved to knowledge base (Entry #[id])
   Search with: /search-knowledge [relevant terms]"
   ```
3. Execute using Bash tool:
   - Run `/exit` first to close current session
   - Then execute the session start command in background
4. Note: The current CLI will exit, and the new session will start in the same terminal

**Option B: Display command to run manually**
1. Show the formatted command to copy/paste
2. Explain: "Copy this command and run it after this session exits"
3. Display with syntax highlighting for easy copying

**Option C: Update CLAUDE.md for persistent memory**
1. Check if `CLAUDE.md` exists in the project root
2. Append the session summary to `CLAUDE.md`:
   ```markdown
   ## Session Summary - [Date/Time]
   [Session title and continuation context]

   Full details in knowledge base: Entry #[id]
   ```
3. Inform user: "Summary added to CLAUDE.md. Start a new session and it will automatically load this context."

**Default behavior**: Use Option A if a session command is configured, otherwise use Option B.

### Example Output Flow

#### Example 1: With Configured Session Command (Auto-execute)

```
User: /slide-window

Agent: Analyzing current session...

I've summarized this session about OpenCode dashboard port configuration debugging.

**Suggested Title:** "OpenCode Dashboard - Express Server Port Configuration"
**Suggested Tags:** opencode, express, debugging, port-configuration, frontend, backend, session-summary

Store this summary? (yes/no/edit)

User: yes

Agent: ✅ Session summary stored to knowledge base
📝 Entry ID: #42
🏷️  Tags: opencode, express, debugging, port-configuration, frontend, backend, session-summary
📊 You can retrieve this later with: /search-knowledge opencode dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 STARTING NEW SESSION WITH CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Detected session start command: unset AWS_VAULT && aws-vault exec daemon-ml -- opencode

Executing: /exit
[Current session exits]

Starting new session with continuation context...
[New session starts with the summary as first message]
```

#### Example 2: Manual Mode (No Session Command Configured)

```
User: /slide-window

Agent: Analyzing current session...

I've summarized this session about OpenCode dashboard port configuration debugging.

**Suggested Title:** "OpenCode Dashboard - Express Server Port Configuration"
**Suggested Tags:** opencode, express, debugging, port-configuration, frontend, backend, session-summary

Store this summary? (yes/no/edit)

User: yes

Agent: ✅ Session summary stored to knowledge base
📝 Entry ID: #42
🏷️  Tags: opencode, express, debugging, port-configuration, frontend, backend, session-summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 CONTINUATION CONTEXT FOR NEW SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy and run this command after exiting:

unset AWS_VAULT && aws-vault exec daemon-ml -- opencode "Continuing from previous session: OpenCode Dashboard - Express Server Port Configuration

Quick context:
- Working on: Understanding OpenCode dashboard architecture
- Current state: Clarified that there's only one Express server on port 3030 serving both API and static files
- Next steps: Implement additional features or move to next task

Full session details saved to knowledge base (Entry #42)
Search with: /search-knowledge opencode dashboard"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run /exit when ready to switch sessions.
```

## Best Practices

1. **Be Comprehensive in Summaries:**
   - Include enough detail for your future self to understand
   - Don't assume you'll remember context
   - Include file paths, commands, and technical specifics

2. **Use Descriptive Titles:**
   - ✅ "AWS Lambda Timeout - Debug CloudWatch Throttling"
   - ❌ "Lambda stuff"

3. **Tag Strategically:**
   - Include technology stack
   - Include activity type (debugging, implementation, etc.)
   - Include domain/area
   - Always include `session-summary` tag

4. **Keep Continuation Context Concise:**
   - The full details are in the knowledge base
   - Only include what's immediately needed to continue
   - 3-5 bullet points maximum

5. **When to Use:**
   - ✅ Long debugging sessions before switching context
   - ✅ After completing a major feature/task
   - ✅ When approaching context limits
   - ✅ End of day to preserve progress
   - ❌ After trivial conversations
   - ❌ When no meaningful work was done

## Error Handling

- **If MCP server is not responding:**
  - Show error message
  - Ask if user wants to store summary to a markdown file instead
  - Save to `~/.opencode/session-summaries/[timestamp]-[title].md`

- **If session is too short/trivial:**
  - Warn user: "This session doesn't have much content to preserve. Continue anyway? (yes/no)"
  - Allow user to abort

- **If session transition fails:**
  - Ensure summary is already safely stored in knowledge base
  - Provide the continuation context as formatted text
  - Offer all three options (CLI command, CLAUDE.md, manual copy)
  - Remind user that full summary is retrievable via `/search-knowledge`

## Related Commands

- `/store-knowledge` - Store specific information without starting a new session
- `/search-knowledge` - Search previously saved session summaries and knowledge
- `/exit` - Exit current session (used before starting a new session)
- `/resume` - Resume a previous session by name or ID
