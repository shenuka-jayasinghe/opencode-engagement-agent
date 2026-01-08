---
description: Generate Weekly Status Report in Confluence
---

## Overview

This command duplicates the latest WSR and only updates specific fields based on the reporting period:
- **Updated Fields:** Reporting Period, Executive Summary, Key Achievements, Upcoming Activities
- **Unchanged Fields:** Blockers, RAID, Service Improvements, Contacts, all other sections
- **Default Period:** 7 days (if not specified)

## Steps

1. **Ask for Latest WSR URL:**
   - **FIRST ACTION:** Ask the user: "Please provide the URL of the latest WSR, or type 'search' to find it automatically"
   - **If user provides URL:**
     - Parse URL to extract: space key, page ID
     - Fetch content: `python3 tools/confluence_tool.py get-page-content [page_id]`
     - Extract from previous WSR:
       - **Title format** (e.g., "Weekly Status Report 2025-12-19" vs "WSR - 2025-12-19")
       - **Parent directory** using API with `?expand=ancestors`
       - **All content sections** for duplication
     - Verify URL path format for later use
   - **If user says 'search':** Proceed to step 2 to search automatically

2. **Configuration & Space Selection (if searching automatically):**
   - Use subagent skills and config for information gathering on bitbucket, conflunce, jira and slack
   - Read `config/engagement_agent_config.json`
   - Extract: `confluence_space_key`, `wsr_template_url`, `client_name`, `programme_name`, `jira_project_key`, `slack_channel_ids`, `bitbucket_workspace`, `bitbucket_project_key`
   - **Determine WSR Space:**
     - Parse `wsr_template_url` to extract space key from URL (e.g., `/spaces/SDRY/` → space is `SDRY`)
     - Use this space key for ALL Confluence operations
   - Calculate reporting period (default: last 7 days unless specified)
   - Output to user: "Using Confluence space: [SPACE_KEY] for WSR generation"

3. **Find Latest WSR (if not provided by user):**
   - Search for recent WSRs: `python3 tools/confluence_tool.py search [SPACE_KEY] "Weekly Status Report" --title-only --limit 5`
   - Look for patterns: "WSR - YYYY-MM-DD" or "Weekly Status Report YYYY-MM-DD"
   - Sort by date, select most recent
   - Fetch most recent WSR content: `python3 tools/confluence_tool.py get-page-content [recent_wsr_page_id]`
   - Extract:
     - **Title Format:** Note exact title format from search results
     - **Parent Directory:** Use API with `?expand=ancestors` to get parent page ID and title
     - **All sections:** Store complete content for duplication
   - Store for later: `parent_id`, `title_format`, `previous_wsr_content`

4. **Gather Information for Updated Fields:**
   - **Determine Reporting Period:**
     - Default: 7 days ending today (unless user specified different period)
     - Calculate start/end dates

   - **Bitbucket - Merged PRs:**
     - List repos: `python3 tools/bitbucket_tool.py list-repositories`
     - For each repo, get merged PRs in reporting period: `list-pull-requests <repo> --state MERGED --limit 20`
     - Extract: PR title, branch, author, reviewers, Jira ticket IDs (pattern: `[JIRA_PROJECT_KEY]-\d+`), merge date, URL
     - Build ticket→PR map for cross-reference

   - **Jira - Tickets:**
     - Get tickets for reporting period: `python3 tools/jira_tool.py get-summary --project-key [JIRA_PROJECT_KEY] --days [PERIOD_DAYS] --max-results 100`
     - Cross-reference with PR map: enrich tickets with PR details
     - Identify: completed tickets (Done/Resolved/Closed), in-progress tickets
     - Validate extracted tickets: `get-ticket <number>` if not in summary

   - **Bitbucket - Open PRs:**
     - Get open PRs at end of period: `list-pull-requests <repo> --state OPEN --limit 10`
     - Extract associated Jira tickets

   - **Slack - Messages:**
     - For each channel in `slack_channel_ids`: `python3 tools/slack_tool.py get-channel-summary <id> <start> <end> --limit 500`
     - Identify unresolved discussions/questions (conversations without resolution)
     - Cross-reference with Jira: exclude conversations where associated ticket is resolved/closed

