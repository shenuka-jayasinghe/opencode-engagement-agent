---
description: Generate Weekly Status Report in Confluence
agent: general
---

When this command is called, perform the following steps:

1.  **Template Analysis and Format Reference:**
    *   Read `engagement_agent_config.json` to get the `wsr_template_url`.
    *   Use `tools/confluence_tool.py search` to find the 2-3 most recent WSRs in the SDRY space using:
        ```bash
        python3 tools/confluence_tool.py search SDRY "Weekly Status Report" --title-only --limit 3
        ```
    *   Fetch the content of the most recent WSR using `get-page-content`:
        - **CRITICAL:** Parse and extract the "Blockers" section content from the most recent WSR
        - These blockers will be carried forward to the new WSR unless explicitly resolved
        - Also extract 1-2 other recent WSRs for format comparison
    *   **Store these URLs for format verification later:** These will be used to verify that the generated WSR matches the established format.
    *   **Key format elements to note:**
        - Header table structure (Client, Programme, Reporting Period, Engagement Status, Indicative End Date)
        - Executive Summary section
        - Main table with Key Achievements (green), Upcoming Activities (yellow), Blockers (red/orange)
        - Service Improvements and Risk Mitigation table
        - RAID table
        - Two-column layout at bottom with Client Contacts and Daemon Contacts
    *   Use `tools/confluence_tool.py get-page-info` on the `wsr_template_url` to find the `parent_id` and `space_key`.

2.  **Read the Configuration:**
    *   Read `engagement_agent_config.json` to get `confluence_space_key`, `slack_channel_ids`, `recipient_emails_to_scan`, `jira_project_key`, `client_name`, `programme_name`, and date range.
    *   Calculate the date range for the last 7 days.

3.  **Gather Information:**
    *   **Slack:** Get summaries from `slack_channel_ids` for the last 7 days using:
        ```bash
        python3 tools/slack_tool.py get-channel-summary <channel_id> <start_date> <end_date> --limit 500
        ```
    *   **Gmail:** Get summaries of relevant emails using:
        ```bash
        python3 tools/gmail_tool.py search-emails --senders "<emails>" --start-date <date> --end-date <date> --max-results 50
        ```
    *   **Jira:** Get a summary of recent tickets using:
        ```bash
        python3 tools/jira_tool.py get-summary --project-key <key> --days 7 --max-results 100
        ```
    *   **Bitbucket:** Get pull request activity for the reporting period:
        *   Read `engagement_agent_config.json` to get `bitbucket_workspace` and `bitbucket_project_key`
        *   For each key repository in the project, get recently merged PRs using:
            ```bash
            python3 tools/bitbucket_tool.py list-pull-requests <workspace> <repo_slug> --state MERGED --limit 20
            ```
        *   **Cross-reference with Jira:** Match PR descriptions/titles with Jira ticket numbers (e.g., "SD-4674")
        *   **Filter by date:** Only include PRs merged within the 7-day reporting window (check "Created" dates)
        *   **Key data to extract:**
            - PR title and description
            - Author and reviewers
            - Related Jira ticket numbers
            - Merge date and target branch
        *   **Approach:**
            - For 1-2 repositories: Execute bitbucket_tool.py directly for each repo
            - For 3+ repositories: Consider delegating to bitbucket-agent for parallel execution
    *   **Confluence:** Get the `parent_id` from the `wsr_template_url` using `get-page-info`.

