import argparse
import json
from atlassian import Confluence
import re

def get_confluence_client(config_file='engagement_agent_config.json'):
    """Initializes and returns a Confluence client."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    confluence_config = config.get('confluence', {})
    server = confluence_config.get('server')
    email = confluence_config.get('email')
    api_token = confluence_config.get('api_token')

    if not all([server, email, api_token]):
        raise ValueError("Confluence server, email, or api_token is not configured.")

    return Confluence(
        url=server,
        username=email,
        password=api_token,
        cloud=True
    )

def get_page_id_from_url(url):
    """Extracts the page ID from a Confluence URL."""
    # Regex to find the page ID, which is usually after '/pages/'
    match = re.search(r'/pages/(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_page_content_by_url(client, url):
    """Fetches the content of a Confluence page given its URL."""
    page_id = get_page_id_from_url(url)
    
    if not page_id:
        return "<h1>Error: Invalid Confluence URL</h1>"
        
    page_content = client.get_page_by_id(page_id, expand='body.storage')
    return page_content['body']['storage']['value']

def get_page_info(client, url):
    """Fetches the page info of a Confluence page given its URL."""
    page_id = get_page_id_from_url(url)
    page = None
    
    if not page_id:
        return {}
        
    try:
        page = client.get_page_by_id(page_id, expand='ancestors,space')
        parent_id = None
        if page['ancestors']:
            parent_id = page['ancestors'][-1]['id']

        return {
            'parent_id': parent_id,
            'space_key': page['space']['key']
        }
    except Exception as e:
        print(f"Error in get_page_info: {e}")
        print(f"Page object: {page}")
        return {}

def create_confluence_page(client, space_key, title, content, parent_id=None):
    """Creates a new page on Confluence under a specified parent page."""
    result = client.create_page(
        space=space_key,
        title=title,
        body=content,
        parent_id=parent_id,
        type='page',
        representation='storage' # Use 'storage' for HTML content
    )
    return result

def update_confluence_page(client, page_id, title, content):
    """Updates an existing Confluence page."""
    result = client.update_page(
        page_id=page_id,
        title=title,
        body=content,
        type='page',
        representation='storage',
        minor_edit=True
    )
    return result

def search_confluence(client, space_key, query, limit=10, start=0, include_labels=None, modified_after=None, title_only=False):
    """Searches for a query in a specific Confluence space with advanced filters.

    Args:
        client: Confluence client
        space_key: Space key to search in
        query: Search query text
        limit: Maximum number of results (default: 10)
        start: Offset for pagination (default: 0)
        include_labels: Comma-separated labels to filter by
        modified_after: Date string (YYYY-MM-DD) to filter by last modified date
        title_only: If True, search only in page titles
    """
    cql_parts = [f"space='{space_key}'"]

    if title_only:
        cql_parts.append(f"title~'{query}'")
    else:
        cql_parts.append(f"text~'{query}'")

    if include_labels:
        for label in include_labels.split(','):
            cql_parts.append(f"label='{label.strip()}'")

    if modified_after:
        cql_parts.append(f"lastModified >= '{modified_after}'")

    cql = " and ".join(cql_parts)
    results = client.cql(cql, limit=limit, start=start)
    return results['results']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Confluence Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # get-page-content command
    get_page_content_parser = subparsers.add_parser('get-page-content')
    get_page_content_parser.add_argument('url', type=str)

    # get-page-info command
    get_page_info_parser = subparsers.add_parser('get-page-info')
    get_page_info_parser.add_argument('url', type=str)

    # create-page command
    create_page_parser = subparsers.add_parser('create-page')
    create_page_parser.add_argument('--space-key', type=str, required=True)
    create_page_parser.add_argument('--title', type=str, required=True)
    create_page_parser.add_argument('--content', type=str, required=True)
    create_page_parser.add_argument('--parent-id', type=str)

    # update-page command
    update_page_parser = subparsers.add_parser('update-page')
    update_page_parser.add_argument('--page-id', type=str, required=True)
    update_page_parser.add_argument('--title', type=str, required=True)
    update_page_parser.add_argument('--content', type=str, required=True)

    # search command
    search_parser = subparsers.add_parser('search')
    search_parser.add_argument('space_key', type=str)
    search_parser.add_argument('query', type=str)
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results (default: 10)')
    search_parser.add_argument('--start', type=int, default=0, help='Offset for pagination (default: 0)')
    search_parser.add_argument('--labels', type=str, help='Comma-separated labels to filter by')
    search_parser.add_argument('--modified-after', type=str, help='Filter by last modified date (YYYY-MM-DD)')
    search_parser.add_argument('--title-only', action='store_true', help='Search only in page titles')

    args = parser.parse_args()
    client = get_confluence_client()

    if args.command == 'get-page-content':
        print(get_page_content_by_url(client, args.url))
    elif args.command == 'get-page-info':
        info = get_page_info(client, args.url)
        print(json.dumps(info))
    elif args.command == 'create-page':
        create_confluence_page(client, args.space_key, args.title, args.content, args.parent_id)
    elif args.command == 'update-page':
        update_confluence_page(client, args.page_id, args.title, args.content)
    elif args.command == 'search':
        results = search_confluence(
            client,
            args.space_key,
            args.query,
            limit=args.limit,
            start=args.start,
            include_labels=args.labels,
            modified_after=args.modified_after,
            title_only=args.title_only
        )
        print(json.dumps(results))
