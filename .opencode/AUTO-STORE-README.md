# Auto-Store Knowledge Configuration

This directory contains the configuration and plugin for automatic knowledge storage.

## 🎯 How It Works

### **Approach 1: Agent Instructions (Recommended - Currently Active)**

The agent is configured via `INSTRUCTIONS.md` to **automatically store important technical information** after significant exchanges. This is **already enabled** for you!

#### What Gets Stored Automatically:
- ✅ Code patterns, commands, and configurations
- ✅ Technical decisions and architectural approaches
- ✅ Problem-solving strategies and debugging steps
- ✅ API endpoints and integration patterns
- ✅ Best practices and optimization techniques
- ✅ Project-specific configurations

#### What DOESN'T Get Stored:
- ❌ Casual conversation or greetings
- ❌ Secrets, passwords, API keys, credentials
- ❌ Personal or private information
- ❌ Trivial exchanges or clarifications

### **Approach 2: Plugin Toggle (Optional)**

A plugin is available at `.opencode/plugin/auto-store-knowledge.ts` that provides commands to manually control auto-storage.

#### Available Commands:
```bash
# Toggle auto-storage on/off
/toggle-auto-store

# Check current status
/auto-store-status
```

## 🚀 Quick Start

### **Option A: Trust the Agent (Easiest)**

You don't need to do anything! The agent is already configured to proactively store knowledge. After technical discussions, you'll see notifications like:

```
📝 Stored in knowledge base: "AWS Lambda Best Practices" (Entry #5)
```

### **Option B: Manual Control**

If you want explicit control, use the commands:

1. **Enable auto-storage:**
   ```
   /toggle-auto-store
   ```

2. **Check if it's enabled:**
   ```
   /auto-store-status
   ```

3. **Manually store something:**
   ```
   /store-knowledge "My Topic"
   ```

## 📋 Example Workflow

### Scenario: Learning about Docker Configuration

```
User: How do I set up Docker Compose for production?

Agent: For production Docker Compose setups:
- Always set `restart: unless-stopped` for containers
- Use `.env` files for secrets (never commit them)
- Mount volumes with `:ro` for read-only configs
- Set resource limits (memory, CPU)

User: Great! Also, how do I enable health checks?

Agent: Add this to your service definition:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

📝 Stored in knowledge base: "Docker Compose Production Configuration" (Entry #8)
Tags: docker, production, devops, configuration
```

## 🔍 Finding Stored Knowledge

After information is stored, you can retrieve it anytime:

```bash
# Semantic search (finds similar concepts)
/search-knowledge docker production

# Text search (exact keywords)
/search-knowledge --text "docker-compose.yml"

# View specific entry
/show-entry 8

# List all entries
/list-knowledge
```

## ⚙️ Configuration Files

- **`.opencode/.auto-store-enabled`** - Toggle state (true/false)
- **`INSTRUCTIONS.md`** - Agent behavior instructions (already configured)
- **`.opencode/plugin/auto-store-knowledge.ts`** - Plugin for toggle commands

## 🛠️ Customization

### Adjust What Gets Stored

Edit `INSTRUCTIONS.md` and modify the "What to Store" section:

```markdown
*   **What to Store:** After significant technical discussions, automatically identify and store:
    *   Your custom criteria here...
```

### Change Tag Strategy

Edit the "Tag Strategy" section in `INSTRUCTIONS.md`:

```markdown
*   **Tag Strategy:** Use consistent, lowercase tags:
    *   Your custom tags here...
```

## 📊 Monitoring Storage

To see what's been stored:

```bash
# View statistics
/knowledge-stats

# Browse recent entries
/search-knowledge --recent

# List by tag
/list-knowledge --tags aws
```

## 🔒 Privacy & Security

The agent is configured to **NEVER store**:
- Passwords, secrets, API keys
- Personal or private information
- Content already in Confluence
- Trivial or casual conversations

All data is stored locally in:
```
~/.local/share/opencode-personal-knowledge/
```

## 💡 Tips

1. **Review stored entries weekly** - Keep your knowledge base clean
2. **Use consistent tags** - Makes searching easier
3. **Combine with Confluence** - Store project-specific knowledge there, personal insights here
4. **Export important entries** - Copy to team documentation when relevant

## 🐛 Troubleshooting

### Auto-storage not working?

1. **Check MCP server status:**
   ```bash
   # In opencode.json, verify:
   "mcp": {
     "personal-knowledge": {
       "enabled": true
     }
   }
   ```

2. **Check agent instructions:**
   - Ensure `INSTRUCTIONS.md` contains the "Personal Knowledge Management" section

3. **Manually test storage:**
   ```
   /store-knowledge "Test Entry"
   ```

### Too much being stored?

1. **Adjust threshold** - Edit `INSTRUCTIONS.md` and change:
   ```
   You detect 2+ exchanges → You detect 4+ exchanges
   ```

2. **Temporarily disable:**
   ```
   /toggle-auto-store
   ```

## 📚 Related Documentation

- **Custom Commands:** `.opencode/command/store-knowledge.md`
- **Search Commands:** `.opencode/command/search-knowledge.md`
- **Management Commands:** `.opencode/command/manage-knowledge.md`
- **Main Instructions:** `INSTRUCTIONS.md`

---

**Current Status:** ✅ **AUTO-STORAGE ENABLED VIA INSTRUCTIONS**

The agent will automatically store important technical information after significant exchanges. You'll see notifications like:

```
📝 Stored in knowledge base: [title] (Entry #X)
```

Use `/search-knowledge` to find stored information anytime! 🚀
