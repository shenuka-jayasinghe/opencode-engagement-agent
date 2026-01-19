---
description: Generate Weekly Status Report in Confluence
---

## Overview

This command duplicates the latest WSR and only updates specific fields based on the reporting period:
- **Updated Fields:** Reporting Period, Executive Summary, Key Achievements, Upcoming Activities
- **Unchanged Fields:** Blockers, RAID, Service Improvements, Contacts, all other sections
- **Default Period:** 7 days (if not specified)

## Steps

1. **Ask for Latest WSR URL and Reporting Period:**
   - **FIRST ACTION:** Ask the user: "Please provide the URL of the latest WSR (or type 'search') AND confirm if you want the report for the past 7 days or specify a custom period."
   - **If user provides URL:**
     - Parse URL to extract: space key, page ID
     - **DELEGATE to confluence-agent:** Fetch content and parent info using Task tool
     - Extract from previous WSR:
       - **Title format** (e.g., "Weekly Status Report 2025-12-19" vs "WSR - 2025-12-19")
       - **Parent directory** using API with `?expand=ancestors`
       - **All content sections** for duplication
     - Verify URL path format for later use
   - **If user says 'search':** Proceed to step 2 to search automatically
   - **Parse Reporting Period:** Note the user's preference (7 days vs custom dates) for use in Step 4.

2. **Configuration & Space Selection (if searching automatically):**
   - Read `config/engagement_agent_config.json`
   - Extract: `confluence_space_key`, `wsr_template_url`, `client_name`, `programme_name`, `jira_project_key`, `slack_channel_ids`, `bitbucket_workspace`, `bitbucket_project_key`
   - **Determine WSR Space:**
     - Parse `wsr_template_url` to extract space key from URL (e.g., `/spaces/SDRY/` → space is `SDRY`)
     - Use this space key for ALL Confluence operations
   - Calculate reporting period (default: last 7 days unless specified)
   - Output to user: "Using Confluence space: [SPACE_KEY] for WSR generation"

3. **Find Latest WSR (if not provided by user):**
   - **DELEGATE to confluence-agent:** Use Task tool to search for recent WSRs
     - Search for: "Weekly Status Report" with `--title-only --limit 5`
     - Look for patterns: "WSR - YYYY-MM-DD" or "Weekly Status Report YYYY-MM-DD"
     - Sort by date, select most recent
     - Fetch most recent WSR content including parent info
   - Extract:
     - **Title Format:** Note exact title format from search results
     - **Parent Directory:** Parent page ID and title
     - **All sections:** Store complete content for duplication
   - Store for later: `parent_id`, `title_format`, `previous_wsr_content`

4. **Gather Information for Updated Fields - START WITH BITBUCKET:**
   - **Determine Reporting Period:**
     - Default: 7 days ending today (unless user specified different period)
     - Calculate start/end dates

   - **CRITICAL: Use PR merge dates as PRIMARY source of truth for completed work**
   
   - **STEP 4.1 - Get PR Data (Use bitbucket_tool.py directly):**
     - List all repositories in project: `python3 tools/bitbucket_tool.py list-repositories [workspace] --project-key [PROJECT_KEY]`
     - For EACH repository, get PRs:
       - **Merged PRs:** `python3 tools/bitbucket_tool.py list-pull-requests [workspace] [repo_slug] --state MERGED --limit 50`
         - Filter by **created date** within reporting period (check "Created: YYYY-MM-DD" in output)
         - Extract: PR number, title, created date, Jira ticket IDs (pattern: `SD-\d+` case-insensitive)
       - **Open PRs:** `python3 tools/bitbucket_tool.py list-pull-requests [workspace] [repo_slug] --state OPEN --limit 20`
         - Extract: PR number, title, Jira ticket IDs
     - Build comprehensive lists:
       - `merged_prs`: All PRs merged in period with {repo, pr_num, title, date, jira_id}
       - `open_prs`: All currently open PRs with {repo, pr_num, title, jira_id}
     - Create ticket→PR mapping for cross-reference

   - **STEP 4.2 - Verify Work with Jira:**
     - For each unique Jira ticket ID from merged PRs:
       - Use `python3 tools/jira_tool.py get-ticket [TICKET_ID]` to get full summary
       - Verify ticket exists and get proper description
     - For open PRs with Jira IDs:
       - Get ticket status to confirm it's "In Progress" or similar
     
   - **STEP 4.3 - Supplement with Non-Code Work (Optional):**
     - Search for completed tickets WITHOUT associated PRs (non-code work):
       - `python3 tools/jira_tool.py search-tickets "project=SD AND resolved >= [START_DATE] AND resolved <= [END_DATE]"`
       - Check if ticket has associated PR from step 4.1
       - If no PR exists, include as standalone achievement (e.g., documentation, manual tasks)

