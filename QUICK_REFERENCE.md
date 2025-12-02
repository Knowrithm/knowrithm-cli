# Knowrithm CLI - Quick Reference

## Setup & Authentication

```bash
# Configure API endpoint
knowrithm config set-base-url https://app.knowrithm.org/api

# Login
knowrithm auth login

# Check authentication
knowrithm auth me

# Set API key (alternative to JWT)
knowrithm auth set-api-key
```

## Context Management (NEW!)

```bash
# Set active agent (use name, not UUID!)
knowrithm context set agent "Support Bot"

# Set active conversation
knowrithm context set conversation "Customer Chat"

# View current context
knowrithm context show

# Clear context
knowrithm context clear all
```

## Agent Management

```bash
# Create agent (interactive wizard)
knowrithm agent create --interactive

# Create agent (quick)
knowrithm agent create --name "Sales Bot" --description "Sales assistant"

# List agents (beautiful table)
knowrithm agent list --format table

# Get agent by name (not UUID!)
knowrithm agent get "Support Bot"

# Update agent
knowrithm agent update "Support Bot" --status active

# Get agent stats
knowrithm agent stats "Support Bot"

# Test agent
knowrithm agent test "Support Bot" --query "Hello"

# Clone agent
knowrithm agent clone "Support Bot" --new-name "Support Bot Copy"

# Delete agent
knowrithm agent delete "Support Bot"

# Get embed code
knowrithm agent embed-code "Support Bot"
```

## Using Context (Faster Workflow)

```bash
# Set agent once
knowrithm context set agent "Support Bot"

# Then use commands without specifying agent
knowrithm agent stats              # Uses active agent
knowrithm agent test --query "Hi"  # Uses active agent
knowrithm agent embed-code         # Uses active agent
```

## Conversations

```bash
# List conversations
knowrithm conversation list --format table

# List for specific agent
knowrithm conversation agent "Support Bot"

# View messages
knowrithm conversation messages <conversation-id>

# Send message
knowrithm conversation chat <conversation-id> --payload '{"message": "Hello"}'

# Delete conversation
knowrithm conversation delete <conversation-id>
```

## Documents & Training

```bash
# Upload documents
knowrithm document upload --agent-id <id> --files doc1.pdf doc2.docx

# Upload from URL
knowrithm document upload --agent-id <id> --url https://example.com

# List documents
knowrithm document list --format table

# List for specific agent
knowrithm document agent <agent-id>

# Delete document
knowrithm document delete <document-id>
```

## Database Connections

```bash
# Create connection
knowrithm database create --payload '{
  "name": "Production DB",
  "url": "postgresql://...",
  "database_type": "postgres",
  "agent_id": "..."
}'

# List connections
knowrithm database list

# Test connection
knowrithm database test <connection-id>

# Analyze schema
knowrithm database analyze <connection-id>

# Text-to-SQL
knowrithm database query <connection-id> --question "Show sales by month"
```

## Website Awareness

```bash
# Register website
knowrithm website create --payload '{
  "agent_id": "...",
  "base_url": "https://example.com"
}'

# List websites
knowrithm website list

# Trigger crawl
knowrithm website crawl <source-id>

# View pages
knowrithm website pages <source-id>
```

## Analytics

```bash
# Dashboard analytics
knowrithm analytics dashboard

# Agent analytics
knowrithm analytics agent <agent-id> --start-date 2024-01-01

# Lead analytics
knowrithm analytics leads --days 30

# Export analytics
knowrithm analytics export --type conversations --format csv > data.csv
```

## Admin Commands

```bash
# List users
knowrithm admin users list --format table

# Filter users
knowrithm admin users list --role admin --status active

# Audit logs
knowrithm admin audit-log --entity-type agent

# System metrics
knowrithm admin system-metrics
```

## Output Formats

```bash
# Table (best for lists)
knowrithm agent list --format table

# JSON (default for details)
knowrithm agent get "Support Bot" --format json

# Tree (best for hierarchical data)
knowrithm agent stats "Support Bot" --format tree

# CSV (for exports)
knowrithm agent list --format csv > agents.csv

# YAML
knowrithm agent get "Support Bot" --format yaml
```

## Tips & Tricks

### Use Names, Not UUIDs
```bash
# ✅ Good
knowrithm agent get "Support Bot"

# ❌ Avoid (but still works)
knowrithm agent get abc123-def456-...
```

### Set Context for Efficiency
```bash
# Set once
knowrithm context set agent "Support Bot"

# Use many times without specifying agent
knowrithm agent stats
knowrithm agent test --query "Hello"
knowrithm agent embed-code
```

### Use Interactive Mode for Complex Operations
```bash
# Guided wizard
knowrithm agent create --interactive

# Better than remembering JSON structure
```

### Use Table Format for Better Readability
```bash
# Much easier to read
knowrithm agent list --format table
knowrithm conversation list --format table
```

### Export Data for Analysis
```bash
# Export to CSV
knowrithm agent list --format csv > agents.csv
knowrithm analytics export --type conversations --format csv > data.csv
```

## Common Workflows

### Create and Train an Agent
```bash
# 1. Create agent
knowrithm agent create --interactive

# 2. Set as active
knowrithm context set agent "My New Agent"

# 3. Upload training documents
knowrithm document upload --agent-id <id> --files docs/*.pdf

# 4. Add website knowledge
knowrithm website create --payload '{
  "agent_id": "<id>",
  "base_url": "https://mysite.com"
}'

# 5. Test the agent
knowrithm agent test --query "What can you help me with?"
```

### Monitor Agent Performance
```bash
# Set active agent
knowrithm context set agent "Support Bot"

# View stats
knowrithm agent stats --format tree

# View analytics
knowrithm analytics agent <agent-id> --days 30

# View conversations
knowrithm conversation agent "Support Bot" --format table
```

### Manage Users (Admin)
```bash
# List all users
knowrithm admin users list --format table

# Find specific user
knowrithm admin users list --search "john"

# Filter by role
knowrithm admin users list --role admin

# View audit log
knowrithm admin audit-log --limit 50
```

## Getting Help

```bash
# General help
knowrithm --help

# Command group help
knowrithm agent --help

# Specific command help
knowrithm agent create --help

# Version
knowrithm --version
```

## Troubleshooting

### Authentication Issues
```bash
# Check current auth
knowrithm auth me

# Re-login
# Re-login
knowrithm auth clear --all
knowrithm auth login
```

### Name Resolution Issues
```bash
# Use ID directly if name fails
knowrithm agent get abc123-def456-...

# Check available agents
knowrithm agent list --format table
```

### Clear Cache
```bash
# If getting stale data
knowrithm config clear-cache
```

## Support

- **Docs**: https://docs.knowrithm.org
- **Discord**: https://discord.gg/knowrithm
- **Email**: agentx@notifications.knowrithm.org
- **GitHub**: https://github.com/knowrithm/knowrithm-cli