4.  **Synthesize Content:**
    *   **Extract blockers from the most recent WSR:**
        - From the most recent WSR content (fetched in step 1), parse the "Blockers" section
        - Carry forward all existing blockers UNLESS there is explicit evidence they have been resolved
        - Evidence of resolution includes:
          * Jira ticket status changed to "Done", "Resolved", or "Closed"
          * Explicit mention in Slack/email that the blocker is resolved
          * The blocker ticket appears in "Key Achievements" for this week
        - If no blockers exist in the previous WSR, start with an empty list
    *   Analyze all gathered information to create:
        - **Executive Summary:** 2-3 sentences capturing the week's key themes
        - **Key Achievements:** 
          * Start with completed Jira tickets from "Done" status
          * Cross-reference with merged Bitbucket PRs to find associated work
          * Include PR titles and link to Jira tickets (e.g., "Fix windcheater pipeline (SD-4702)")
          * Format as pipe-separated list
          * Example: "Deployed matillion hub RDS (SD-4674)|Updated fashion parameter store permissions (SD-4698)|Fixed pipeline assume role error (SD-4534)"
        - **Upcoming Activities:** 
          * Start with "In Progress" Jira tickets
          * Add planned work mentioned in Slack/email
          * Cross-reference with open PRs in Bitbucket for work in code review
          * Format as pipe-separated list
        - **Blockers:** 
          * Start with blockers carried forward from previous WSR
          * Add any NEW blockers identified from this week's communications
          * Remove blockers only if explicitly resolved (see criteria above)
          * Use "None" only if no blockers exist at all
    *   **Jira and Bitbucket Integration:**
        - Use PR information to enrich Jira ticket context
        - If a Jira ticket is "Done" but has a merged PR, include the PR details
        - If a Jira ticket is "In Progress" with an open PR, note it's in code review
        - Link PR activity to demonstrate tangible progress
    *   **Jira Ticket References:** Simply use plain text Jira ticket IDs (e.g., "SD-1234") in any section. The wsr_tool.py will automatically convert them to proper Confluence links. You can also provide pre-formatted links if you prefer, and they will be preserved.
        - Example: "Fix windcheater pipeline (SD-4702)" will be automatically converted to use proper links
        - Pre-formatted links like `<a href="...">SD-4702</a>` will also work

5.  **Generate the WSR:**
    *   Use the stable `tools/wsr_tool.py` script to generate the HTML and create the page in Confluence.
    *   **IMPORTANT:** Always activate the virtual environment first:
        ```bash
        cd $PWD && source venv/bin/activate && python3 tools/wsr_tool.py \
          --space-key "SDRY" \
          --title "Weekly Status Report - YYYY-MM-DD" \
          --parent-id "123456789" \
          --period "Week X (YYYY-MM-DD - YYYY-MM-DD)" \
          --summary "Executive summary text..." \
          --achievements "Achievement 1|Achievement 2|Fixed deployment issue (SD-4702)" \
          --upcoming "Task 1|Task 2" \
          --blockers "None" \
          --client "Superdry" \
          --programme "Managed Service (SD0002 EXT003)" \
          --status-color "Green"
        ```
    *   **Note:** The tool will automatically convert Jira ticket references (like SD-4702) to clickable links.
    *   **CRITICAL:** Do not delete the tool or any templates after use.

6.  **Format Verification:**
    *   After generating the WSR, fetch its content using `get-page-content`.
    *   Compare the generated WSR structure against the 2-3 reference WSRs you fetched in step 1.
    *   **Verify:**
        - Header table has all required fields (Client, Programme, Reporting Period, Engagement Status, Indicative End Date)
        - Executive Summary section exists and is properly formatted
        - Main table has the three colored sections (Key Achievements, Upcoming Activities, Blockers)
        - All Jira ticket references are properly linked (not plain text)
        - Overall HTML structure matches the reference format
    *   If significant format differences are detected, report them to the user.

7.  **Return Results:**
    *   Provide the user with:
        - URL of the newly created WSR
        - Links to the 2-3 reference WSRs used for format verification
        - Confirmation that format matches previous WSRs (or note any differences)

8.  **Open in Browser:**
    *   After generating the WSR, verify the Confluence link is correct.
    *   Open the newly created WSR in the user's default browser using:
        ```bash
        open [new_confluence_document_link]
        ```
    *   This provides immediate visual confirmation of the generated report.
