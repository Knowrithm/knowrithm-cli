# Knowrithm CLI - User Guide

## Overview

The Knowrithm CLI is a powerful command-line interface for managing your Knowrithm platform. This enhanced version includes user-friendly features like name-based lookups, interactive modes, context management, and beautiful output formatting.

## Installation

```bash
# Install from source
cd knowrithm-cli
# Set your API base URL
knowrithm config set-base-url https://app.knowrithm.org/api

# Login with your credentials
knowrithm auth login
# Enter your email and password when prompted

# Or use API keys
knowrithm auth set-api-key
# Enter your API key and secret when prompted
```

### 2. Verify Your Setup

```bash
# Check your authentication
knowrithm auth me

# View current configuration
knowrithm config show
```

## Core Concepts

### Context Management

The CLI maintains context to reduce repetitive typing. You can set an active agent, conversation, or organization, and subsequent commands will use these defaults.

```bash
# Set active agent
knowrithm context set agent "Support Bot"

# Set active conversation
knowrithm context set conversation "Customer Chat #123"

# View current context
knowrithm context show

# Clear context
knowrithm context clear all
```

### Name-Based Lookups

Instead of remembering UUIDs, you can use human-friendly names:

```bash
# Get agent by name (not UUID)
knowrithm agent get "Support Bot"

# Update agent by name
knowrithm agent update "Support Bot" --status inactive

# The CLI automatically resolves names to IDs
```

### Output Formatting

Choose your preferred output format:

```bash
# Table format (default for lists)
knowrithm agent list --format table

# JSON format
knowrithm agent get "Support Bot" --format json

# Tree format (great for hierarchical data)
knowrithm agent stats "Support Bot" --format tree

# CSV format (for exports)
knowrithm agent list --format csv > agents.csv

# YAML format
knowrithm agent get "Support Bot" --format yaml
```

## Agent Management

### Creating Agents

#### Interactive Mode (Recommended for Beginners)

```bash
knowrithm agent create --interactive
```

This launches a wizard that guides you through agent creation.

#### Quick Create

```bash
knowrithm agent create --name "Sales Bot" --description "Handles sales inquiries"
```

#### From JSON File

```bash
# Create agent-config.json
cat > agent-config.json <<EOF
{
  "name": "Support Bot",
  "description": "Customer support agent",
  "status": "active",
  "personality_traits": ["helpful", "friendly", "professional"],
  "capabilities": ["chat", "search", "database_query"]
}
EOF

# Create agent from file
knowrithm agent create --payload @agent-config.json
```

### Listing Agents

```bash
# List all agents (table format)
knowrithm agent list

# Search agents
knowrithm agent list --search "support"

# Filter by status
knowrithm agent list --status active

# JSON output
knowrithm agent list --format json

# With pagination
knowrithm agent list --page 2 --per-page 50
```

### Getting Agent Details

```bash
# By name
knowrithm agent get "Support Bot"

# By ID (still works)
knowrithm agent get abc123-def456-...

# Tree format for better readability
knowrithm agent get "Support Bot" --format tree
```

### Updating Agents

```bash
# Update name
knowrithm agent update "Support Bot" --name "Customer Support Bot"

# Update status
knowrithm agent update "Support Bot" --status inactive

# Update description
knowrithm agent update "Support Bot" --description "New description"

# Update from JSON
knowrithm agent update "Support Bot" --payload '{"status": "active", "description": "Updated"}'
```

### Testing Agents

```bash
# Test with a query
knowrithm agent test "Support Bot" --query "What is your refund policy?"

# Test using active agent (from context)
knowrithm context set agent "Support Bot"
knowrithm agent test --query "Hello, how can you help me?"
```

### Agent Statistics

```bash
# Get stats for specific agent
knowrithm agent stats "Support Bot"

# Use active agent from context
knowrithm context set agent "Support Bot"
knowrithm agent stats

# Tree format for better visualization
knowrithm agent stats "Support Bot" --format tree
```

### Cloning Agents

```bash
# Clone with new name
knowrithm agent clone "Support Bot" --new-name "Support Bot Copy"

# Clone with custom settings
knowrithm agent clone "Support Bot" --payload '{"name": "New Bot", "description": "Cloned agent"}'
```

### Deleting and Restoring Agents

