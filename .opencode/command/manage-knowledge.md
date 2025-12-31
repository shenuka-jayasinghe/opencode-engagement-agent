---
description: Manage personal knowledge database entries
agent: general
---

# Knowledge Management Commands

Additional commands for managing your personal knowledge database.

## Commands

### 1. Show Entry Details
```
/show-entry <id>
```

**Purpose:** View the complete content of a specific knowledge entry

**Steps:**
1. Parse the entry ID from command arguments
2. Use `personal-knowledge_get_knowledge` with the ID
3. Display full entry details:
   - ID and Title
   - Full content (not just preview)
   - All tags
   - Source URL (if available)
   - Created date
   - Last modified date
4. Suggest related actions:
   - Update entry
   - Delete entry
   - Search for similar entries

**Example:**
```
User: /show-entry 8

Agent: 
# Entry #8: AWS Lambda Configuration and Error Handling

**Created:** 2025-12-28 14:32:15
**Modified:** 2025-12-28 14:32:15
**Tags:** aws, lambda, error-handling, cloudwatch
**Source:** https://confluence.example.com/display/DOCS/Lambda+Best+Practices

## Content:

AWS Lambda timeout configuration best practices:

1. Set timeout based on expected execution time plus buffer (e.g., if function runs 30s, set timeout to 45s)
2. Default timeout is 3 seconds - almost always too short for production

Error Handling:
- For async functions, use try-catch blocks to capture errors
- Log all errors to CloudWatch with structured logging
- Use Lambda Destinations for async invocation failures
- Set up CloudWatch alarms for error rates > 1%

CloudWatch Logs:
- Set retention period (7-30 days for non-critical, 90+ days for audit logs)
- Use log groups per function
- Enable X-Ray tracing for distributed tracing

---
💡 Actions:
- Update: /update-entry 8
- Delete: /delete-entry 8
- Similar: /search-knowledge lambda configuration
```

---

### 2. List All Knowledge Entries
```
/list-knowledge [--tags tag1,tag2] [--limit 20]
```

**Purpose:** Browse all knowledge entries with optional filters

**Steps:**
1. Parse arguments:
   - `--tags`: Filter by tags (comma-separated)
   - `--limit`: Number of entries (default 20)
2. Use `personal-knowledge_list_knowledge` with filters
3. Display entries in table format:
   - ID | Title | Tags | Created Date
4. Show summary statistics
5. Suggest next actions

**Example:**
```
User: /list-knowledge --tags aws --limit 10

Agent:
Found 10 entries tagged with [aws]:

| ID | Title                                    | Tags                              | Created    |
|----|------------------------------------------|-----------------------------------|------------|
| 8  | AWS Lambda Configuration                 | aws, lambda, error-handling       | 2025-12-28 |
| 12 | EC2 Instance Rightsizing Strategy        | aws, ec2, optimization, cost      | 2025-12-26 |
| 15 | Serverless Error Monitoring              | aws, monitoring, serverless       | 2025-12-25 |
| 18 | S3 Bucket Lifecycle Policies             | aws, s3, cost-optimization        | 2025-12-22 |
| 22 | IAM Role Best Practices                  | aws, iam, security                | 2025-12-20 |
| 25 | CloudFormation Stack Management          | aws, cloudformation, iac          | 2025-12-18 |
| 28 | RDS Backup and Recovery                  | aws, rds, database, backup        | 2025-12-15 |
| 31 | VPC Network Architecture                 | aws, vpc, networking              | 2025-12-12 |
| 34 | Cost Explorer Analysis Tips              | aws, cost, finops                 | 2025-12-10 |
| 37 | ECS Task Definition Optimization         | aws, ecs, docker, performance     | 2025-12-08 |

**Summary:** 10 of 42 total AWS-tagged entries shown

💡 View any entry: /show-entry <id>
💡 See all entries: /list-knowledge --limit 50
```

---

### 3. Update Knowledge Entry
```
/update-entry <id> [--title "New Title"] [--content "New content"] [--tags tag1,tag2] [--source "url"]
```

**Purpose:** Modify an existing knowledge entry

