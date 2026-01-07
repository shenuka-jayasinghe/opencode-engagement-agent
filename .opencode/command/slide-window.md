---
description: Summarize current session, save to vectordb, and continue in a new session
---

**Execution:** DIRECT by Orchestrator (DO NOT delegate). You hold full context; delegation is inefficient.

## Purpose
Slide context window for long sessions:
1. **Synthesize:** Summarize decisions, technical details, next steps
2. **Persist:** Save to `personal-knowledge_store_knowledge`
3. **Restart:** Fresh session with summary injected

## Steps

1. **Summarize:** Review history, extract: goal, achievements (decisions, code changes), current state (files modified, pending tasks), next steps. Verify technical accuracy (IDs, paths, commands).

2. **Store:** Use `personal-knowledge_store_knowledge` with descriptive title, structured content, tags (`session-summary` + tech tags)

3. **Start New Session:**
   - Get profile from `engagement_agent_config.json` (`aws_bedrock.aws_profile`)
   - Execute: `unset AWS_VAULT && aws-vault exec <profile> -- opencode run "Continuing from '<Title>'. Context: <Summary>. Do nothing until further instructions."`
   - Capture output

4. **Get Session ID:** Parse output for `ses_...`. Fallback: `opencode session list` (second most recent, not current)

5. **Handoff:** Inform user, instruct: `opencode -s <NEW_SESSION_ID>` (NOT `opencode -c`)