5. **Generate Updated Content:**

   - **Reporting Period:**
     - Format: "Week X (YYYY-MM-DD - YYYY-MM-DD)"
     - Calculate week number and format dates

   - **Key Achievements (UPDATED):**
     - Start with merged PRs, enrich with Jira context
     - Format: "[Jira Summary] ([Ticket ID])" or "[Summary] (ID - repos)" for multi-repo
     - Include "Done" tickets without PRs (non-code work)
     - Sort by importance (customer-facing, critical first)
     - Pipe-separated list
     - **Jira References:** Use plain text IDs (e.g., "SD-1234"); wsr_tool.py auto-converts to links

   - **Upcoming Activities (UPDATED):**
     - Open PRs at end of period: "[Jira Summary] - in code review (ID)"
     - In-progress tickets: "[Jira Summary] - in progress (ID)"
     - Unresolved Slack conversations (where Jira ticket not resolved): Brief description with context
     - Sort by priority, pipe-separated

   - **Executive Summary (UPDATED):**
     - 2-3 sentences summarizing the reporting period
     - Count completed items from achievements
     - Highlight major achievements
     - Mention any critical upcoming items
     - Note: Blocker count remains same as previous WSR (not recalculated)

6. **Generate WSR:**
   - Activate venv: `cd $PWD && source venv/bin/activate`
   - **Use Title Format from Latest WSR:** Match exact format (e.g., "Weekly Status Report YYYY-MM-DD" or "WSR - YYYY-MM-DD")
   - **Use Parent ID from Latest WSR:** Use extracted parent_id
   - **Calculate new date:** End date of reporting period

   - Run: `python3 tools/wsr_tool.py --space-key "[SPACE_KEY]" --title "[TITLE_FORMAT] YYYY-MM-DD" --parent-id "[PARENT_ID]" --period "Week X (YYYY-MM-DD - YYYY-MM-DD)" --summary "..." --achievements "...|..." --upcoming "...|..." --blockers "..." --client "[CLIENT_NAME]" --programme "[PROGRAMME_NAME]" --status-color "Green"`

   - **Example:** `--title "Weekly Status Report 2026-01-07" --parent-id "50703073291"`

   - **CRITICAL:**
     - Pass blockers, RAID, and service improvements EXACTLY as they appear in previous WSR
     - Tool auto-converts Jira IDs to links
     - Do not delete tool/templates
     - Capture the Confluence page ID from output

7. **Verify Page Creation:**
   - Search for the newly created page: `python3 tools/confluence_tool.py search [SPACE_KEY] "[TITLE_FORMAT] YYYY-MM-DD" --title-only --limit 1`
   - If NOT found: Report error - "WSR creation failed - page not found in Confluence space [SPACE_KEY]"
   - If found: Extract page ID and webui path from search results
   - **URL Construction:**
     - From search results, get `_links.webui` field (e.g., "/spaces/SDRY/pages/51617366018/Weekly+Status+Report+2026-01-07")
     - Build full URL: `https://daemonsolutions.atlassian.net/wiki` + `webui_path`
     - **CRITICAL:** Do NOT add duplicate `/wiki/wiki/` - only use `/wiki/` once
   - Verify URL matches format from latest WSR
   - **Verify Parent Directory:** Confirm parent matches latest WSR

8. **Verify Updated Fields:**
   - Fetch generated WSR content: `python3 tools/confluence_tool.py get-page-content <page_id>`
   - Verify:
     - **Reporting Period:** Matches specified period
     - **Executive Summary:** Updated with new content
     - **Key Achievements:** Shows merged PRs and completed tickets from reporting period
     - **Upcoming Activities:** Shows open PRs, in-progress tickets, unresolved Slack items
     - **Unchanged sections:** Blockers, RAID, Service Improvements match previous WSR exactly
   - Report any discrepancies to user

9.  **Return to User:**
   - **ONLY if page verified:** Return verified WSR URL and summary
   - **URL Format:** `https://daemonsolutions.atlassian.net/wiki/spaces/[SPACE]/pages/[ID]/[TITLE]`
   - **Example Output:** "WSR created: https://daemonsolutions.atlassian.net/wiki/spaces/SDRY/pages/51617366018/Weekly+Status+Report+2026-01-07"
   - Include:
     - Latest WSR link used as reference
     - Reporting period used
     - Count of achievements added
     - Count of upcoming activities
     - Confirmation that other sections duplicated unchanged

10. **Open Browser:**
    - **ONLY if URL verified:** `open [verified_confluence_url]`
    - If verification failed, skip this step and report error

## Key Principles

- **Duplication-First:** Copy the entire previous WSR structure
- **Minimal Changes:** Only update Reporting Period, Executive Summary, Achievements, Upcoming Activities
- **Preserve History:** Blockers, RAID, Service Improvements carry forward unchanged
- **Default Period:** 7 days unless user specifies otherwise
- **Jira Integration:** Auto-link all Jira ticket IDs in the final report
- **Verification:** Always verify page creation and updated fields before returning URL