```bash
# Delete agent (with confirmation)
knowrithm agent delete "Support Bot"

# Delete without confirmation
knowrithm agent delete "Support Bot" --yes

# Restore deleted agent
knowrithm agent restore "Support Bot"
```

### Getting Embed Code

```bash
# Get widget embed code
knowrithm agent embed-code "Support Bot"

# Using active agent
knowrithm context set agent "Support Bot"
knowrithm agent embed-code
```

## Conversation Management

### Starting Conversations

```bash
# Start new conversation with an agent
knowrithm conversation start "Support Bot"

# Create with custom title
knowrithm conversation create --payload '{"agent_id": "...", "title": "Customer Issue #123"}'
```

### Listing Conversations

```bash
# List all conversations
knowrithm conversation list

# List for specific agent
knowrithm conversation agent "Support Bot"

# List for current user/lead
knowrithm conversation entity

# Filter by status
knowrithm conversation list --status open

# Table format
knowrithm conversation list --format table
```

### Viewing Messages

```bash
# View messages in a conversation
knowrithm conversation messages <conversation-id>

# With pagination
knowrithm conversation messages <conversation-id> --page 1 --per-page 50
```

### Sending Messages

```bash
# Send a message
knowrithm conversation chat <conversation-id> --payload '{"message": "Hello, I need help"}'

# Interactive chat mode
knowrithm conversation chat <conversation-id> --interactive
```

### Managing Conversations

```bash
# Delete conversation
knowrithm conversation delete <conversation-id>

# Restore conversation
knowrithm conversation restore <conversation-id>

# Delete all messages
knowrithm conversation delete-messages <conversation-id>

# Restore all messages
knowrithm conversation restore-messages <conversation-id>

# List deleted conversations
knowrithm conversation deleted
```

## Training & Knowledge Management

### Document Upload

```bash
# Upload documents to train an agent
knowrithm document upload --agent-id <agent-id> --files doc1.pdf doc2.docx

# Upload from URL
knowrithm document upload --agent-id <agent-id> --url https://example.com/docs

# List documents
knowrithm document list

# List documents for specific agent
knowrithm document agent <agent-id>

# Delete document
knowrithm document delete <document-id>
```

### Database Connections

```bash
# Create database connection
knowrithm database create --payload '{
  "name": "Production DB",
  "url": "postgresql://user:pass@localhost:5432/db",
  "database_type": "postgres",
  "agent_id": "..."
}'

# List connections
knowrithm database list

# Test connection
knowrithm database test <connection-id>

# Analyze database schema
knowrithm database analyze <connection-id>

# Text-to-SQL query
knowrithm database query <connection-id> --question "Show me total sales by month"
```

### Website Awareness

```bash
# Register a website
knowrithm website create --payload '{
  "agent_id": "...",
  "base_url": "https://example.com",
  "seed_urls": ["https://example.com/docs"]
}'

# List websites
knowrithm website list

# Trigger crawl
knowrithm website crawl <source-id>

# View crawled pages
knowrithm website pages <source-id>
```

## Analytics

### Dashboard Analytics

```bash
# View dashboard analytics
knowrithm analytics dashboard

# Agent-specific analytics
knowrithm analytics agent <agent-id> --start-date 2024-01-01 --end-date 2024-12-31

# Lead analytics
knowrithm analytics leads --days 30

# Usage analytics
knowrithm analytics usage --start-date 2024-01-01

# Export analytics
knowrithm analytics export --type conversations --format csv > conversations.csv
```

## Admin Commands

### User Management

```bash
# List users
knowrithm admin users list

# Filter users
knowrithm admin users list --role admin --status active

# Search users
knowrithm admin users list --search "john"

# Get specific user
knowrithm admin users get <user-id>

# Update user status
knowrithm admin users update-status <user-id> --status suspended

# Update user role
knowrithm admin users update-role <user-id> --role admin
```

### Audit Logs

```bash
# View audit logs
knowrithm admin audit-log

# Filter by entity type
knowrithm admin audit-log --entity-type agent

# Filter by risk level
knowrithm admin audit-log --risk-level high
```

### System Metrics

```bash
# View system metrics
knowrithm admin system-metrics

# For specific company (super admin)
knowrithm admin system-metrics --company-id <company-id>
```

## Super Admin Commands

### Company Management

