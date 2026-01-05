import argparse
import json
import sys
from atlassian import Bitbucket


def get_bitbucket_client(config_file="config/engagement_agent_config.json"):
    """Initializes and returns a Bitbucket client.

    Uses the same Atlassian credentials as Confluence/Jira since Bitbucket
    is part of the Atlassian ecosystem.
    """
    with open(config_file, "r") as f:
        config = json.load(f)

    # Check if there's a dedicated bitbucket config first
    bitbucket_config = config.get("bitbucket", {})

    if bitbucket_config and bitbucket_config.get("email"):
        # Use dedicated Bitbucket config if provided
        url = bitbucket_config.get("url", "https://api.bitbucket.org")
        username = bitbucket_config.get("email")
        password = bitbucket_config.get("api_token")
        cloud = bitbucket_config.get("cloud", True)
    else:
        # Fall back to Confluence credentials (same Atlassian account)
        confluence_config = config.get("confluence", {})
        url = "https://api.bitbucket.org"
        username = confluence_config.get("email")
        password = confluence_config.get("api_token")
        cloud = True

    if not all([username, password]):
        raise ValueError(
            "Bitbucket/Atlassian credentials not configured. "
            "Either add a 'bitbucket' section or ensure 'confluence' credentials are present."
        )

    return Bitbucket(url=url, username=username, password=password, cloud=cloud)


def list_workspaces(client):
    """Lists all accessible workspaces."""
    try:
        response = client.get("2.0/workspaces")
        workspaces = response.get("values", [])
        result = []
        for ws in workspaces:
            result.append(f"Workspace: {ws['name']} (slug: {ws['slug']})")
        return "\n".join(result) if result else "No workspaces found."
    except Exception as e:
        return f"Failed to list workspaces: {e}"


def list_projects(client, workspace):
    """Lists all projects in a workspace."""
    try:
        response = client.get(f"2.0/workspaces/{workspace}/projects")
        projects = response.get("values", [])
        result = []
        for proj in projects:
            result.append(f"Project: {proj['name']} (key: {proj['key']})")
        return "\n".join(result) if result else f"No projects found in workspace {workspace}."
    except Exception as e:
        return f"Failed to list projects in workspace {workspace}: {e}"


def list_repositories(client, workspace, project_key=None):
    """Lists all repositories in a workspace, optionally filtered by project."""
    try:
        if project_key:
            response = client.get(f"2.0/repositories/{workspace}", params={"q": f'project.key="{project_key}"'})
        else:
            response = client.get(f"2.0/repositories/{workspace}")

        repos = response.get("values", [])
        result = []
        for repo in repos:
            project_info = repo.get("project", {})
            project_name = project_info.get("name", "N/A")
            result.append(f"Repo: {repo['name']} (slug: {repo['slug']}, project: {project_name})")
        return "\n".join(result) if result else "No repositories found."
    except Exception as e:
        return f"Failed to list repositories: {e}"


def get_repository_info(client, workspace, repo_slug):
    """Gets detailed information about a repository."""
    try:
        repo = client.get(f"2.0/repositories/{workspace}/{repo_slug}")
        project = repo.get("project", {})

        info = []
        info.append(f"Repository: {repo['name']}")
        info.append(f"Description: {repo.get('description', 'No description')}")
        info.append(f"Project: {project.get('name', 'N/A')} ({project.get('key', 'N/A')})")

        # Get main branch info
        mainbranch = repo.get("mainbranch", {})
        if mainbranch:
            info.append(f"Main branch: {mainbranch.get('name', 'N/A')}")

        info.append(f"Size: {repo.get('size', 0)} bytes")
        info.append(f"Language: {repo.get('language', 'N/A')}")

        # Get clone URLs
        clone_links = repo.get("links", {}).get("clone", [])
        for link in clone_links:
            if link.get("name") == "https":
                info.append(f"Clone URL (HTTPS): {link['href']}")

        info.append(f"Web URL: {repo.get('links', {}).get('html', {}).get('href', 'N/A')}")

        return "\n".join(info)
    except Exception as e:
        return f"Failed to get repository info: {e}"


def list_pull_requests(client, workspace, repo_slug, state="OPEN", limit=10):
    """Lists pull requests for a repository.

    Args:
        client: Bitbucket client
        workspace: Workspace slug
        repo_slug: Repository slug
        state: PR state (OPEN, MERGED, DECLINED, SUPERSEDED, default: OPEN)
        limit: Maximum number of results (default: 10)
    """
    try:
        # Build API path
        params = {"state": state, "pagelen": limit}
        prs = client.get(f"2.0/repositories/{workspace}/{repo_slug}/pullrequests", params=params)

        result = []
        for pr in prs.get("values", []):
            author = pr["author"]["display_name"]
            created = pr["created_on"][:10]  # Just the date
            result.append(f"PR #{pr['id']}: {pr['title']}")
            result.append(f"  Author: {author}, Created: {created}, State: {pr['state']}")
            result.append(f"  URL: {pr['links']['html']['href']}")
            result.append("")

        return "\n".join(result) if result else f"No {state} pull requests found."
    except Exception as e:
        return f"Failed to list pull requests: {e}"