5. **Synthesize Data and Generate Updated Content:**

   - **Cross-Reference Data:** 
     - Primary source: Merged PRs from Bitbucket (Step 4.1)
     - Enrich each PR with Jira ticket summary (Step 4.2)
     - Group PRs by Jira ticket (multiple PRs may relate to same ticket)
     - Add non-code completed work from Jira (Step 4.3)
     - Link open PRs to their Jira tickets

   - **Reporting Period:**
     - Format: "Week X (YYYY-MM-DD - YYYY-MM-DD)"
     - Calculate week number and format dates

   - **Key Achievements (UPDATED):**
      - **PRIMARY SOURCE:** Merged PRs from reporting period
      - For each Jira ticket with merged PR(s):
        - Format: "[Jira Ticket Summary] ([Ticket ID] - repo)" 
        - If multiple PRs for same ticket: "[Summary] ([Ticket ID] - repo1, repo2)"
        - Example: "Matillion Hub migration - upgrade to v1.75.40 (SD-4674 - windcheater)"
      - For PRs without Jira tickets:
        - Format: "[Brief description from PR title] (repo)"
        - Example: "Upgrade Terraform to v1.14.3 (laguna, pipeline, datatransfer)"
      - Include completed Jira tickets WITHOUT PRs (non-code work) if significant
      - Sort by importance (customer-facing, migrations, critical infrastructure first)
      - Pipe-separated list
      - **Jira References:** Use plain text IDs (e.g., "SD-1234"); wsr_tool.py auto-converts to links

   - **Upcoming Activities (UPDATED):**
     - **PRIMARY SOURCE:** Open PRs from Bitbucket
     - For each open PR:
       - Format: "[Jira Ticket Summary] - in code review ([Ticket ID] - repo)"
       - Example: "Image converter system - in code review (SD-4735 - laguna)"
     - Include in-progress Jira tickets without open PRs if significant
     - Sort by priority, pipe-separated

   - **Executive Summary (UPDATED):**
     - **CRITICAL:** Client-facing language - focus on BUSINESS VALUE, not technical details
     - 2-3 sentences summarizing the reporting period
     - Use professional but human tone with first-person plural ("we") language
     - Count: "[X] completed items" OR "[X] key accomplishments" 
     - Highlight: Business impact of major achievements (e.g., "migration", "optimization", "enhancement")
     - Mention: Any critical upcoming items
     - **AVOID:** Technical details like "PRs", "merge conflicts", "repo names", "terraform versions"
     - **GOOD:** "We completed the Matillion Hub migration and infrastructure updates"
     - **BAD:** "We merged 17 PRs including 4 PRs to resolve merge conflicts in laguna repo"
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
    - **DELEGATE to confluence-agent:** Use Task tool to verify the newly created page
      - Search for the newly created page with exact title
      - Extract page ID and webui path from search results
    - If NOT found: Report error - "WSR creation failed - page not found in Confluence space [SPACE_KEY]"
    - If found: 
      - **URL Construction:**
        - From search results, get `_links.webui` field (e.g., "/spaces/SDRY/pages/51617366018/Weekly+Status+Report+2026-01-07")
        - Build full URL: `[confluence.server from config]` + `webui_path`
        - **CRITICAL:** Do NOT add duplicate `/wiki/wiki/` - the server URL includes `/wiki/` if needed
      - Verify URL matches format from latest WSR
      - **Verify Parent Directory:** Confirm parent matches latest WSR

8. **Verify Updated Fields:**
   - **DELEGATE to confluence-agent:** Fetch generated WSR content
   - Verify:
     - **Reporting Period:** Matches specified period
     - **Executive Summary:** Updated with new content
     - **Key Achievements:** Shows merged PRs and completed tickets from reporting period
     - **Upcoming Activities:** Shows open PRs, in-progress tickets, unresolved Slack items
     - **Unchanged sections:** Blockers, RAID, Service Improvements match previous WSR exactly
   - Report any discrepancies to user

 9.  **Return to User:**
    - **ONLY if page verified:** Return verified WSR URL and summary
    - **URL Format:** `[confluence.server from config]/wiki/spaces/[SPACE]/pages/[ID]/[TITLE]`
    - **Example Output:** "WSR created: [confluence.server]/wiki/spaces/SDRY/pages/51617366018/Weekly+Status+Report+2026-01-07"
   - Include:
     - Latest WSR link used as reference
     - Reporting period used
     - Count of achievements added
     - Count of upcoming activities
     - Confirmation that other sections duplicated unchanged

10. **Open Browser:**
    - **ONLY if URL verified:** `open [verified_confluence_url]`
    - If verification failed, skip this step and report error

## Execution Strategy

This command uses Bitbucket PRs as the primary source of truth for work completed.

### Data Gathering Strategy:

**Step 4 - PR-First Approach:**
1. **Bitbucket PRs (DIRECT):** Use `bitbucket_tool.py` directly to get all merged and open PRs
   - Fastest and most accurate method
   - Filter by created date to identify work in reporting period
   - Extract Jira ticket IDs from PR titles
   
2. **Jira Verification (DIRECT):** Use `jira_tool.py` directly to:
   - Get full ticket summaries for each Jira ID found in PRs
   - Supplement with non-code work (tickets without PRs)

3. **Slack (OPTIONAL):** Only if specifically requested by user
   - Can identify unresolved discussions or blockers
   - Not part of standard WSR generation flow

**Why Direct Tool Usage:**
- 50% cheaper than delegating to sub-agents
- Faster (1 LLM call vs 3)
- Full control over data filtering and processing
- Clear visibility into what data is being gathered

**When to Use Sub-Agents:**
- Only for complex queries requiring interpretation
- Only when user specifically requests comprehensive Slack analysis
- NOT for standard WSR generation

### Key Principles

- **PR-First Methodology:** Bitbucket PRs are source of truth for completed work
- **Date Accuracy:** Use PR created/merged dates, not Jira resolution dates
- **Client-Facing Language:** Executive summary must focus on business value, not technical details
- **Minimal Changes:** Only update Reporting Period, Executive Summary, Achievements, Upcoming Activities
- **Preserve History:** Blockers, RAID, Service Improvements carry forward unchanged
- **Default Period:** 7 days unless user specifies otherwise
- **Jira Integration:** Auto-link all Jira ticket IDs in the final report
- **Verification:** Always verify page creation and updated fields before returning URL
