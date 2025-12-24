---
description: Generate Weekly Status Report in Confluence
agent: general
---

When this command is called, perform the following steps:

1.  **Template Verification and Creation:**
    *   First, check if a local template exists at `tools/templates/wsr_full_template.html`.
    *   **If the template does NOT exist:**
        *   Read the `engagement_agent_config.json` file to get the example `wsr_template_url`.
        *   Use `tools/confluence_tool.py get-page-info` on the URL to find the `parent_id` and `space_key`.
        *   Use `tools/confluence_tool.py search` to find the 3 most recent WSRs under that same parent to understand the structure.
        *   Fetch the content of the most recent and complete example using `get-page-content`.
        *   Analyze the HTML to identify the dynamic sections (Reporting Period, Executive Summary, Achievements, Upcoming Activities, Blockers) and replace their content with Jinja2 placeholders (e.g., `{{ executive_summary }}`).
        *   Save this content as the new `tools/templates/wsr_full_template.html`. This becomes the stable, reusable template for all future WSRs.

2.  **Read the Configuration:**
    *   Read `engagement_agent_config.json` to get `confluence_space_key`, `slack_channel_ids`, `recipient_emails_to_scan`, and `wsr_template_url` (for parent ID reference).
    *   Calculate the date range for the last 7 days.

3.  **Gather Information:**
    *   **Slack:** Get summaries from `slack_channel_ids` for the last 7 days.
    *   **Gmail:** Get summaries of relevant emails.
    *   **Jira:** Get a summary of recent tickets.
    *   **Confluence:** Get the `parent_id` from the `wsr_template_url`.

4.  **Synthesize Content:**
    *   Synthesize the gathered information into an Executive Summary and pipe-separated lists for Key Achievements, Upcoming Activities, and Blockers.

5.  **Generate the WSR:**
    *   Use the stable `tools/wsr_tool.py` script to generate the HTML from the `wsr_full_template.html` and create the page in Confluence, passing the synthesized content as arguments.
    *   **CRITICAL:** Do not delete the tool or the template after use.
    *   Example call:
        ```bash
        python3 tools/wsr_tool.py \
          --space-key "SDRY" \
          --title "Weekly Status Report - YYYY-MM-DD" \
          --parent-id "123456789" \
          --period "Week X (YYYY-MM-DD - YYYY-MM-DD)" \
          --summary "Executive summary text..." \
          --achievements "Achievement 1|Achievement 2" \
          --upcoming "Task 1|Task 2" \
          --blockers "None"
        ```

6.  **Verify:**
    *   Return the URL of the newly created page to the user.