def get_pull_request(client, workspace, repo_slug, pr_id):
    """Gets detailed information about a specific pull request."""
    try:
        pr = client.get(f"2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}")

        info = []
        info.append(f"PR #{pr['id']}: {pr['title']}")
        info.append(f"Author: {pr['author']['display_name']}")
        info.append(f"State: {pr['state']}")
        info.append(f"Created: {pr['created_on']}")
        info.append(f"Updated: {pr['updated_on']}")
        info.append(f"Source: {pr['source']['branch']['name']}")
        info.append(f"Destination: {pr['destination']['branch']['name']}")
        info.append(f"Description:\n{pr.get('description', 'No description')}")
        info.append(f"\nURL: {pr['links']['html']['href']}")

        # Get reviewers
        reviewers = pr.get("reviewers", [])
        if reviewers:
            info.append("\nReviewers:")
            for reviewer in reviewers:
                info.append(f"  - {reviewer['display_name']}")

        # Get participants
        participants = pr.get("participants", [])
        if participants:
            info.append("\nParticipants:")
            for participant in participants:
                approved = "✓" if participant.get("approved", False) else "✗"
                info.append(f"  - {participant['user']['display_name']} (approved: {approved})")

        return "\n".join(info)
    except Exception as e:
        return f"Failed to get pull request: {e}"


def get_latest_pull_request(client, workspace, repo_slug, state="OPEN"):
    """Gets the most recent pull request from a repository."""
    try:
        params = {"state": state, "pagelen": 1, "sort": "-created_on"}
        prs = client.get(f"2.0/repositories/{workspace}/{repo_slug}/pullrequests", params=params)

        values = prs.get("values", [])
        if not values:
            return f"No {state} pull requests found in {workspace}/{repo_slug}"

        pr = values[0]
        return get_pull_request(client, workspace, repo_slug, pr["id"])
    except Exception as e:
        return f"Failed to get latest pull request: {e}"


def list_branches(client, workspace, repo_slug, limit=10):
    """Lists branches in a repository."""
    try:
        params = {"pagelen": limit}
        branches = client.get(f"2.0/repositories/{workspace}/{repo_slug}/refs/branches", params=params)

        result = []
        for branch in branches.get("values", []):
            result.append(f"Branch: {branch['name']}")
            if branch.get("target"):
                result.append(f"  Last commit: {branch['target']['hash'][:12]}")
                result.append(f"  Author: {branch['target']['author']['raw']}")
                result.append(f"  Date: {branch['target']['date'][:10]}")
            result.append("")

        return "\n".join(result) if result else "No branches found."
    except Exception as e:
        return f"Failed to list branches: {e}"


def get_recent_commits(client, workspace, repo_slug, branch=None, limit=10):
    """Gets recent commits from a repository.

    Args:
        client: Bitbucket client
        workspace: Workspace slug
        repo_slug: Repository slug
        branch: Branch name (optional, defaults to main branch)
        limit: Maximum number of commits (default: 10)
    """
    try:
        path = f"2.0/repositories/{workspace}/{repo_slug}/commits"
        if branch:
            path += f"/{branch}"

        params = {"pagelen": limit}
        commits = client.get(path, params=params)

        result = []
        for commit in commits.get("values", []):
            result.append(f"Commit: {commit['hash'][:12]}")
            result.append(f"  Author: {commit['author']['raw']}")
            result.append(f"  Date: {commit['date'][:10]}")
            result.append(f"  Message: {commit['message'].strip()}")
            result.append("")

        return "\n".join(result) if result else "No commits found."
    except Exception as e:
        return f"Failed to get commits: {e}"


