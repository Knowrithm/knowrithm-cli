# Knowrithm CLI - Quick Reference Card

## 🚀 Getting Started

### Launch Dashboard
```bash
knowrithm dashboard
```
Beautiful welcome screen with all commands, quick actions, and helpful links!

### First Time Setup
```bash
# 1. Configure API endpoint
knowrithm config set-base-url https://app.knowrithm.org/api

# 2. Login
knowrithm auth login

# 3. View dashboard
knowrithm dashboard
```

## 📋 Main Commands

| Command | Description | Example |
|---------|-------------|---------|
| 🤖 **agent** | Manage AI agents | `knowrithm agent list` |
| 💬 **conversation** | Manage conversations | `knowrithm conversation list` |
| 📄 **document** | Manage documents | `knowrithm document list` |
| 👥 **lead** | Manage leads | `knowrithm lead list` |
| 🏢 **company** | Manage companies | `knowrithm company current` |
| 🔐 **auth** | Authentication | `knowrithm auth login` |
| 📊 **analytics** | View analytics | `knowrithm analytics dashboard` |
| ⚙️ **settings** | LLM settings | `knowrithm settings list` |
| 🌐 **website** | Website sources | `knowrithm website list` |
| 🗄️ **database** | Database connections | `knowrithm database list` |
| 👨‍💼 **admin** | Admin commands | `knowrithm admin users list` |
| 🔧 **system** | System utilities | `knowrithm system health` |

## ⚡ Quick Actions

### Agent Management
```bash
# Create agent (interactive)
knowrithm agent create --interactive

# List agents (beautiful table)
knowrithm agent list --format table

# Get agent details
knowrithm agent get "Agent Name"

# Update agent
knowrithm agent update "Agent Name" --name "New Name"

# Test agent
knowrithm agent test "Agent Name" --query "Hello"

# Get statistics
knowrithm agent stats "Agent Name"
```

### Conversations
```bash
# List conversations
knowrithm conversation list

# View messages (timeline format)
knowrithm conversation messages <conversation_id>

# Send message
knowrithm conversation chat <conversation_id> --message "Hello"
```

### Admin Tasks
```bash
# View audit logs
knowrithm admin audit-log --entity-type agent --risk-level high

# View system metrics
knowrithm admin metrics

# List users
knowrithm admin users list
```

### Context Management
```bash
# Set active agent
knowrithm context set agent "Agent Name"

# View current context
knowrithm context show

# Clear context
knowrithm context clear all
```

## 🎨 Output Formats

All list commands support multiple formats:

```bash
# Table format (default for lists)
knowrithm agent list --format table

# JSON format
knowrithm agent list --format json

# YAML format
knowrithm agent list --format yaml

# CSV format (for exports)
knowrithm agent list --format csv > agents.csv

# Tree format (hierarchical view)
knowrithm agent get "Agent Name" --format tree
```

## 🔍 Filtering & Search

```bash
# Filter by status
knowrithm agent list --status active

# Search by name
knowrithm agent list --search "support"

# Pagination
knowrithm agent list --page 2 --per-page 50

# Multiple filters
knowrithm conversation entity \
  --entity-type lead \
  --status open \
  --page 1
```

## 🔐 Authentication

```bash
# Login with email/password
knowrithm auth login

# Check current user
knowrithm auth me

# Refresh token
knowrithm auth refresh

# Logout
knowrithm auth logout

# Validate credentials
knowrithm auth validate
```

## 📊 Analytics

```bash
# Dashboard
knowrithm analytics dashboard

# Agent analytics
knowrithm analytics agent <agent_id>

# Lead analytics
knowrithm analytics leads --start-date 2025-01-01

# Usage analytics
knowrithm analytics usage
```

## 🛠️ Configuration

```bash
# View current config
knowrithm config show

# Set base URL
knowrithm config set-base-url https://your-instance.com

# SSL verification
knowrithm config set-verify-ssl --enable
knowrithm config set-verify-ssl --disable

# Config file path
knowrithm config path
```

## 💡 Tips & Tricks

### Use Names Instead of UUIDs
```bash
# ✅ Easy to remember
knowrithm agent get "Support Bot"

# ❌ Hard to remember
knowrithm agent get abc123-def456-789...
```

### Set Context for Faster Workflows
```bash
# Set once
knowrithm context set agent "Support Bot"

# Use many times without specifying agent
knowrithm agent stats
knowrithm agent test --query "Hello"
knowrithm agent embed-code
```

### Interactive Mode for Complex Operations
```bash
# Guided wizard
knowrithm agent create --interactive

# Follow the prompts - much easier!
```

### Export Data
```bash
# Export to CSV
knowrithm agent list --format csv > agents.csv

# Export to JSON
knowrithm conversation list --format json > conversations.json

# Pipe to jq for processing
knowrithm agent list --format json | jq '.data[] | {name, status}'
```

### Batch Operations
```bash
# Loop through pages
for i in {1..5}; do
  knowrithm agent list --page $i --per-page 20
done

# Bulk delete
knowrithm document bulk-delete --payload '{"document_ids": ["id1", "id2"]}'
```

## 🆘 Help & Support

### Get Help
```bash
# General help
knowrithm --help

# Command-specific help
knowrithm agent --help
knowrithm agent create --help

# View version
knowrithm --version
```

### Troubleshooting
```bash
# Check configuration
knowrithm config show

# Test connection
knowrithm system health

# Validate auth
knowrithm auth validate

# Clear and re-login
knowrithm auth clear --all
knowrithm auth login
```

### Resources
- **Dashboard**: `knowrithm dashboard`
- **Documentation**: https://docs.knowrithm.org
- **Support**: agentx@notifications.knowrithm.org
- **User Guide**: See `USER_GUIDE.md`
- **Command Reference**: See `COMMAND_REFERENCE.md`

## 🎯 Common Workflows

### Create and Test Agent
```bash
# 1. Create
knowrithm agent create --interactive

# 2. Set as active
knowrithm context set agent "My Agent"

# 3. Upload documents
knowrithm document upload --agent-id <id> --file ./docs/faq.pdf

# 4. Test
knowrithm agent test --query "What is your refund policy?"

# 5. Get embed code
knowrithm agent embed-code
```

### Monitor Conversations
```bash
# 1. List recent conversations
knowrithm conversation list --per-page 10

# 2. View specific conversation
knowrithm conversation messages <conversation_id>

# 3. Get analytics
knowrithm analytics conversation <conversation_id>
```

### Admin Monitoring
```bash
# 1. View audit logs
knowrithm admin audit-log --per-page 20

# 2. Filter by risk
knowrithm admin audit-log --risk-level high

# 3. Check metrics
knowrithm admin metrics

# 4. List users
knowrithm admin users list
```

---

**💡 Pro Tip**: Start every session with `knowrithm dashboard` to see all available commands and quick actions!
