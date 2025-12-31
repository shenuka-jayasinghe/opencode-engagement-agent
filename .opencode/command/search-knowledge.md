---
description: Search personal knowledge vector database
agent: general
---

# Search Knowledge Command

When this command is called with `/search-knowledge`, perform semantic or text-based searches in the personal knowledge database.

## Usage Patterns

### 1. **Semantic Search (Default)**
```
/search-knowledge docker networking
```
- Uses AI similarity matching (embeddings)
- Finds entries with similar meaning, not just exact keywords
- Returns ranked results with similarity scores

### 2. **Text Search (Keyword-based)**
```
/search-knowledge --text "api.example.com"
```
- Searches for exact keyword matches
- Useful for finding specific commands, URLs, or code
- Faster than semantic search

### 3. **Search with Filters**
```
/search-knowledge aws --tags security,iam --limit 5
```
- Filter by tags
- Limit number of results
- Combine with semantic or text search

### 4. **Browse Recent Entries**
```
/search-knowledge --recent
```
- Shows most recently added entries
- Useful for reviewing what you've stored
- Default limit: 10 entries

## Command Execution Steps

1. **Parse Arguments:**
   - Extract search query (main argument)
   - Check for `--text` flag (switches to keyword search)
   - Check for `--tags` filter (comma-separated)
   - Check for `--limit` (number of results, default 5)
   - Check for `--recent` flag (show recent entries)

2. **Execute Search:**
   
   **If `--recent` flag:**
   - Use `personal-knowledge_list_knowledge` with limit
   - Sort by created date descending
   
   **If `--text` flag:**
   - Use `personal-knowledge_search_knowledge_text` with query
   - Apply tag filters if provided
   
   **Otherwise (semantic search):**
   - Use `personal-knowledge_search_knowledge` with query
   - Apply tag filters if provided
   - Limit results to specified number

3. **Format Results:**
   - Show each result with:
     - Entry ID
     - Title
     - Similarity score (for semantic search) or match type (for text search)
     - Content preview (first 200 characters)
     - Tags
     - Created/modified date
   - Number results (1, 2, 3...)
   - Show total count of results

4. **Provide Next Actions:**
   - Suggest viewing full content: "Show me entry #[id]"
   - Suggest refining search if no results
   - Suggest related tags for filtering

## Examples

### Example 1: Semantic search
```
User: /search-knowledge lambda error handling

Agent: Found 3 entries:

### 1. AWS Lambda Configuration and Error Handling (ID: 8) — 92% similar
Created: 2025-12-28 | Tags: aws, lambda, error-handling, cloudwatch

Content preview:
"AWS Lambda timeout configuration best practices. Set timeout based on expected execution time plus buffer. For async functions, use try-catch blocks to capture errors and log to CloudWatch..."

[View full entry: "Show me entry #8"]

### 2. Python Async Exception Patterns (ID: 12) — 85% similar
Created: 2025-12-20 | Tags: python, async, error-handling

Content preview:
"When handling exceptions in async Python functions, always use asyncio.gather() with return_exceptions=True to prevent one failure from canceling other tasks..."

[View full entry: "Show me entry #12"]

### 3. Serverless Error Monitoring (ID: 15) — 78% similar
Created: 2025-12-15 | Tags: aws, monitoring, serverless

Content preview:
"Set up CloudWatch alarms for Lambda errors and throttles. Use X-Ray for distributed tracing across microservices..."

[View full entry: "Show me entry #15"]

---
💡 Tip: Use "/search-knowledge --tags lambda" to filter by specific tags
```

### Example 2: Text search for exact match
```
User: /search-knowledge --text "api.example.com"

Agent: Found 2 entries with exact matches:

### 1. API Endpoint Configuration (ID: 5) — Exact match
Created: 2025-12-30 | Tags: api, production, configuration

Content preview:
"The production API is at https://api.example.com. Use X-API-Key header for authentication. Rate limit is 1000 requests/hour..."

[View full entry: "Show me entry #5"]

### 2. Service Integration Guide (ID: 18) — Exact match
Created: 2025-12-10 | Tags: integration, api, backend

Content preview:
"To integrate with the external service, point to api.example.com/v2. Requires OAuth2 authentication with client credentials flow..."

[View full entry: "Show me entry #18"]
```

### Example 3: Search with tag filter
```
User: /search-knowledge database --tags postgresql,performance --limit 3

Agent: Found 3 entries tagged with [postgresql, performance]:

### 1. PostgreSQL Query Optimization (ID: 22) — 95% similar
Created: 2025-12-25 | Tags: postgresql, performance, database, optimization

Content preview:
"Use EXPLAIN ANALYZE to identify slow queries. Create indexes on foreign key columns and WHERE clause columns. Consider partial indexes for large tables..."

[View full entry: "Show me entry #22"]

[... 2 more results ...]
```

### Example 4: Browse recent entries
```
User: /search-knowledge --recent

Agent: Your 10 most recent knowledge entries:

1. **OpenCode Personal Knowledge MCP Usage** (ID: 1) — 2025-12-31
   Tags: opencode, mcp, knowledge-management, semantic-search
   
2. **Jira API Setup** (ID: 5) — 2025-12-31
   Tags: jira, api, authentication, atlassian
   
3. **Docker Compose Production Setup** (ID: 7) — 2025-12-30
   Tags: docker, devops, production

[... 7 more entries ...]

💡 View any entry with: "Show me entry #[id]"
```

## Search Tips

1. **Use Natural Language:** Semantic search understands concepts
   - ✅ "how to debug memory leaks"
   - ✅ "cost optimization strategies"
   
2. **Use Exact Text for Specifics:** Text search for precise matches
   - ✅ `--text "import tensorflow"` (code snippets)
   - ✅ `--text "https://docs.aws.amazon.com"` (URLs)

3. **Combine with Tags:** Narrow results by topic
   - ✅ `/search-knowledge security --tags aws`

4. **Start Broad, Then Filter:** If too many results, add constraints
   - First: `/search-knowledge kubernetes`
   - Then: `/search-knowledge kubernetes --tags networking --limit 3`

5. **Check Recent Entries:** Review what you've stored lately
   - ✅ `/search-knowledge --recent`

## No Results?

If search returns no results:

1. **Try broader terms:** "database" instead of "PostgreSQL 15.2"
2. **Check tags:** Use `/list-knowledge --tags` to see available tags
3. **Use text search:** If semantic search fails, try `--text`
4. **Review all entries:** Use `/search-knowledge --recent` to browse

## Related Commands

- `/store-knowledge` - Store new entry
- `/show-entry <id>` - View full entry details
- `/list-knowledge` - List all entries with filters
- `/knowledge-stats` - See database statistics
