---
description: Manage personal knowledge database entries
agent: general
---

## Commands

### 1. Show Entry `/show-entry <id>`
View complete content of a knowledge entry.

**Steps:**
1. Parse ID, use `personal-knowledge_get_knowledge`
2. Display: ID, title, full content, tags, source URL, dates
3. Suggest: update, delete, search similar

**Output:** Full entry with actions (update, delete, search similar)

### 2. List Entries `/list-knowledge [--tags tag1,tag2] [--limit 20]`
Browse entries with optional filters.

**Steps:** Parse args, use `personal-knowledge_list_knowledge`, display table (ID|Title|Tags|Date), show stats, suggest actions

### 3. Update Entry `/update-entry <id> [--title "..."] [--content "..."] [--tags ...] [--source "..."]`
Modify existing entry.

**Steps:** Parse ID and params, use `personal-knowledge_update_knowledge`, show before/after, re-index

### 4. Delete Entry `/delete-entry <id>`
Remove entry from database.

**Steps:** Parse ID, show details, confirm, use `personal-knowledge_delete_knowledge`

### 5. Database Stats `/knowledge-stats`
View database statistics.

**Steps:** Use `personal-knowledge_get_knowledge_stats`, display: total entries, tags, most used tags, storage size, recent activity, suggest maintenance

## Tag Best Practices

**Good:** Cloud (`aws`, `gcp`), languages (`python`, `go`), concerns (`security`, `performance`), activities (`debugging`, `migration`), environments (`production`, `staging`)

**Avoid:** Single-use tags, redundancy (`k8s`+`kubernetes`), spaces (use hyphens), too many (3-5 ideal)

## Maintenance

1. **Monthly review:** Update outdated info, delete temp notes, consolidate duplicates
2. **Tag consistency:** Use `/list-knowledge`, standardize similar tags
3. **Backup:** DB at `~/.local/share/opencode-personal-knowledge/`
4. **Quality:** Store meaningful, reusable info; one concept per entry

## Related

`/store-knowledge` | `/search-knowledge` | `/show-entry <id>`
