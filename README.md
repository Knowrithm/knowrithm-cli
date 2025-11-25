# Knowrithm CLI

A comprehensive Python command-line interface for the Knowrithm enterprise multi-agent chatbot platform. The CLI provides full access to the REST API, enabling developers and operators to manage agents, ingest content, handle leads, analyze conversations, and query analytics directly from the terminal.

## 🎉 What's New - Enhanced User Experience!

The CLI has been significantly improved with user-friendly features:

- **✨ Name-Based Lookups**: Use agent names instead of UUIDs (`knowrithm agent get "Support Bot"`)
- **🎯 Context Management**: Set active agent/conversation once, use everywhere
- **🧙 Interactive Wizards**: Step-by-step guided agent creation
- **📊 Beautiful Formatting**: Table, tree, CSV, and YAML output formats
- **🔍 Fuzzy Matching**: "Did you mean?" suggestions for typos
- **⚡ Quick Commands**: Update agents without complex JSON payloads
- **💡 Better Errors**: Meaningful messages with helpful suggestions

**See [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md) for details, [USER_GUIDE.md](USER_GUIDE.md) for comprehensive examples, and [PYTHON_SDK_EXAMPLES.md](PYTHON_SDK_EXAMPLES.md) for Python code examples.**

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Command Reference](#command-reference)
- [Common Workflows](#common-workflows)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Features

### Core Capabilities
- **Authentication Management**: JWT sessions, API key credentials, token refresh
- **Agent Lifecycle**: Create, clone, update, delete, restore, statistics, testing, embed code generation
- **Conversation Management**: List, create, chat, message handling, entity-scoped queries
- **Document Ingestion**: File uploads, URL scraping, semantic search, chunk management
- **Database Integration**: Connection management, schema analysis, knowledge graphs, text-to-SQL, data exports
- **Analytics & Reporting**: Dashboards, agent performance, lead analytics, usage metrics, data exports
- **Lead Management**: Registration, creation, updates, status tracking
- **Company Administration**: Tenant management, bulk operations, statistics
- **Website Awareness**: Source registration, crawling, page discovery
- **LLM Settings**: Provider configuration, model selection, testing
- **System Utilities**: Health checks, task status polling, geographic data

### Enhanced User Experience (NEW!)
- **Name Resolution**: Reference resources by name instead of UUID
- **Context Management**: Maintain active agent, conversation, organization
- **Interactive Modes**: Guided wizards for complex operations
- **Multiple Output Formats**: JSON, table, tree, CSV, YAML
- **Fuzzy Matching**: Typo-tolerant name lookups
- **Quick Options**: Common operations without JSON payloads
- **Better Error Handling**: Meaningful messages with suggestions

### Technical Features
- Asynchronous task support with optional polling (`--wait` flags)
- JSON payload loading from files or inline strings
- Flexible authentication strategies
- Comprehensive error handling
- Pagination support for list operations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone or download the CLI package**
   ```bash
   cd /path/to/knowrithm-cli
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   
   # Activate on Linux/macOS
   source .venv/bin/activate
   
   # Activate on Windows
   .venv\Scripts\activate
   ```

3. **Install the CLI in editable mode**
   ```bash
   pip install -e .
   ```

4. **Verify installation**
   ```bash
   knowrithm --version
   knowrithm --help
   ```

The `knowrithm` executable will be available on your `$PATH` after installation.

## Quick Start

### 0. Launch Interactive Dashboard (NEW!)

```bash
# View the beautiful Knowrithm dashboard with all commands
knowrithm dashboard
```

This displays a gorgeous ASCII logo and interactive menu with all available commands, quick actions, and helpful information!

### 1. Initial Setup

```bash
# Set API endpoint
knowrithm config set-base-url https://app.knowrithm.org/api

# Login
knowrithm auth login
# Enter your email and password when prompted
```

### 2. Create Your First Agent (Interactive Mode)

```bash
# Launch interactive wizard
knowrithm agent create --interactive

# Follow the prompts:
# - Agent name: "Support Bot"
# - Description: "Customer support agent"
# - Configure advanced settings? No
```

### 3. Set Active Agent (Context)

```bash
# Set as active agent
knowrithm context set agent "Support Bot"

# Now you can use commands without specifying the agent
knowrithm agent stats
knowrithm agent test --query "Hello, how can you help?"
```

### 4. List Agents (Beautiful Table Format)

```bash
# View all agents in a formatted table
knowrithm agent list --format table
```

### 5. Get Agent Details by Name

```bash
# No need to remember UUIDs!
knowrithm agent get "Support Bot" --format tree
```

**That's it!** You're ready to use the CLI. See [USER_GUIDE.md](USER_GUIDE.md) for more examples and [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for a command cheat sheet.

## Configuration

### Initial Setup

1. **Set the API base URL**
   ```bash
   knowrithm config set-base-url https://your-knowrithm-instance.com
   ```
   
   For local development:
   ```bash
   knowrithm config set-base-url http://localhost:8000
   ```

2. **Configure TLS verification (optional)**
   ```bash
   # Disable for self-signed certificates (development only)
   knowrithm config set-verify-ssl --disable
   
   # Enable for production
   knowrithm config set-verify-ssl --enable
   ```

3. **View current configuration**
   ```bash
   knowrithm config show
   ```

4. **Get configuration file path**
   ```bash
   knowrithm config path
   ```

### Configuration File

Configuration is stored in `~/.knowrithm/config.json` with the following structure:

```json
{
  "base_url": "https://app.knowrithm.org",
  "verify_ssl": true,
  "auth": {
    "jwt": {
      "access_token": "...",
      "refresh_token": "...",
      "expires_at": 1234567890
    },
    "api_key": {
      "key": "...",
      "secret": "***"
    }
  }
}
```

## Authentication

The CLI supports three authentication methods:

### 1. Email/Password (JWT)

**Login and store tokens**
```bash
knowrithm auth login --email admin@example.com --password
# Password will be prompted securely
```

**Check current user**
```bash
knowrithm auth me
```

**Refresh expired tokens**
```bash
knowrithm auth refresh
```

**Logout and clear tokens**
```bash
knowrithm auth logout
```

### 2. API Key/Secret

**Store API credentials**
```bash
knowrithm auth set-api-key --key YOUR_KEY --secret YOUR_SECRET
```

**Clear API credentials only**
```bash
knowrithm auth clear --api-key
```

### 3. Public Registration

**Register a new company admin account**
```bash
knowrithm auth register --payload '{
  "email": "admin@newcompany.com",
  "password": "SecurePass123!",
  "company_name": "New Company LLC",
  "first_name": "John",
  "last_name": "Doe"
}'
```

Or using a file:
```bash
knowrithm auth register --payload @registration.json
```

### Validation

**Validate current credentials**
```bash
knowrithm auth validate
```

### Authentication Strategy Selection

Most commands accept `--auth` to specify the authentication method:

```bash
# Auto-select (default: tries JWT first, then API key)
knowrithm agent list --auth auto

# Force JWT authentication
knowrithm agent list --auth jwt

# Force API key authentication
knowrithm agent list --auth api-key

# No authentication (public endpoints only)
knowrithm system health --auth none
```

## Command Reference

### Agent Management

```bash
# List all agents
knowrithm agent list [OPTIONS]
  --company-id TEXT       Filter by company ID (super admin only)
  --status TEXT          Filter by agent status
  --search TEXT          Search string for name/description
  --page INTEGER         Page number (default: 1)
  --per-page INTEGER     Items per page (default: 20)

# Get specific agent
knowrithm agent get AGENT_ID

# Create new agent
knowrithm agent create --payload PAYLOAD [--wait/--no-wait]

# Clone existing agent
knowrithm agent clone AGENT_ID [--payload OVERRIDES] [--wait/--no-wait]

# Update agent
knowrithm agent update AGENT_ID --payload PAYLOAD [--wait/--no-wait]

# Delete agent (soft delete)
knowrithm agent delete AGENT_ID [--wait/--no-wait]

# Restore deleted agent
knowrithm agent restore AGENT_ID [--wait/--no-wait]

# Get agent statistics
knowrithm agent stats AGENT_ID

# Test agent
knowrithm agent test AGENT_ID [--payload TEST_PAYLOAD] [--wait/--no-wait]

# Get embed code
knowrithm agent embed-code AGENT_ID
```

### Conversation Management

```bash
# List all conversations
knowrithm conversation list [--page INT] [--per-page INT]

# List conversations by entity
knowrithm conversation entity [OPTIONS]
  --entity-id TEXT       Specific entity ID
  --entity-type TEXT     Filter by entity type (lead/user)
  --status TEXT          Conversation status filter
  --page INTEGER         Page number
  --per-page INTEGER     Items per page

# List conversations by agent
knowrithm conversation agent AGENT_ID [OPTIONS]
  --status TEXT          Filter by conversation status
  --page INTEGER         Page number
  --per-page INTEGER     Items per page

# Create new conversation
knowrithm conversation create --payload PAYLOAD [--wait/--no-wait]

# Get messages for conversation
knowrithm conversation messages CONVERSATION_ID [--page INT] [--per-page INT]

# Send chat message
knowrithm conversation chat CONVERSATION_ID --payload MESSAGE [--wait/--no-wait]

# Delete conversation
knowrithm conversation delete CONVERSATION_ID

# Restore conversation
knowrithm conversation restore CONVERSATION_ID

# Delete all messages in conversation
knowrithm conversation delete-messages CONVERSATION_ID

# Restore all messages in conversation
knowrithm conversation restore-messages CONVERSATION_ID

# List deleted conversations
knowrithm conversation deleted
```

### Document Management

```bash
# List all documents
knowrithm document list [--page INT] [--per-page INT]

# List documents for agent
knowrithm document agent AGENT_ID [--page INT] [--per-page INT]

# Upload documents
knowrithm document upload --agent-id AGENT_ID [OPTIONS]
  --file PATH            Path to file (can be used multiple times)
  --url URL              URL to ingest (can be used multiple times)
  --payload JSON         Additional JSON fields

# Delete document
knowrithm document delete DOCUMENT_ID

# Restore document
knowrithm document restore DOCUMENT_ID

# Delete all chunks for document
knowrithm document delete-chunks DOCUMENT_ID

# Restore all chunks for document
knowrithm document restore-chunks DOCUMENT_ID

# Delete single chunk
knowrithm document delete-chunk CHUNK_ID

# Restore single chunk
knowrithm document restore-chunk CHUNK_ID

# List deleted documents
knowrithm document deleted

# List deleted chunks
knowrithm document deleted-chunks

# Bulk delete documents
knowrithm document bulk-delete --payload '{"document_ids": [...]}'

# Semantic search
knowrithm document search --payload SEARCH_PAYLOAD
```

### Database Management

```bash
# List database connections
knowrithm database list

# List deleted connections
knowrithm database deleted

# Create connection
knowrithm database create --payload CONNECTION_CONFIG

# Get connection details
knowrithm database get CONNECTION_ID

# Delete connection
knowrithm database delete CONNECTION_ID

# Restore connection
knowrithm database restore CONNECTION_ID

# Test connection
knowrithm database test CONNECTION_ID

# Analyze connection (semantic analysis)
knowrithm database analyze CONNECTION_ID [--wait/--no-wait]

# Analyze all connections
knowrithm database analyze-all [--payload FILTERS] [--wait/--no-wait]

# List tables for connection
knowrithm database tables CONNECTION_ID [--page INT] [--per-page INT]

# Get table metadata
knowrithm database table TABLE_ID

# Delete table metadata
knowrithm database table-delete TABLE_ID

# Restore table metadata
knowrithm database table-restore TABLE_ID

# Get semantic snapshot
knowrithm database semantic-snapshot CONNECTION_ID

# Get knowledge graph
knowrithm database knowledge-graph CONNECTION_ID

# Get sample queries
knowrithm database sample-queries CONNECTION_ID

# Text-to-SQL generation
knowrithm database text-to-sql CONNECTION_ID --payload '{"question": "..."}'

# Export database content
knowrithm database export --payload EXPORT_CONFIG
```

### Analytics & Reporting

```bash
# Get analytics dashboard
knowrithm analytics dashboard [--company-id COMPANY_ID]

# Get agent analytics
knowrithm analytics agent AGENT_ID [OPTIONS]
  --start-date ISO_DATE  Start date filter
  --end-date ISO_DATE    End date filter

# Get agent performance comparison
knowrithm analytics agent-performance AGENT_ID [OPTIONS]
  --start-date ISO_DATE
  --end-date ISO_DATE

# Get conversation analytics
knowrithm analytics conversation CONVERSATION_ID

# Get lead analytics
knowrithm analytics leads [OPTIONS]
  --start-date ISO_DATE
  --end-date ISO_DATE
  --company-id TEXT      Super admin override

# Get usage analytics
knowrithm analytics usage [OPTIONS]
  --start-date ISO_DATE
  --end-date ISO_DATE

# Export analytics data
knowrithm analytics export --payload EXPORT_CONFIG
```

### Lead Management

```bash
# Public lead registration (no auth)
knowrithm lead register --payload REGISTRATION_PAYLOAD

# Create lead (authenticated)
knowrithm lead create --payload LEAD_DATA

# List company leads
knowrithm lead list [OPTIONS]
  --status TEXT          Filter by lead status
  --search TEXT          Search by name/email
  --page INTEGER         Page number
  --per-page INTEGER     Items per page

# Get specific lead
knowrithm lead get LEAD_ID

# Update lead
knowrithm lead update LEAD_ID --payload UPDATE_DATA

# Delete lead
knowrithm lead delete LEAD_ID
```

### Company Management

```bash
# List companies (super admin)
knowrithm company list [--page INT] [--per-page INT]

# Get current company
knowrithm company current

# Get specific company
knowrithm company get COMPANY_ID

# Create company (public onboarding)
knowrithm company create --payload COMPANY_DATA

# Update company
knowrithm company update COMPANY_ID --payload UPDATE_DATA

# Partial update company
knowrithm company patch COMPANY_ID --payload PARTIAL_DATA

# Delete company
knowrithm company delete COMPANY_ID

# Restore company
knowrithm company restore COMPANY_ID

# List deleted companies
knowrithm company deleted

# Bulk delete companies
knowrithm company bulk-delete --payload '{"company_ids": [...]}'

# Bulk restore companies
knowrithm company bulk-restore --payload '{"company_ids": [...]}'

# Get company statistics
knowrithm company statistics [COMPANY_ID] [--days INT]

# Get related data counts
knowrithm company related-data COMPANY_ID

# Cascade delete (super admin)
knowrithm company cascade-delete COMPANY_ID [--payload OPTIONS]
```

### LLM Settings Management

```bash
# Create settings (using provider/model IDs)
knowrithm settings create --payload SETTINGS_DATA [--wait/--no-wait]

# Create settings (using provider/model names - SDK endpoint)
knowrithm settings create-sdk --payload SETTINGS_DATA [--wait/--no-wait]

# List settings for company
knowrithm settings list-company COMPANY_ID

# List settings for agent
knowrithm settings list-agent AGENT_ID

# Get specific settings
knowrithm settings get SETTINGS_ID

# Update settings
knowrithm settings update SETTINGS_ID --payload UPDATE_DATA [--wait/--no-wait]

# Delete settings
knowrithm settings delete SETTINGS_ID [--wait/--no-wait]

# Test settings
knowrithm settings test SETTINGS_ID [--payload OVERRIDES] [--wait/--no-wait]
```

### Website Awareness

```bash
# List website sources
knowrithm website list [--agent-id AGENT_ID]

# List sources for specific agent
knowrithm website agent AGENT_ID

# Register website source
knowrithm website register --payload SOURCE_CONFIG

# Trigger crawl job
knowrithm website crawl SOURCE_ID [--payload OPTIONS] [--wait/--no-wait]

# List discovered pages
knowrithm website pages SOURCE_ID

# Delete website source
knowrithm website delete SOURCE_ID [--wait/--no-wait]

# Widget handshake (unauthenticated)
knowrithm website handshake --payload HANDSHAKE_DATA
```

### System Utilities

```bash
# Health check
knowrithm system health

# Poll task status
knowrithm system task-status TASK_ID

# Trigger address seed data
knowrithm system address-seed

# List countries
knowrithm system countries

# Get country by ID
knowrithm system country COUNTRY_ID

# List states for country
knowrithm system states COUNTRY_ID

# Get state by ID
knowrithm system state STATE_ID

# List cities for state
knowrithm system cities STATE_ID

# Get city by ID
knowrithm system city CITY_ID
```

## Common Workflows

### Setting Up a New Agent

```bash
# 1. Create agent configuration file
cat > agent.json <<EOF
{
  "name": "Customer Support Bot",
  "description": "Handles customer inquiries",
  "status": "active",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
EOF

# 2. Create the agent
knowrithm agent create --payload @agent.json --wait

# 3. Upload knowledge base documents
knowrithm document upload \
  --agent-id <agent_id> \
  --file ./docs/faq.pdf \
  --file ./docs/product-guide.pdf

# 4. Test the agent
knowrithm agent test <agent_id> \
  --payload '{"query": "What is your refund policy?"}' \
  --wait

# 5. Get embed code for website
knowrithm agent embed-code <agent_id>
```

### Managing Conversations

```bash
# Create a conversation
knowrithm conversation create --payload '{
  "agent_id": "<agent_id>",
  "entity_type": "lead",
  "entity_id": "<lead_id>"
}'

# Send messages
knowrithm conversation chat <conversation_id> \
  --payload '{"message": "Hello, I need help"}' \
  --wait

# View conversation history
knowrithm conversation messages <conversation_id>

# Get conversation analytics
knowrithm analytics conversation <conversation_id>
```

### Database Integration Workflow

```bash
# 1. Create database connection
cat > db_config.json <<EOF
{
  "name": "Production Database",
  "type": "postgresql",
  "host": "db.example.com",
  "port": 5432,
  "database": "production",
  "username": "readonly_user",
  "password": "secure_password"
}
EOF

knowrithm database create --payload @db_config.json

# 2. Test the connection
knowrithm database test <connection_id>

# 3. Run semantic analysis
knowrithm database analyze <connection_id> --wait

# 4. View knowledge graph
knowrithm database knowledge-graph <connection_id>

# 5. Get sample queries
knowrithm database sample-queries <connection_id>

# 6. Generate SQL from natural language
knowrithm database text-to-sql <connection_id> \
  --payload '{"question": "Show top 10 customers by revenue"}'
```

### Bulk Document Upload

```bash
# Upload multiple files at once
knowrithm document upload \
  --agent-id <agent_id> \
  --file ./docs/file1.pdf \
  --file ./docs/file2.docx \
  --file ./docs/file3.txt

# Upload from URLs
knowrithm document upload \
  --agent-id <agent_id> \
  --url https://example.com/page1 \
  --url https://example.com/page2

# Mixed upload
knowrithm document upload \
  --agent-id <agent_id> \
  --file ./local-doc.pdf \
  --url https://example.com/remote-content
```

### Analytics Export

```bash
# Export conversation data
knowrithm analytics export --payload '{
  "type": "conversations",
  "format": "csv",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}'

# Export lead analytics
knowrithm analytics export --payload '{
  "type": "leads",
  "format": "json",
  "filters": {
    "status": "qualified"
  }
}'

# Export agent performance
knowrithm analytics export --payload '{
  "type": "agents",
  "format": "xlsx",
  "agent_ids": ["<agent_id_1>", "<agent_id_2>"]
}'
```

## Advanced Usage

### Working with JSON Payloads

**Inline JSON:**
```bash
knowrithm agent create --payload '{"name": "Test Agent", "status": "active"}'
```

**From file:**
```bash
knowrithm agent create --payload @agent.json
```

**From stdin:**
```bash
echo '{"name": "Dynamic Agent"}' | knowrithm agent create --payload @-
```

### Asynchronous Task Handling

Many operations return a `task_id` for async processing:

```bash
# Wait for completion (default for most operations)
knowrithm agent create --payload @agent.json --wait

# Return immediately without waiting
knowrithm agent create --payload @agent.json --no-wait

# Manually poll task status
knowrithm system task-status <task_id>
```

### Pagination

List commands support pagination:

```bash
# Default: page 1, 20 items
knowrithm agent list

# Custom pagination
knowrithm agent list --page 2 --per-page 50

# Get all items (loop through pages)
for i in {1..10}; do
  knowrithm agent list --page $i --per-page 100
done
```

### Filtering and Search

```bash
# Filter agents by status
knowrithm agent list --status active

# Search agents
knowrithm agent list --search "customer support"

# Multiple filters
knowrithm conversation entity \
  --entity-type lead \
  --status open \
  --page 1 \
  --per-page 20
```

### Piping and Integration

```bash
# Extract specific fields with jq
knowrithm agent list | jq '.data[] | {id, name, status}'

# Save output to file
knowrithm agent get <agent_id> > agent-backup.json

# Use in scripts
AGENT_ID=$(knowrithm agent create --payload @agent.json | jq -r '.data.id')
echo "Created agent: $AGENT_ID"
```

### Batch Operations

```bash
# Bulk delete documents
knowrithm document bulk-delete --payload '{
  "document_ids": [
    "doc_1", "doc_2", "doc_3"
  ]
}'

# Bulk restore companies
knowrithm company bulk-restore --payload '{
  "company_ids": [
    "company_1", "company_2"
  ]
}'
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to API
```bash
# Check configuration
knowrithm config show

# Verify base URL is correct
knowrithm config set-base-url https://correct-url.com

# Test connection
knowrithm system health
```

**Problem:** SSL certificate errors
```bash
# For development only - disable SSL verification
knowrithm config set-verify-ssl --disable

# For production - ensure proper certificates
knowrithm config set-verify-ssl --enable
```

### Authentication Issues

**Problem:** Token expired
```bash
# Refresh tokens
knowrithm auth refresh

# Or login again
knowrithm auth login
```

**Problem:** Invalid credentials
```bash
# Clear all credentials and start fresh
knowrithm auth clear --all

# Login with correct credentials
knowrithm auth login

# Validate
knowrithm auth validate
```

### Task Timeout

**Problem:** Async task takes too long
```bash
# Run without waiting
knowrithm agent create --payload @agent.json --no-wait

# Get task ID from response, then poll manually
knowrithm system task-status <task_id>
```

### Payload Errors

**Problem:** Invalid JSON payload
```bash
# Validate JSON file
cat payload.json | jq .

# Use proper quotes
knowrithm agent create --payload '{"key": "value"}'  # Correct
knowrithm agent create --payload "{\"key\": \"value\"}"  # Also correct
```

### Permission Errors

**Problem:** Insufficient permissions
```bash
# Check current user/company
knowrithm auth me
knowrithm company current

# Ensure correct authentication method
knowrithm agent list --auth jwt  # or --auth api-key
```

### Debugging

**Enable verbose output:**
```bash
# Add -v or --verbose flag (if implemented)
knowrithm -v agent list

# Use debug mode
export KNOWRITHM_DEBUG=1
knowrithm agent list
```

## Development

### Project Structure
```
knowrithm-cli/
├── knowrithm_cli/
│   ├── __init__.py
│   ├── client.py          # HTTP client wrapper
│   ├── config.py          # Configuration management
│   ├── utils.py           # Shared utilities
│   └── commands/
│       ├── __init__.py
│       ├── agent.py       # Agent commands
│       ├── analytics.py   # Analytics commands
│       ├── auth.py        # Authentication commands
│       ├── common.py      # Shared command helpers
│       ├── company.py     # Company commands
│       ├── config_cmd.py  # Config commands
│       ├── conversation.py # Conversation commands
│       ├── database.py    # Database commands
│       ├── document.py    # Document commands
│       ├── lead.py        # Lead commands
│       ├── settings.py    # LLM settings commands
│       ├── system.py      # System utilities
│       └── website.py     # Website commands
├── setup.py
├── README.md
└── requirements.txt
```

### Running Tests
```bash
# Syntax check
python -m compileall knowrithm_cli

# Run basic smoke tests
knowrithm --help
knowrithm system health
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review command help: `knowrithm COMMAND --help`
- Contact Knowrithm support: agentx@notifications.knowrithm.org
- API Documentation: https://docs.knowrithm.org

## License

Copyright © 2024 Knowrithm. All rights reserved.