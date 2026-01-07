---
description: Store information in personal knowledge vector database
agent: general
---

## Usage

**Context:** `/store-knowledge` - Analyze last 3-5 exchanges, extract technical info
**With title:** `/store-knowledge "AWS IAM Best Practices"` - Use title, analyze context
**Specific content:** `/store-knowledge "Title" --content "..."` - Store exact content
**With tags:** `/store-knowledge "Title" --tags aws,rds,postgresql` - Comma-separated tags

## Execution

1. **Parse:** Title (quoted), `--content`, `--tags`, `--source` (optional URL)
2. **Content:** Use `--content` if provided; else analyze last 3-5 exchanges (code, config, decisions, patterns); ask if unclear
3. **Title:** Use provided or auto-generate from content; confirm if auto
4. **Tags:** Use provided or auto-generate 2-5 (tech names, categories, domain terms); show for confirmation
5. **Store:** Use `personal-knowledge_store_knowledge` (title, content, tags, source), confirm with ID
6. **Tips:** Show search examples and related terms

## Example
```
/store-knowledge "Docker Compose Production"
  --content "Set restart: unless-stopped. Use .env for secrets. Mount :ro for read-only."
  --tags docker,devops,production

✅ Stored entry #5: "Docker Compose Production"
Retrieve: "Search my knowledge for docker production" or "Show me entry #5"
```

## Best Practices

1. **Specific titles:** "AWS EC2 Rightsizing Strategy" not "Notes"
2. **Consistent tags:** Tech (`aws`, `python`), activity (`debugging`, `migration`), domain (`security`, `networking`)
3. **Include context:** Add source URLs, GitHub links, doc refs
4. **Store incrementally:** Small focused entries, one concept per entry
5. **Review before storing:** Confirm auto-generated content/tags

## Error Handling

- MCP not responding: Check `opencode.json`
- Storage fails: Verify `~/.local/share/opencode-personal-knowledge/` writable
- Empty content: Prompt user
- Invalid tags: Clean format (lowercase, alphanumeric, hyphens)

## Related

`/search-knowledge` | `/list-knowledge` | `/update-knowledge` | `/delete-knowledge`