**Steps:**
1. Parse entry ID and update parameters
2. If no parameters provided: Show current entry and prompt for what to update
3. Use `personal-knowledge_update_knowledge` with changes
4. Confirm update with before/after summary
5. Re-index entry for semantic search

**Example:**
```
User: /update-entry 8 --tags aws,lambda,error-handling,cloudwatch,production

Agent:
Updated entry #8: "AWS Lambda Configuration and Error Handling"

**Changes:**
- Tags: aws, lambda, error-handling, cloudwatch → aws, lambda, error-handling, cloudwatch, production

✅ Entry updated and re-indexed for semantic search

💡 View updated entry: /show-entry 8
```

---

### 4. Delete Knowledge Entry
```
/delete-entry <id>
```

**Purpose:** Remove an entry from the knowledge database

**Steps:**
1. Parse entry ID
2. Use `personal-knowledge_get_knowledge` to show entry details
3. Ask for confirmation before deletion
4. Use `personal-knowledge_delete_knowledge` to remove entry
5. Confirm deletion

**Example:**
```
User: /delete-entry 42

Agent:
⚠️  You're about to delete:

**Entry #42:** "Temporary Testing Notes"
**Created:** 2025-12-15
**Tags:** testing, temporary
**Content preview:** "These are just temporary notes for debugging..."

Are you sure you want to delete this entry? (yes/no)

User: yes

Agent: ✅ Entry #42 deleted successfully
```

---

### 5. Knowledge Database Stats
```
/knowledge-stats
```

**Purpose:** View statistics about your knowledge database

**Steps:**
1. Use `personal-knowledge_get_knowledge_stats`
2. Display metrics:
   - Total entries
   - Total tags
   - Most used tags
   - Entries per tag
   - Storage size
   - Recent activity
3. Suggest maintenance actions if needed

**Example:**
```
User: /knowledge-stats

Agent:
# Personal Knowledge Database Statistics

**Total Entries:** 42
**Total Unique Tags:** 28
**Database Size:** 2.4 MB
**Vector Index Size:** 1.8 MB

## Most Used Tags (Top 10):
1. aws (18 entries)
2. python (12 entries)
3. docker (10 entries)
4. security (9 entries)
5. database (8 entries)
6. optimization (7 entries)
7. kubernetes (6 entries)
8. monitoring (6 entries)
9. api (5 entries)
10. testing (5 entries)

## Recent Activity:
- Last entry added: 2025-12-31 (2 hours ago)
- Entries added this week: 5
- Entries added this month: 18

## Storage Location:
`~/.local/share/opencode-personal-knowledge/`

💡 Browse recent entries: /search-knowledge --recent
💡 View all tags: /list-knowledge
```

---

## Tag Management Best Practices

**Good Tags:**
- ✅ `aws`, `azure`, `gcp` (cloud providers)
- ✅ `python`, `typescript`, `go` (languages)
- ✅ `security`, `performance`, `cost` (concerns)
- ✅ `debugging`, `optimization`, `migration` (activities)
- ✅ `production`, `staging`, `development` (environments)

**Avoid:**
- ❌ Very specific tags used only once
- ❌ Redundant tags (e.g., both `k8s` and `kubernetes`)
- ❌ Tags with spaces (use hyphens: `error-handling`)
- ❌ Too many tags per entry (3-5 is ideal)

## Maintenance Tips

1. **Regular Review:** Monthly review of entries
   - Update outdated information
   - Delete temporary notes
   - Consolidate duplicate entries

2. **Tag Consistency:** Use `/list-knowledge` to see all tags
   - Standardize similar tags
   - Update entries with inconsistent tags

3. **Backup:** Knowledge DB is in `~/.local/share/opencode-personal-knowledge/`
   - Include in your backup routine
   - Export critical entries to Confluence for team sharing

4. **Quality Over Quantity:** 
   - Store meaningful, reusable information
   - Delete entries that are no longer relevant
   - Keep entries focused (one concept per entry)

## Related Commands

- `/store-knowledge` - Store new entry
- `/search-knowledge` - Search entries
- `/show-entry <id>` - View full entry
