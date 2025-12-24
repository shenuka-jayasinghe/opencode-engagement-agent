import argparse
import json
import os
import sys
from jinja2 import Environment, FileSystemLoader
from confluence_tool import get_confluence_client, create_confluence_page

def generate_wsr(space_key, title, parent_id, reporting_period, executive_summary, achievements, upcoming, blockers, template_dir='tools/templates', template_file='wsr_full_template.html'):
    try:
        # 1. Setup Jinja2 environment
        # Use absolute path for template_dir if not provided
        if not os.path.isabs(template_dir):
             template_dir = os.path.join(os.getcwd(), template_dir)

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)

        # 2. Render the template with data
        html_content = template.render(
            reporting_period=reporting_period,
            executive_summary=executive_summary,
            key_achievements=achievements,
            upcoming_activities=upcoming,
            blockers=blockers
        )

        # 3. Create the page in Confluence
        client = get_confluence_client()
        result = create_confluence_page(client, space_key, title, html_content, parent_id)
        
        # Construct the page URL
        if result and 'id' in result:
            page_id = result['id']
            # Get the base URL from the client
            base_url = client.url.rstrip('/')
            page_url = f"{base_url}/wiki/spaces/{space_key}/pages/{page_id}/{title.replace(' ', '+')}"
            print(f"Successfully created WSR page: '{title}' in space '{space_key}'")
            print(f"Page URL: {page_url}")
        else:
            print(f"Successfully created WSR page: '{title}' in space '{space_key}'")
        return True

    except Exception as e:
        print(f"Error generating WSR: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WSR Generator Tool')
    parser.add_argument('--space-key', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--parent-id', required=True)
    parser.add_argument('--period', required=True)
    parser.add_argument('--summary', required=True)
    # Lists are passed as pipe-separated strings for simplicity in CLI: "Item 1|Item 2"
    parser.add_argument('--achievements', required=True)
    parser.add_argument('--upcoming', required=True)
    parser.add_argument('--blockers', required=True)

    args = parser.parse_args()

    generate_wsr(
        args.space_key,
        args.title,
        args.parent_id,
        args.period,
        args.summary,
        args.achievements.split('|'),
        args.upcoming.split('|'),
        args.blockers.split('|')
    )
