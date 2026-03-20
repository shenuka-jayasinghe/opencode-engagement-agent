import sys
import os
import csv
from datetime import datetime

# Add tools to path to allow import
sys.path.append(os.path.join(os.getcwd(), 'tools'))

try:
    from jira_tool import get_jira_client
except ImportError:
    sys.path.append(os.getcwd())
    from jira_tool import get_jira_client

def generate_csv_report():
    try:
        client = get_jira_client()
    except Exception as e:
        print(f"Failed to initialize Jira client: {e}")
        return

    years = range(2020, 2026)
    
    # Categories mapped to partial JQL
    # We will append the date range to these
    categories = {
        "Total Tickets": 'project = SD',
        "Service Requests": 'project = SD AND issuetype = "Service Request"',
        "Incidents (All)": 'project = SD AND issuetype = "Incident"',
        "Technical Debt": 'project = SD AND issuetype = "Technical Debt"',
        "Risk": 'project = SD AND issuetype = "Risk"',
        "Problem": 'project = SD AND issuetype = "Problem"',
        "Task": 'project = SD AND issuetype = "Task"',
        "Sub-task": 'project = SD AND issuetype = "Sub-task"'
    }

    output_file = "jira_yearly_report.csv"
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Year'] + list(categories.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Print header to console as well for immediate visibility
        print(",".join(fieldnames))

        for year in years:
            row = {'Year': year}
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            # Date range JQL
            date_jql = f' AND created >= "{start_date}" AND created <= "{end_date}"'
            
            print(f"Processing {year}...", end='', flush=True)
            
            for cat_name, base_jql in categories.items():
                full_jql = base_jql + date_jql
                try:
                    # maxResults=0 returns only meta data (total count) which is much faster
                    count = client.search_issues(full_jql, maxResults=0, fields="key").total
                    row[cat_name] = count
                except Exception:
                    # Fallback for invalid issue types (like Proactive Task if it doesn't exist)
                    row[cat_name] = 0
            
            writer.writerow(row)
            print(" Done.")
            
            # Print row to console
            print(",".join(str(row[k]) for k in fieldnames))

    print(f"\nReport saved to {output_file}")

if __name__ == "__main__":
    generate_csv_report()
