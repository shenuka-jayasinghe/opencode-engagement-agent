---
description: Store information in personal knowledge vector database
agent: general
---

# Store Knowledge Command

When this command is called with `/store-knowledge`, perform the following steps:

## Usage Patterns

### 1. **Store Current Context**
```
/store-knowledge
```
- Analyzes the recent conversation (last 3-5 exchanges)
- Extracts key technical information, decisions, or learnings
- Prompts user for a title or generates one automatically
- Stores with relevant tags

### 2. **Store with Title**
```
/store-knowledge "AWS IAM Best Practices"
```
- Uses the provided title
- Analyzes recent context for content
- Auto-generates appropriate tags

### 3. **Store Specific Content**
```
/store-knowledge "API Endpoint Configuration" --content "The production API is at https://api.example.com. Use X-API-Key header for auth."
```
- Stores the exact content provided
- Uses the specified title
- Prompts for tags or generates them

### 4. **Store with Tags**
```
/store-knowledge "Database Migration Steps" --tags aws,rds,postgresql,migration
```
- Stores with specified tags for easier retrieval
- Tags should be comma-separated, no spaces

## Command Execution Steps

1. **Parse Arguments:**
   - Extract title (if provided in quotes)
   - Extract `--content` flag value (if provided)
   - Extract `--tags` flag value (if provided)
   - Extract `--source` flag value (optional URL or reference)

2. **Determine Content:**
   - If `--content` is provided: Use that exact content
   - If no `--content`: Analyze the last 3-5 conversation exchanges for technical information:
     - Code snippets or commands
     - Configuration details
     - Technical decisions or patterns
     - Problem-solving approaches
     - Important facts or learnings
   - If no meaningful content found: Ask user what to store

3. **Determine Title:**
   - If title provided in quotes: Use it
   - If no title: Generate a concise, descriptive title from the content
   - Confirm with user if auto-generated

4. **Determine Tags:**
   - If `--tags` provided: Use them
   - If no tags: Auto-generate 2-5 relevant tags based on content:
     - Technology names (aws, python, docker, etc.)
     - Categories (security, performance, debugging, etc.)
     - Project/domain terms from engagement_agent_config.json if relevant
   - Show generated tags to user for confirmation

5. **Store the Entry:**
   - Use the `personal-knowledge_store_knowledge` tool with:
     - `title`: The determined title
     - `content`: The determined content
     - `tags`: Array of tags
     - `source`: Optional source URL/reference
   - Confirm successful storage with entry ID

6. **Provide Usage Tips:**
   - Show the user how to search for this entry:
     - "Search my knowledge for [key concept]"
     - "Show me entry #[id]"
   - Suggest related search terms based on content

## Examples

### Example 1: Store conversation context
```
User: /store-knowledge

Agent: I found this technical information from our recent discussion:
- AWS Lambda timeout configuration
- Error handling patterns for async functions
- CloudWatch log retention settings

Suggested title: "AWS Lambda Configuration and Error Handling"
Suggested tags: aws, lambda, error-handling, cloudwatch

Store this? (yes/no)
```

### Example 2: Store specific content
```
User: /store-knowledge "Docker Compose Production Setup" --content "Always set restart: unless-stopped for production containers. Use .env files for secrets. Mount volumes with :ro for read-only configs." --tags docker,devops,production

Agent: ✅ Stored knowledge entry #5: "Docker Compose Production Setup"
📊 Indexed for semantic search
🏷️ Tags: docker, devops, production

You can retrieve this with:
- "Search my knowledge for docker production"
- "Show me entry #5"
```

### Example 3: Quick store from context
```
[After discussing Jira API configuration]

User: /store-knowledge "Jira API Setup"

Agent: Analyzing recent discussion...

Found content:
- Jira API endpoint: https://your-domain.atlassian.net/rest/api/3
- Authentication: Use API token with email as username
- Rate limits: 10 requests/second

Suggested tags: jira, api, authentication, atlassian

Store this? (yes/no)
```

## Best Practices

1. **Be Specific in Titles:** Use descriptive titles that make entries easy to find
   - ✅ "AWS EC2 Instance Rightsizing Strategy"
   - ❌ "Notes"

2. **Use Consistent Tags:** Establish a tagging convention
   - Technology: `aws`, `python`, `docker`
   - Activity: `debugging`, `optimization`, `migration`
   - Domain: `security`, `networking`, `database`

3. **Include Context:** Add source URLs, dates, or references when relevant
   - Confluence page URLs
   - GitHub issue/PR links
   - Documentation references

4. **Store Incrementally:** Don't wait to store large documents
   - Store small, focused entries frequently
   - Each entry should be about one concept or task

5. **Review Before Storing:** Always confirm auto-generated content and tags
   - Ensure accuracy
   - Add missing context
   - Adjust tags for better discoverability

## Error Handling

- If MCP server is not responding: Check `opencode.json` configuration
- If storage fails: Verify `~/.local/share/opencode-personal-knowledge/` is writable
- If content is empty: Prompt user for explicit content or context
- If tags are invalid: Clean and validate tag format (lowercase, alphanumeric, hyphens)

## Related Commands

- `/search-knowledge <query>` - Search stored knowledge
- `/list-knowledge` - List all entries
- `/update-knowledge <id>` - Update existing entry
- `/delete-knowledge <id>` - Delete entry
