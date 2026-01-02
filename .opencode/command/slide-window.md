---
description: Summarize current session, save to vectordb, and continue in a new session
---

# Slide Window Command

**Trigger:** `/slide-window`

**Execution Mode:** DIRECT execution by the Orchestrator Agent.
*   **CRITICAL: DO NOT** delegate this to a sub-agent.
*   **Efficiency Rationale:** The Orchestrator Agent (You) already holds the full conversation context in memory. Delegating to a sub-agent would require passing this massive context, which is inefficient, slow, and prone to data loss. You are the most capable model (Claude 3.5 Sonnet) for this complex summarization task. Direct execution is faster and higher quality.

## Purpose
Manage long-running sessions by "sliding the window" of context:
1.  **Synthesize:** Summarize key decisions, technical details, and next steps from the current session.
2.  **Persist:** Save this summary to the personal knowledge base (`personal-knowledge_store_knowledge`) for semantic retrieval.
3.  **Restart:** seamless transition to a fresh session with the summary injected.

## Execution Steps

1.  **Analyze & Summarize:**
    Review the full conversation history. Extract:
    *   Goal of the session
    *   What was achieved (decisions, discoveries, code changes)
    *   Current state (files modified, pending tasks)
    *   Immediate next steps
    *   *Self-Correction:* Ensure technical details (IDs, paths, commands) are accurate.

2.  **Store Knowledge:**
    *   **Tool:** `personal-knowledge_store_knowledge`
    *   **Title:** Descriptive title (e.g., "Laguna Transfers Investigation")
    *   **Content:** The structured summary.
    *   **Tags:** Include `session-summary` + relevant tech tags.

3.  **Start New Session:**
    *   **Retrieve Profile:** Get `aws_bedrock.aws_profile` from `engagement_agent_config.json`.
    *   **Construct Command:**
        ```bash
        unset AWS_VAULT && aws-vault exec <profile> -- opencode run "Continuing from session '<Title>'. Context: <Summary>. Do nothing until further instructions are given"
        ```
    *   **Execute:** Run the command using the `bash` tool. **Capture the output.**

4.  **Identify New Session ID:**
    *   Parse the output of the `opencode run` command to find the new Session ID (typically `ses_...`).
    *   *Fallback:* If the ID isn't in the output, run `opencode session list` to find the not the most recent, but the one before the most recent. The most recent is the current session ID which we don't want.

5.  **Handoff:**
    *   Inform the user the new session has started.
    *   **CRITICAL:** Instruct them to exit and run the specific connection command:
        `opencode -s <NEW_SESSION_ID>`
        (Do NOT recommend `opencode -c` as it defaults to the old session).