```bash
# List companies
knowrithm superadmin companies list

# Get company details
knowrithm superadmin companies get <company-id>

# Create company
knowrithm superadmin companies create --payload '{
  "name": "Acme Corp",
  "email": "admin@acme.com"
}'

# Update company
knowrithm superadmin companies update <company-id> --payload '{"name": "New Name"}'

# Delete company
knowrithm superadmin companies delete <company-id>
```

### Advanced Analytics

```bash
# User engagement analytics
knowrithm superadmin analytics user-engagement

# Change tracking
knowrithm superadmin analytics change-tracking --risk-level high

# Agent performance trends
knowrithm superadmin analytics agent-performance-trends

# Retention analytics
knowrithm superadmin analytics retention

# Comparative analytics
knowrithm superadmin analytics comparative --compare-by companies
```

### System Health

```bash
# System health check
knowrithm superadmin system health

# System metrics
knowrithm superadmin system metrics --interval day
```

## Configuration

### Viewing Configuration

```bash
# Show current configuration
knowrithm config show
```

### Setting Base URL

```bash
# Set API base URL
knowrithm config set-base-url https://app.knowrithm.org/api
```

### SSL Verification

```bash
# Disable SSL verification (not recommended for production)
knowrithm config set-verify-ssl false

# Enable SSL verification
knowrithm config set-verify-ssl true
```

### Managing Credentials

```bash
# Clear JWT tokens
knowrithm auth clear --tokens

# Clear API keys
knowrithm auth clear --api-key

# Clear all credentials
knowrithm auth clear --all
```

## Tips & Best Practices

### 1. Use Context for Efficiency

```bash
# Set active agent once
knowrithm context set agent "Support Bot"

# Then use commands without specifying agent
knowrithm agent stats
knowrithm agent test --query "Hello"
knowrithm agent embed-code
```

### 2. Use Table Format for Lists

```bash
# Much easier to read than JSON
knowrithm agent list --format table
knowrithm conversation list --format table
```

### 3. Use Tree Format for Details

```bash
# Better visualization of hierarchical data
knowrithm agent get "Support Bot" --format tree
knowrithm agent stats "Support Bot" --format tree
```

### 4. Use Names Instead of IDs

```bash
# Easier to remember and type
knowrithm agent get "Support Bot"
knowrithm agent update "Support Bot" --status active

# Instead of
knowrithm agent get abc123-def456-...
```

### 5. Use Interactive Mode for Complex Operations

```bash
# Guided wizard for agent creation
knowrithm agent create --interactive

# Less error-prone than JSON payloads
```

### 6. Export Data for Analysis

```bash
# Export to CSV for Excel/Google Sheets
knowrithm agent list --format csv > agents.csv
knowrithm analytics export --type conversations --format csv > conversations.csv
```

### 7. Use Fuzzy Matching

```bash
# CLI will suggest close matches if exact name not found
knowrithm agent get "Suport Bot"
# Did you mean 'Support Bot'? Using that instead of 'Suport Bot'.
```

## Troubleshooting

### Authentication Issues

```bash
# Verify your credentials
knowrithm auth me

# Re-login if needed
knowrithm auth logout
knowrithm auth login

# Or refresh tokens
knowrithm auth refresh
```

### Name Resolution Issues

```bash
# Clear name cache if getting stale results
knowrithm config clear-cache

# Use ID directly if name resolution fails
knowrithm agent get abc123-def456-...
```

### API Errors

```bash
# Check your base URL
knowrithm config show

# Verify SSL settings
knowrithm config set-verify-ssl true

# Check API status
curl https://app.knowrithm.org/api/health
```

## Getting Help

```bash
# General help
knowrithm --help

# Command group help
knowrithm agent --help

# Specific command help
knowrithm agent create --help

# Show version
knowrithm --version
```

## Examples Repository

For more examples and use cases, check out the examples directory:

```bash
# Clone the repository
git clone https://github.com/knowrithm/knowrithm-cli.git
cd knowrithm-cli/examples

# Run example scripts
./create-agent.sh
./train-agent.sh
./chat-with-agent.sh
```

## Support

- **Documentation**: https://docs.knowrithm.org
- **Discord**: https://discord.gg/knowrithm
- **Email**: agentx@notifications.knowrithm.org
- **GitHub Issues**: https://github.com/knowrithm/knowrithm-cli/issues

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details
