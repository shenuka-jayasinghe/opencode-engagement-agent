---
description: Search personal knowledge vector database
---

Perform semantic or text-based searches in personal knowledge database.

## Usage

**Semantic (default):** `/search-knowledge docker networking` - AI similarity matching
**Text (keyword):** `/search-knowledge --text "api.example.com"` - Exact matches
**Filtered:** `/search-knowledge aws --tags security,iam --limit 5`
**Recent:** `/search-knowledge --recent` - Latest entries (limit 10)

## Execution

1. **Parse:** Query, `--text`, `--tags`, `--limit` (default 5), `--recent`
2. **Execute:**
   - `--recent`: Use `personal-knowledge_list_knowledge` (sort by date desc)
   - `--text`: Use `personal-knowledge_search_knowledge_text`
   - Default: Use `personal-knowledge_search_knowledge` (semantic)
   - Apply tag filters if provided
3. **Format:** Display ID, title, score/match, preview (200 chars), tags, date
4. **Suggest:** "Show me entry #[id]", refine search, related tags

## Example Output

```
/search-knowledge lambda error handling

Found 3 entries:
1. AWS Lambda Configuration (ID: 8) — 92% similar
   Tags: aws, lambda, error-handling | 2025-12-28
   Preview: "AWS Lambda timeout best practices. Set timeout based on..."

2. Python Async Exception Patterns (ID: 12) — 85% similar
   Tags: python, async, error-handling | 2025-12-20

💡 View full: "Show me entry #8"
```

## Tips

- **Semantic:** Natural language ("how to debug memory leaks")
- **Text:** Exact matches for code/URLs (`--text "import tensorflow"`)
- **Tags:** Narrow results (`/search-knowledge security --tags aws`)
- **No results:** Try broader terms, check `/list-knowledge --tags`, use `--text`, or browse `--recent`

## Related

`/store-knowledge` | `/show-entry <id>` | `/list-knowledge` | `/knowledge-stats`
