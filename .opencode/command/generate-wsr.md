---
description: Generate Weekly Status Report in Confluence
agent: general
---

## Steps

1. **Template Analysis:**
   - Get `wsr_template_url` from config
   - Find 2-3 recent WSRs: `python3 tools/confluence_tool.py search SDRY "Weekly Status Report" --title-only --limit 3`
   - Fetch most recent WSR content, **extract "Blockers" section** (carry forward unless resolved)
   - Note format: header table, executive summary, main table (achievements/green, upcoming/yellow, blockers/red), RAID, contacts
   - Get `parent_id` and `space_key` from template

2. **Configuration:** Read config for: `confluence_space_key`, `slack_channel_ids`, `recipient_emails_to_scan`, `jira_project_key`, `client_name`, `programme_name`. Calculate last 7 days.

3. **Gather Information:**
   - **Bitbucket (First):**
     - Get workspace/project from config
     - List repos: `python3 tools/bitbucket_tool.py list-repositories`
     - For each repo, get merged PRs (7-day window): `list-pull-requests <repo> --state MERGED --limit 20`
     - Extract Jira ticket numbers from branches/titles (pattern: `SD-\d+`)
     - Extract: PR title, branch, author, reviewers, tickets, merge date, URL
     - Build ticket→PR map for cross-reference
   - **Jira:** `python3 tools/jira_tool.py get-summary --project-key <key> --days 7 --max-results 100`
     - Cross-reference with PR map: enrich tickets with PR details
     - Validate extracted tickets: `get-ticket <number>` if not in summary
   - **Slack:** `python3 tools/slack_tool.py get-channel-summary <id> <start> <end> --limit 500`
   - **Gmail:** `python3 tools/gmail_tool.py search-emails --senders "<emails>" --start-date <date> --end-date <date> --max-results 50`

4. **Synthesize Content:**
   - **Blockers:** Parse from previous WSR; carry forward unless resolved (ticket Done/Resolved/Closed, mentioned in Slack/email, or in this week's achievements)
   - **Key Achievements:**
     - Start with merged PRs, enrich with Jira context (use ticket summary, not PR title)
     - Format: "[Jira Summary] ([Ticket ID])" or "[Summary] (ID - repos)" for multi-repo
     - Include "Done" tickets without PRs (non-code work)
     - Sort by importance (customer-facing, critical first)
     - Pipe-separated list
   - **Upcoming Activities:**
     - Get open PRs: `list-pull-requests <repo> --state OPEN --limit 10`
     - Extract tickets, format: "[Jira Summary] - in code review (ID)" or "- in progress (ID)"
     - Add "In Progress" tickets and planned work from Slack/email
     - Sort by priority, pipe-separated
   - **Executive Summary:** 2-3 sentences: count completed items, highlight major achievements, note blockers
   - **Integration Tips:** Verify tickets, use Jira summaries (not PR titles), build ticket→PR map, handle edge cases (multi-repo PRs, no-ticket PRs, no-PR tickets)
   - **Jira References:** Use plain text IDs (e.g., "SD-1234"); wsr_tool.py auto-converts to links

5. **Generate WSR:**
   - Activate venv: `cd $PWD && source venv/bin/activate`
   - Run: `python3 tools/wsr_tool.py --space-key "SDRY" --title "WSR - YYYY-MM-DD" --parent-id "..." --period "Week X (...)" --summary "..." --achievements "...|..." --upcoming "...|..." --blockers "..." --client "..." --programme "..." --status-color "Green"`
   - Tool auto-converts Jira IDs to links
   - **Do not delete tool/templates**

6. **Verify Format:**
   - Fetch generated WSR: `get-page-content`
   - Compare to reference WSRs from step 1
   - Check: header table fields, executive summary, colored sections, Jira links, HTML structure
   - Report differences to user

7. **Return:** WSR URL, reference WSR links, format confirmation/differences

8. **Open Browser:** `open [new_confluence_url]` for visual confirmation