def search_code(client, workspace, search_query, repo_slug=None):
    """Searches for code in repositories.

    Args:
        client: Bitbucket client
        workspace: Workspace slug
        search_query: Text to search for
        repo_slug: Optional repository slug to limit search
    """
    try:
        # Note: Bitbucket Cloud code search requires special API endpoints
        # This is a basic implementation - may need enhancement based on API availability
        params = {"search_query": search_query, "pagelen": 20}

        if repo_slug:
            path = f"2.0/repositories/{workspace}/{repo_slug}/search/code"
        else:
            path = f"2.0/workspaces/{workspace}/search/code"

        results = client.get(path, params=params)

        result = []
        for item in results.get("values", []):
            file_path = item.get("path_matches", [{}])[0].get("text", "N/A")
            result.append(f"File: {file_path}")
            if item.get("content_matches"):
                for match in item["content_matches"][:3]:  # Show first 3 matches
                    result.append(f"  Match: {match.get('lines', [{}])[0].get('line', '')}")
            result.append("")

        return "\n".join(result) if result else "No code matches found."
    except Exception as e:
        return f"Code search failed (may not be available on your plan): {e}"


def main():
    parser = argparse.ArgumentParser(description="Bitbucket API Tool")
    parser.add_argument("--config", default="config/engagement_agent_config.json", help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List workspaces
    subparsers.add_parser("list-workspaces", help="List all accessible workspaces")

    # List projects
    projects_parser = subparsers.add_parser("list-projects", help="List projects in a workspace")
    projects_parser.add_argument("workspace", help="Workspace slug")

    # List repositories
    repos_parser = subparsers.add_parser("list-repositories", help="List repositories")
    repos_parser.add_argument("workspace", help="Workspace slug")
    repos_parser.add_argument("--project-key", help="Filter by project key")

    # Get repository info
    repo_info_parser = subparsers.add_parser("get-repository", help="Get repository information")
    repo_info_parser.add_argument("workspace", help="Workspace slug")
    repo_info_parser.add_argument("repo_slug", help="Repository slug")

    # List pull requests
    prs_parser = subparsers.add_parser("list-pull-requests", help="List pull requests")
    prs_parser.add_argument("workspace", help="Workspace slug")
    prs_parser.add_argument("repo_slug", help="Repository slug")
    prs_parser.add_argument(
        "--state", default="OPEN", choices=["OPEN", "MERGED", "DECLINED", "SUPERSEDED"], help="PR state"
    )
    prs_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")

    # Get pull request
    pr_parser = subparsers.add_parser("get-pull-request", help="Get pull request details")
    pr_parser.add_argument("workspace", help="Workspace slug")
    pr_parser.add_argument("repo_slug", help="Repository slug")
    pr_parser.add_argument("pr_id", type=int, help="Pull request ID")

    # Get latest pull request
    latest_pr_parser = subparsers.add_parser("get-latest-pull-request", help="Get the most recent pull request")
    latest_pr_parser.add_argument("workspace", help="Workspace slug")
    latest_pr_parser.add_argument("repo_slug", help="Repository slug")
    latest_pr_parser.add_argument(
        "--state", default="OPEN", choices=["OPEN", "MERGED", "DECLINED", "SUPERSEDED"], help="PR state"
    )

    # List branches
    branches_parser = subparsers.add_parser("list-branches", help="List branches")
    branches_parser.add_argument("workspace", help="Workspace slug")
    branches_parser.add_argument("repo_slug", help="Repository slug")
    branches_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")

    # Get commits
    commits_parser = subparsers.add_parser("get-commits", help="Get recent commits")
    commits_parser.add_argument("workspace", help="Workspace slug")
    commits_parser.add_argument("repo_slug", help="Repository slug")
    commits_parser.add_argument("--branch", help="Branch name")
    commits_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")

    # Search code
    search_parser = subparsers.add_parser("search-code", help="Search for code")
    search_parser.add_argument("workspace", help="Workspace slug")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--repo-slug", help="Repository slug (optional)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = get_bitbucket_client(args.config)

        if args.command == "list-workspaces":
            print(list_workspaces(client))

        elif args.command == "list-projects":
            print(list_projects(client, args.workspace))

        elif args.command == "list-repositories":
            print(list_repositories(client, args.workspace, args.project_key))

        elif args.command == "get-repository":
            print(get_repository_info(client, args.workspace, args.repo_slug))

        elif args.command == "list-pull-requests":
            print(list_pull_requests(client, args.workspace, args.repo_slug, args.state, args.limit))

        elif args.command == "get-pull-request":
            print(get_pull_request(client, args.workspace, args.repo_slug, args.pr_id))

        elif args.command == "get-latest-pull-request":
            print(get_latest_pull_request(client, args.workspace, args.repo_slug, args.state))

        elif args.command == "list-branches":
            print(list_branches(client, args.workspace, args.repo_slug, args.limit))

        elif args.command == "get-commits":
            print(get_recent_commits(client, args.workspace, args.repo_slug, args.branch, args.limit))

        elif args.command == "search-code":
            print(search_code(client, args.workspace, args.query, args.repo_slug))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
