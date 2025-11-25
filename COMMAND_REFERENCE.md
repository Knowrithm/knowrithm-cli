# Knowrithm CLI - Complete Command Reference

This document provides detailed reference information for all Knowrithm CLI commands, including examples, parameters, and response formats.

## Table of Contents

1. [Authentication Commands](#authentication-commands)
2. [Agent Management](#agent-management)
3. [Conversation Management](#conversation-management)
4. [Document Management](#document-management)
5. [Database Management](#database-management)
6. [Analytics Commands](#analytics-commands)
7. [Lead Management](#lead-management)
8. [Company Management](#company-management)
9. [LLM Settings Management](#llm-settings-management)
10. [Website Awareness](#website-awareness)
11. [System Utilities](#system-utilities)
12. [Configuration Commands](#configuration-commands)

---

## Authentication Commands

### `knowrithm auth login`

Authenticate using email and password, storing JWT tokens locally.

**Usage:**
```bash
knowrithm auth login [OPTIONS]
```

**Options:**
- `--email TEXT` - User email address (prompted if not provided)
- `--password TEXT` - Account password (prompted securely if not provided)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Examples:**
```bash
# Interactive login
knowrithm auth login

# Non-interactive login
knowrithm auth login --email admin@example.com --password mySecurePass123
```

**Response:**
```json
{
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_at": 1735689600
  },
  "user": {
    "id": "user_123",
    "email": "admin@example.com",
    "company_id": "company_456"
  }
}
```

---

### `knowrithm auth logout`

Revoke the current session and clear locally stored tokens.

**Usage:**
```bash
knowrithm auth logout
```

**Examples:**
```bash
knowrithm auth logout
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

### `knowrithm auth refresh`

Refresh the access token using the stored refresh token.

**Usage:**
```bash
knowrithm auth refresh
```

**Examples:**
```bash
knowrithm auth refresh
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_at": 1735693200
}
```

---

### `knowrithm auth register`

Register a new company admin account (public endpoint).

**Usage:**
```bash
knowrithm auth register --payload PAYLOAD
```

**Options:**
- `--payload TEXT` - JSON string or @filepath with registration data

**Payload Schema:**
```json
{
  "email": "admin@newcompany.com",
  "password": "SecurePassword123!",
  "company_name": "New Company LLC",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Examples:**
```bash
# From inline JSON
knowrithm auth register --payload '{
  "email": "admin@startup.com",
  "password": "StrongPass123!",
  "company_name": "Startup Inc",
  "first_name": "Jane",
  "last_name": "Smith"
}'

# From file
knowrithm auth register --payload @registration.json
```

---

### `knowrithm auth me`

Get details for the currently authenticated user.

**Usage:**
```bash
knowrithm auth me [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method (default: auto)

**Examples:**
```bash
knowrithm auth me
```

**Response:**
```json
{
  "id": "user_123",
  "email": "admin@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "company_id": "company_456",
  "company_name": "Example Corp"
}
```

---

### `knowrithm auth set-api-key`

Store API key and secret for future requests.

**Usage:**
```bash
knowrithm auth set-api-key [OPTIONS]
```

**Options:**
- `--key TEXT` - API key (prompted if not provided)
- `--secret TEXT` - API secret (prompted securely if not provided)

**Examples:**
```bash
# Interactive
knowrithm auth set-api-key

# Non-interactive
knowrithm auth set-api-key --key "ak_123456" --secret "sk_abcdef"
```

---

### `knowrithm auth clear`

Clear cached authentication credentials.

**Usage:**
```bash
knowrithm auth clear [OPTIONS]
```

**Options:**
- `--all` - Clear both JWT tokens and API key credentials
- `--tokens` - Clear only JWT tokens
- `--api-key` - Clear only API key credentials

**Examples:**
```bash
# Clear everything
knowrithm auth clear --all

# Clear only JWT tokens
knowrithm auth clear --tokens

# Clear only API key
knowrithm auth clear --api-key
```

---

### `knowrithm auth validate`

Validate current credentials with the backend.

**Usage:**
```bash
knowrithm auth validate [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm auth validate
```

**Response:**
```json
{
  "valid": true,
  "user_id": "user_123",
  "company_id": "company_456",
  "expires_at": 1735689600
}
```

---

## Agent Management

### `knowrithm agent list`

List agents for the authenticated company.

**Usage:**
```bash
knowrithm agent list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--company-id TEXT` - Filter by company ID (super admin only)
- `--status TEXT` - Filter by agent status (active, inactive, training)
- `--search TEXT` - Search string for name/description
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
# List all agents
knowrithm agent list

# Filter by status
knowrithm agent list --status active

# Search agents
knowrithm agent list --search "customer support"

# Pagination
knowrithm agent list --page 2 --per-page 50

# Super admin: list agents for specific company
knowrithm agent list --company-id company_789
```

**Response:**
```json
{
  "data": [
    {
      "id": "agent_123",
      "name": "Customer Support Bot",
      "description": "Handles customer inquiries",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:22:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

### `knowrithm agent get`

Retrieve a specific agent by ID.

**Usage:**
```bash
knowrithm agent get AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm agent get agent_123
```

**Response:**
```json
{
  "id": "agent_123",
  "name": "Customer Support Bot",
  "description": "Handles customer inquiries and basic troubleshooting",
  "status": "active",
  "company_id": "company_456",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": "You are a helpful customer support assistant..."
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:22:00Z",
  "statistics": {
    "total_conversations": 1250,
    "active_conversations": 42,
    "avg_response_time_ms": 850
  }
}
```

---

### `knowrithm agent create`

Create a new agent.

**Usage:**
```bash
knowrithm agent create [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON string or @filepath (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Payload Schema:**
```json
{
  "name": "Agent Name",
  "description": "Agent description",
  "status": "active",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": "Custom instructions...",
    "model": "gpt-4"
  },
  "capabilities": ["chat", "search", "database_query"]
}
```

**Examples:**
```bash
# From inline JSON
knowrithm agent create --payload '{
  "name": "Sales Assistant",
  "description": "Helps with sales inquiries",
  "status": "active"
}'

# From file
knowrithm agent create --payload @agent-config.json --wait

# Without waiting
knowrithm agent create --payload @agent-config.json --no-wait
```

---

### `knowrithm agent clone`

Clone an existing agent with optional overrides.

**Usage:**
```bash
knowrithm agent clone AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent to clone

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON overrides for the cloned agent
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Examples:**
```bash
# Simple clone
knowrithm agent clone agent_123

# Clone with name override
knowrithm agent clone agent_123 --payload '{"name": "Sales Bot - Copy"}'

# Clone with multiple overrides
knowrithm agent clone agent_123 --payload '{
  "name": "Modified Clone",
  "description": "Cloned and customized",
  "settings": {
    "temperature": 0.5
  }
}'
```

---

### `knowrithm agent update`

Update an existing agent.

**Usage:**
```bash
knowrithm agent update AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent to update

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON string or @filepath with update fields (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Examples:**
```bash
# Update status
knowrithm agent update agent_123 --payload '{"status": "inactive"}'

# Update settings
knowrithm agent update agent_123 --payload '{
  "settings": {
    "temperature": 0.9,
    "max_tokens": 1000
  }
}'

# Update from file
knowrithm agent update agent_123 --payload @updates.json
```

---

### `knowrithm agent delete`

Soft delete an agent (can be restored later).

**Usage:**
```bash
knowrithm agent delete AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent to delete

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
knowrithm agent delete agent_123
knowrithm agent delete agent_123 --wait
```

---

### `knowrithm agent restore`

Restore a soft-deleted agent.

**Usage:**
```bash
knowrithm agent restore AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent to restore

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
knowrithm agent restore agent_123
```

---

### `knowrithm agent stats`

Retrieve statistics for an agent.

**Usage:**
```bash
knowrithm agent stats AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm agent stats agent_123
```

**Response:**
```json
{
  "agent_id": "agent_123",
  "total_conversations": 1250,
  "active_conversations": 42,
  "total_messages": 8500,
  "avg_response_time_ms": 850,
  "satisfaction_score": 4.6,
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-11-02T00:00:00Z"
  }
}
```

---

### `knowrithm agent test`

Run a test query against an agent.

**Usage:**
```bash
knowrithm agent test AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent to test

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON test payload
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Test Payload Schema:**
```json
{
  "query": "What is your refund policy?",
  "context": {
    "user_id": "test_user",
    "metadata": {}
  }
}
```

**Examples:**
```bash
# Simple test
knowrithm agent test agent_123 --payload '{"query": "Hello"}'

# Test with context
knowrithm agent test agent_123 --payload '{
  "query": "What is my order status?",
  "context": {
    "user_id": "user_456",
    "metadata": {"order_id": "ORD-12345"}
  }
}'
```

**Response:**
```json
{
  "query": "What is your refund policy?",
  "response": "Our refund policy allows returns within 30 days...",
  "confidence": 0.95,
  "sources": [
    {
      "document_id": "doc_789",
      "chunk_id": "chunk_123",
      "relevance": 0.92
    }
  ],
  "response_time_ms": 782
}
```

---

### `knowrithm agent embed-code`

Fetch widget embed code for an agent.

**Usage:**
```bash
knowrithm agent embed-code AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm agent embed-code agent_123
```

**Response:**
```json
{
  "agent_id": "agent_123",
  "embed_code": "<script src=\"https://cdn.knowrithm.org/widget.js\" data-agent-id=\"agent_123\"></script>",
  "configuration": {
    "position": "bottom-right",
    "theme": "light",
    "language": "en"
  }
}
```

---

## Conversation Management

### `knowrithm conversation list`

List conversations for the company.

**Usage:**
```bash
knowrithm conversation list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
knowrithm conversation list
knowrithm conversation list --page 2 --per-page 50
```

---

### `knowrithm conversation entity`

List conversations scoped to an entity (lead or user).

**Usage:**
```bash
knowrithm conversation entity [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--entity-id TEXT` - Specific entity ID to inspect
- `--entity-type TEXT` - Filter by entity type (lead/user)
- `--status TEXT` - Conversation status filter (open/closed/archived)
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
# List all conversations for current entity
knowrithm conversation entity

# Filter by entity type
knowrithm conversation entity --entity-type lead

# Specific entity with status filter
knowrithm conversation entity \
  --entity-id lead_456 \
  --entity-type lead \
  --status open

# Pagination
knowrithm conversation entity --page 1 --per-page 30
```

---

### `knowrithm conversation agent`

List conversations for a specific agent.

**Usage:**
```bash
knowrithm conversation agent AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--status TEXT` - Filter by conversation status
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
knowrithm conversation agent agent_123
knowrithm conversation agent agent_123 --status open
knowrithm conversation agent agent_123 --page 2
```

---

### `knowrithm conversation create`

Create a new conversation.

**Usage:**
```bash
knowrithm conversation create [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON string or @filepath (required)
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Payload Schema:**
```json
{
  "agent_id": "agent_123",
  "entity_type": "lead",
  "entity_id": "lead_456",
  "metadata": {
    "source": "website",
    "campaign": "summer_2024"
  }
}
```

**Examples:**
```bash
knowrithm conversation create --payload '{
  "agent_id": "agent_123",
  "entity_type": "lead",
  "entity_id": "lead_456"
}'
```

---

### `knowrithm conversation messages`

Retrieve messages for a conversation.

**Usage:**
```bash
knowrithm conversation messages CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 50)

**Examples:**
```bash
knowrithm conversation messages conv_789
knowrithm conversation messages conv_789 --page 1 --per-page 100
```

**Response:**
```json
{
  "conversation_id": "conv_789",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Hello, I need help",
      "timestamp": "2024-11-02T10:15:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Hello! I'm here to help. What can I assist you with?",
      "timestamp": "2024-11-02T10:15:02Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 12
  }
}
```

---

### `knowrithm conversation chat`

Send a chat message into a conversation.

**Usage:**
```bash
knowrithm conversation chat CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON string or @filepath with message (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Payload Schema:**
```json
{
  "message": "What is your refund policy?",
  "metadata": {
    "source": "mobile_app"
  }
}
```

**Examples:**
```bash
knowrithm conversation chat conv_789 \
  --payload '{"message": "Hello, I need help with my order"}'

knowrithm conversation chat conv_789 \
  --payload @message.json \
  --wait
```

---

### `knowrithm conversation delete`

Soft delete a conversation.

**Usage:**
```bash
knowrithm conversation delete CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm conversation delete conv_789
```

---

### `knowrithm conversation restore`

Restore a soft-deleted conversation.

**Usage:**
```bash
knowrithm conversation restore CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm conversation restore conv_789
```

---

### `knowrithm conversation delete-messages`

Delete all messages for a conversation.

**Usage:**
```bash
knowrithm conversation delete-messages CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm conversation delete-messages conv_789
```

---

### `knowrithm conversation restore-messages`

Restore all messages for a conversation.

**Usage:**
```bash
knowrithm conversation restore-messages CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm conversation restore-messages conv_789
```

---

### `knowrithm conversation deleted`

List soft-deleted conversations.

**Usage:**
```bash
knowrithm conversation deleted [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm conversation deleted
```

---

## Document Management

### `knowrithm document list`

List documents for the current company.

**Usage:**
```bash
knowrithm document list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
knowrithm document list
knowrithm document list --page 2 --per-page 50
```

---

### `knowrithm document agent`

List documents linked to a specific agent.

**Usage:**
```bash
knowrithm document agent AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
knowrithm document agent agent_123
knowrithm document agent agent_123 --page 1 --per-page 100
```

---

### `knowrithm document upload`

Upload documents or initiate scraping tasks.

**Usage:**
```bash
knowrithm document upload [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--agent-id TEXT` - Agent identifier to associate (required)
- `--file PATH` - Path to file (can be used multiple times)
- `--url TEXT` - URL to ingest (can be used multiple times)
- `--payload TEXT` - Additional JSON fields for the upload request

**Examples:**
```bash
# Upload single file
knowrithm document upload \
  --agent-id agent_123 \
  --file ./docs/faq.pdf

# Upload multiple files
knowrithm document upload \
  --agent-id agent_123 \
  --file ./docs/faq.pdf \
  --file ./docs/manual.docx \
  --file ./docs/guide.txt

# Scrape URLs
knowrithm document upload \
  --agent-id agent_123 \
  --url https://example.com/page1 \
  --url https://example.com/page2

# Mixed upload
knowrithm document upload \
  --agent-id agent_123 \
  --file ./local-doc.pdf \
  --url https://example.com/remote-content

# With additional metadata
knowrithm document upload \
  --agent-id agent_123 \
  --file ./doc.pdf \
  --payload '{"category": "product_docs", "priority": "high"}'
```

---

### `knowrithm document delete`

Soft delete a document.

**Usage:**
```bash
knowrithm document delete DOCUMENT_ID [OPTIONS]
```

**Arguments:**
- `DOCUMENT_ID` - The document identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document delete doc_456
```

---

### `knowrithm document restore`

Restore a soft-deleted document.

**Usage:**
```bash
knowrithm document restore DOCUMENT_ID [OPTIONS]
```

**Arguments:**
- `DOCUMENT_ID` - The document identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document restore doc_456
```

---

### `knowrithm document delete-chunks`

Delete all chunks for a document.

**Usage:**
```bash
knowrithm document delete-chunks DOCUMENT_ID [OPTIONS]
```

**Arguments:**
- `DOCUMENT_ID` - The document identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document delete-chunks doc_456
```

---

### `knowrithm document restore-chunks`

Restore all chunks for a document.

**Usage:**
```bash
knowrithm document restore-chunks DOCUMENT_ID [OPTIONS]
```

**Arguments:**
- `DOCUMENT_ID` - The document identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document restore-chunks doc_456
```

---

### `knowrithm document delete-chunk`

Delete a single document chunk.

**Usage:**
```bash
knowrithm document delete-chunk CHUNK_ID [OPTIONS]
```

**Arguments:**
- `CHUNK_ID` - The chunk identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document delete-chunk chunk_789
```

---

### `knowrithm document restore-chunk`

Restore a single document chunk.

**Usage:**
```bash
knowrithm document restore-chunk CHUNK_ID [OPTIONS]
```

**Arguments:**
- `CHUNK_ID` - The chunk identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document restore-chunk chunk_789
```

---

### `knowrithm document deleted`

List deleted documents.

**Usage:**
```bash
knowrithm document deleted [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document deleted
```

---

### `knowrithm document deleted-chunks`

List deleted document chunks.

**Usage:**
```bash
knowrithm document deleted-chunks [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm document deleted-chunks
```

---

### `knowrithm document bulk-delete`

Bulk delete documents.

**Usage:**
```bash
knowrithm document bulk-delete [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON string or @filepath with document_ids (required)

**Payload Schema:**
```json
{
  "document_ids": [
    "doc_001",
    "doc_002",
    "doc_003"
  ]
}
```

**Examples:**
```bash
knowrithm document bulk-delete --payload '{
  "document_ids": ["doc_001", "doc_002", "doc_003"]
}'
```

---

### `knowrithm document search`

Run semantic document search.

**Usage:**
```bash
knowrithm document search [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON search payload (required)

**Payload Schema:**
```json
{
  "query": "refund policy",
  "agent_id": "agent_123",
  "top_k": 5,
  "filters": {
    "document_type": "policy"
  }
}
```

**Examples:**
```bash
knowrithm document search --payload '{
  "query": "What is the return policy?",
  "agent_id": "agent_123",
  "top_k": 10
}'
```

**Response:**
```json
{
  "query": "What is the return policy?",
  "results": [
    {
      "document_id": "doc_456",
      "chunk_id": "chunk_789",
      "content": "Our return policy allows returns within 30 days...",
      "score": 0.95,
      "metadata": {
        "document_name": "refund_policy.pdf",
        "page": 2
      }
    }
  ],
  "total_results": 5
}
```

---

## Database Management

### `knowrithm database list`

List database connections owned by the user.

**Usage:**
```bash
knowrithm database list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database list
```

**Response:**
```json
{
  "connections": [
    {
      "id": "conn_123",
      "name": "Production Database",
      "type": "postgresql",
      "host": "db.example.com",
      "database": "prod_db",
      "status": "active",
      "last_analyzed": "2024-11-01T10:00:00Z"
    }
  ]
}
```

---

### `knowrithm database deleted`

List deleted database connections.

**Usage:**
```bash
knowrithm database deleted [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database deleted
```

---

### `knowrithm database create`

Create a new database connection.

**Usage:**
```bash
knowrithm database create [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload describing the connection (required)

**Payload Schema:**
```json
{
  "name": "Production Database",
  "type": "postgresql",
  "host": "db.example.com",
  "port": 5432,
  "database": "production",
  "username": "readonly_user",
  "password": "secure_password",
  "ssl_enabled": true,
  "options": {
    "pool_size": 5,
    "timeout": 30
  }
}
```

**Supported Database Types:**
- `postgresql`
- `mysql`
- `mssql`
- `oracle`
- `mongodb`
- `snowflake`

**Examples:**
```bash
# PostgreSQL connection
knowrithm database create --payload '{
  "name": "Main DB",
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass"
}'

# From file
knowrithm database create --payload @db-config.json
```

---

### `knowrithm database get`

Get details for a database connection.

**Usage:**
```bash
knowrithm database get CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database get conn_123
```

---

### `knowrithm database delete`

Soft delete a database connection.

**Usage:**
```bash
knowrithm database delete CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database delete conn_123
```

---

### `knowrithm database restore`

Restore a deleted database connection.

**Usage:**
```bash
knowrithm database restore CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database restore conn_123
```

---

### `knowrithm database test`

Test a database connection.

**Usage:**
```bash
knowrithm database test CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database test conn_123
```

**Response:**
```json
{
  "connection_id": "conn_123",
  "status": "success",
  "latency_ms": 45,
  "database_version": "PostgreSQL 14.5",
  "accessible_tables": 127
}
```

---

### `knowrithm database analyze`

Queue semantic analysis for a database connection.

**Usage:**
```bash
knowrithm database analyze CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
# Start analysis and return immediately
knowrithm database analyze conn_123

# Wait for analysis to complete
knowrithm database analyze conn_123 --wait
```

---

### `knowrithm database analyze-all`

Analyze all active database connections.

**Usage:**
```bash
knowrithm database analyze-all [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON payload with filters
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
knowrithm database analyze-all
knowrithm database analyze-all --wait
```

---

### `knowrithm database tables`

List table metadata for a database connection.

**Usage:**
```bash
knowrithm database tables CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 50)

**Examples:**
```bash
knowrithm database tables conn_123
knowrithm database tables conn_123 --page 2 --per-page 100
```

**Response:**
```json
{
  "connection_id": "conn_123",
  "tables": [
    {
      "id": "table_456",
      "name": "customers",
      "schema": "public",
      "row_count": 15420,
      "columns": [
        {
          "name": "id",
          "type": "integer",
          "nullable": false,
          "primary_key": true
        },
        {
          "name": "email",
          "type": "varchar",
          "nullable": false
        }
      ],
      "description": "Customer information and contact details"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 127
  }
}
```

---

### `knowrithm database table`

Retrieve metadata for a single table.

**Usage:**
```bash
knowrithm database table TABLE_ID [OPTIONS]
```

**Arguments:**
- `TABLE_ID` - The table identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database table table_456
```

---

### `knowrithm database table-delete`

Delete table metadata.

**Usage:**
```bash
knowrithm database table-delete TABLE_ID [OPTIONS]
```

**Arguments:**
- `TABLE_ID` - The table identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database table-delete table_456
```

---

### `knowrithm database table-restore`

Restore a deleted table metadata record.

**Usage:**
```bash
knowrithm database table-restore TABLE_ID [OPTIONS]
```

**Arguments:**
- `TABLE_ID` - The table identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database table-restore table_456
```

---

### `knowrithm database semantic-snapshot`

Retrieve the semantic snapshot for a database connection.

**Usage:**
```bash
knowrithm database semantic-snapshot CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database semantic-snapshot conn_123
```

**Response:**
```json
{
  "connection_id": "conn_123",
  "snapshot": {
    "entities": [
      {
        "name": "Customer",
        "description": "Individual or organization that purchases products",
        "attributes": ["id", "name", "email", "created_at"]
      }
    ],
    "relationships": [
      {
        "from": "Order",
        "to": "Customer",
        "type": "belongs_to",
        "cardinality": "many_to_one"
      }
    ]
  },
  "generated_at": "2024-11-01T10:00:00Z"
}
```

---

### `knowrithm database knowledge-graph`

Retrieve the knowledge graph for a database connection.

**Usage:**
```bash
knowrithm database knowledge-graph CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database knowledge-graph conn_123
```

---

### `knowrithm database sample-queries`

Retrieve generated sample queries for a database connection.

**Usage:**
```bash
knowrithm database sample-queries CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm database sample-queries conn_123
```

**Response:**
```json
{
  "connection_id": "conn_123",
  "queries": [
    {
      "description": "Get top 10 customers by total purchases",
      "sql": "SELECT customer_id, SUM(amount) as total FROM orders GROUP BY customer_id ORDER BY total DESC LIMIT 10",
      "category": "analytics"
    },
    {
      "description": "Find customers who haven't ordered in 90 days",
      "sql": "SELECT * FROM customers WHERE id NOT IN (SELECT DISTINCT customer_id FROM orders WHERE created_at > NOW() - INTERVAL '90 days')",
      "category": "retention"
    }
  ]
}
```

---

### `knowrithm database text-to-sql`

Generate SQL from natural language.

**Usage:**
```bash
knowrithm database text-to-sql CONNECTION_ID [OPTIONS]
```

**Arguments:**
- `CONNECTION_ID` - The connection identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with natural language question (required)

**Payload Schema:**
```json
{
  "question": "Show me the top 10 customers by revenue",
  "execute": false
}
```

**Examples:**
```bash
knowrithm database text-to-sql conn_123 --payload '{
  "question": "What are the total sales for each product category?"
}'

knowrithm database text-to-sql conn_123 --payload '{
  "question": "Find all orders placed in the last 7 days",
  "execute": true
}'
```

**Response:**
```json
{
  "question": "What are the total sales for each product category?",
  "sql": "SELECT category, SUM(price * quantity) as total_sales FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY category ORDER BY total_sales DESC",
  "explanation": "This query joins products with order items to calculate total sales by category",
  "confidence": 0.92,
  "results": [
    {
      "category": "Electronics",
      "total_sales": 125430.50
    }
  ]
}
```

---

### `knowrithm database export`

Export database content to documents.

**Usage:**
```bash
knowrithm database export [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with connection_id and options (required)

**Payload Schema:**
```json
{
  "connection_id": "conn_123",
  "format": "csv",
  "tables": ["customers", "orders"],
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31"
  }
}
```

**Examples:**
```bash
knowrithm database export --payload '{
  "connection_id": "conn_123",
  "format": "json",
  "tables": ["products", "categories"]
}'
```

---

## Analytics Commands

### `knowrithm analytics dashboard`

Retrieve the main analytics dashboard.

**Usage:**
```bash
knowrithm analytics dashboard [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--company-id TEXT` - Optional company ID (super admin only)

**Examples:**
```bash
# Current company dashboard
knowrithm analytics dashboard

# Super admin: specific company
knowrithm analytics dashboard --company-id company_789
```

**Response:**
```json
{
  "company_id": "company_456",
  "period": {
    "start": "2024-10-01T00:00:00Z",
    "end": "2024-11-02T00:00:00Z"
  },
  "metrics": {
    "total_conversations": 5420,
    "active_agents": 12,
    "total_leads": 892,
    "avg_response_time_ms": 750,
    "satisfaction_score": 4.5
  },
  "trends": {
    "conversations_growth": 15.3,
    "leads_growth": 22.7
  }
}
```

---

### `knowrithm analytics agent`

Retrieve analytics for a single agent.

**Usage:**
```bash
knowrithm analytics agent AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--start-date TEXT` - ISO start date (e.g., 2024-01-01)
- `--end-date TEXT` - ISO end date (e.g., 2024-12-31)

**Examples:**
```bash
knowrithm analytics agent agent_123

knowrithm analytics agent agent_123 \
  --start-date 2024-10-01 \
  --end-date 2024-10-31
```

**Response:**
```json
{
  "agent_id": "agent_123",
  "period": {
    "start": "2024-10-01T00:00:00Z",
    "end": "2024-10-31T00:00:00Z"
  },
  "metrics": {
    "total_conversations": 342,
    "total_messages": 2847,
    "avg_response_time_ms": 820,
    "satisfaction_score": 4.6,
    "resolution_rate": 0.87
  },
  "daily_stats": [
    {
      "date": "2024-10-01",
      "conversations": 12,
      "messages": 98
    }
  ]
}
```

---

### `knowrithm analytics agent-performance`

Compare agent performance to company averages.

**Usage:**
```bash
knowrithm analytics agent-performance AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--start-date TEXT` - ISO start date
- `--end-date TEXT` - ISO end date

**Examples:**
```bash
knowrithm analytics agent-performance agent_123
knowrithm analytics agent-performance agent_123 --start-date 2024-10-01
```

**Response:**
```json
{
  "agent_id": "agent_123",
  "agent_metrics": {
    "avg_response_time_ms": 820,
    "satisfaction_score": 4.6,
    "resolution_rate": 0.87
  },
  "company_averages": {
    "avg_response_time_ms": 950,
    "satisfaction_score": 4.3,
    "resolution_rate": 0.82
  },
  "comparison": {
    "response_time_delta": -13.7,
    "satisfaction_delta": 7.0,
    "resolution_delta": 6.1
  }
}
```

---

### `knowrithm analytics conversation`

Retrieve analytics for a specific conversation.

**Usage:**
```bash
knowrithm analytics conversation CONVERSATION_ID [OPTIONS]
```

**Arguments:**
- `CONVERSATION_ID` - The conversation identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm analytics conversation conv_789
```

**Response:**
```json
{
  "conversation_id": "conv_789",
  "duration_seconds": 420,
  "message_count": 14,
  "avg_response_time_ms": 780,
  "sentiment_analysis": {
    "overall": "positive",
    "score": 0.78
  },
  "resolution_status": "resolved",
  "satisfaction_score": 5
}
```

---

### `knowrithm analytics leads`

Retrieve lead analytics.

**Usage:**
```bash
knowrithm analytics leads [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--start-date TEXT` - ISO start date
- `--end-date TEXT` - ISO end date
- `--company-id TEXT` - Super admin override company ID

**Examples:**
```bash
knowrithm analytics leads

knowrithm analytics leads \
  --start-date 2024-01-01 \
  --end-date 2024-12-31

# Super admin
knowrithm analytics leads --company-id company_789
```

**Response:**
```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T00:00:00Z"
  },
  "total_leads": 2847,
  "by_status": {
    "new": 420,
    "qualified": 892,
    "converted": 567,
    "lost": 968
  },
  "conversion_rate": 0.199,
  "avg_time_to_conversion_days": 12.5,
  "by_source": {
    "website": 1245,
    "referral": 678,
    "direct": 924
  }
}
```

---

### `knowrithm analytics usage`

Retrieve platform usage analytics.

**Usage:**
```bash
knowrithm analytics usage [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--start-date TEXT` - ISO start date
- `--end-date TEXT` - ISO end date

**Examples:**
```bash
knowrithm analytics usage
knowrithm analytics usage --start-date 2024-10-01 --end-date 2024-10-31
```

**Response:**
```json
{
  "period": {
    "start": "2024-10-01T00:00:00Z",
    "end": "2024-10-31T00:00:00Z"
  },
  "api_calls": {
    "total": 45680,
    "by_endpoint": {
      "/api/v1/agent": 12450,
      "/api/v1/conversation": 18920
    }
  },
  "tokens_used": {
    "total": 2847500,
    "by_model": {
      "gpt-4": 1245000,
      "gpt-3.5-turbo": 1602500
    }
  },
  "storage": {
    "documents_mb": 4567,
    "embeddings_mb": 892
  }
}
```

---

### `knowrithm analytics export`

Export analytics data in various formats.

**Usage:**
```bash
knowrithm analytics export [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload describing the export request (required)

**Payload Schema:**
```json
{
  "type": "conversations|leads|agents|usage",
  "format": "csv|json|xlsx",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "filters": {
    "agent_ids": ["agent_123"],
    "status": "active"
  }
}
```

**Examples:**
```bash
# Export conversations as CSV
knowrithm analytics export --payload '{
  "type": "conversations",
  "format": "csv",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}'

# Export leads as JSON
knowrithm analytics export --payload '{
  "type": "leads",
  "format": "json",
  "filters": {
    "status": "qualified"
  }
}'

# Export agent analytics as Excel
knowrithm analytics export --payload '{
  "type": "agents",
  "format": "xlsx",
  "filters": {
    "agent_ids": ["agent_123", "agent_456"]
  }
}'
```

---

## Lead Management

### `knowrithm lead register`

Public lead registration (no authentication required).

**Usage:**
```bash
knowrithm lead register [OPTIONS]
```

**Options:**
- `--payload TEXT` - JSON payload for lead registration (required)

**Payload Schema:**
```json
{
  "email": "lead@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "company": "ACME Corp",
  "source": "website",
  "metadata": {
    "campaign": "summer_2024",
    "utm_source": "google"
  }
}
```

**Examples:**
```bash
knowrithm lead register --payload '{
  "email": "prospect@company.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "source": "landing_page"
}'
```

---

### `knowrithm lead create`

Create a lead within the authenticated company.

**Usage:**
```bash
knowrithm lead create [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload describing the lead (required)

**Examples:**
```bash
knowrithm lead create --payload '{
  "email": "newlead@example.com",
  "first_name": "Bob",
  "last_name": "Johnson",
  "status": "new",
  "score": 75
}'
```

---

### `knowrithm lead list`

List company leads.

**Usage:**
```bash
knowrithm lead list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--status TEXT` - Filter by lead status (new, qualified, converted, lost)
- `--search TEXT` - Search by name/email
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
# List all leads
knowrithm lead list

# Filter by status
knowrithm lead list --status qualified

# Search leads
knowrithm lead list --search "john"

# Pagination with filters
knowrithm lead list --status new --page 2 --per-page 50
```

---

### `knowrithm lead get`

Retrieve a specific lead.

**Usage:**
```bash
knowrithm lead get LEAD_ID [OPTIONS]
```

**Arguments:**
- `LEAD_ID` - The lead identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm lead get lead_456
```

**Response:**
```json
{
  "id": "lead_456",
  "email": "lead@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "company": "ACME Corp",
  "status": "qualified",
  "score": 85,
  "source": "website",
  "created_at": "2024-10-15T09:30:00Z",
  "last_contacted": "2024-10-28T14:20:00Z",
  "metadata": {
    "campaign": "summer_2024"
  }
}
```

---

### `knowrithm lead update`

Update a lead.

**Usage:**
```bash
knowrithm lead update LEAD_ID [OPTIONS]
```

**Arguments:**
- `LEAD_ID` - The lead identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with fields to update (required)

**Examples:**
```bash
# Update status
knowrithm lead update lead_456 --payload '{
  "status": "converted"
}'

# Update multiple fields
knowrithm lead update lead_456 --payload '{
  "status": "qualified",
  "score": 90,
  "notes": "Very interested in premium plan"
}'
```

---

### `knowrithm lead delete`

Delete (soft delete) a lead.

**Usage:**
```bash
knowrithm lead delete LEAD_ID [OPTIONS]
```

**Arguments:**
- `LEAD_ID` - The lead identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm lead delete lead_456
```

---

## Company Management

### `knowrithm company list`

List companies (super admin only).

**Usage:**
```bash
knowrithm company list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--page INTEGER` - Page number (default: 1)
- `--per-page INTEGER` - Items per page (default: 20)

**Examples:**
```bash
knowrithm company list
knowrithm company list --page 2 --per-page 50
```

---

### `knowrithm company current`

Retrieve the authenticated company.

**Usage:**
```bash
knowrithm company current [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company current
```

---

### `knowrithm company get`

Retrieve a specific company by ID.

**Usage:**
```bash
knowrithm company get COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company get company_789
```

---

### `knowrithm company create`

Create a company (public onboarding).

**Usage:**
```bash
knowrithm company create [OPTIONS]
```

**Options:**
- `--payload TEXT` - JSON payload describing the company (required)

**Payload Schema:**
```json
{
  "name": "New Company LLC",
  "email": "admin@newcompany.com",
  "industry": "technology",
  "size": "50-200",
  "admin_user": {
    "email": "admin@newcompany.com",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

**Examples:**
```bash
knowrithm company create --payload @company.json
```

---

### `knowrithm company update`

Update company metadata.

**Usage:**
```bash
knowrithm company update COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with updates (required)

**Examples:**
```bash
knowrithm company update company_789 --payload '{
  "name": "Updated Company Name",
  "industry": "healthcare"
}'
```

---

### `knowrithm company patch`

Partially update a company.

**Usage:**
```bash
knowrithm company patch COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with partial update fields (required)

**Examples:**
```bash
knowrithm company patch company_789 --payload '{
  "status": "active"
}'
```

---

### `knowrithm company delete`

Soft delete a company.

**Usage:**
```bash
knowrithm company delete COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company delete company_789
```

---

### `knowrithm company restore`

Restore a soft-deleted company.

**Usage:**
```bash
knowrithm company restore COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company restore company_789
```

---

### `knowrithm company deleted`

List deleted companies.

**Usage:**
```bash
knowrithm company deleted [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company deleted
```

---

### `knowrithm company bulk-delete`

Bulk delete companies.

**Usage:**
```bash
knowrithm company bulk-delete [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with company_ids (required)

**Examples:**
```bash
knowrithm company bulk-delete --payload '{
  "company_ids": ["company_001", "company_002", "company_003"]
}'
```

---

### `knowrithm company bulk-restore`

Bulk restore companies.

**Usage:**
```bash
knowrithm company bulk-restore [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with company_ids (required)

**Examples:**
```bash
knowrithm company bulk-restore --payload '{
  "company_ids": ["company_001", "company_002"]
}'
```

---

### `knowrithm company statistics`

Retrieve lead statistics for a company.

**Usage:**
```bash
knowrithm company statistics [COMPANY_ID] [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - Optional company identifier (uses current if not provided)

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--days INTEGER` - Number of days to include in statistics

**Examples:**
```bash
# Current company statistics
knowrithm company statistics

# Last 30 days
knowrithm company statistics --days 30

# Specific company (super admin)
knowrithm company statistics company_789 --days 90
```

**Response:**
```json
{
  "company_id": "company_456",
  "period_days": 30,
  "statistics": {
    "total_leads": 284,
    "new_leads": 67,
    "qualified_leads": 89,
    "converted_leads": 42,
    "conversion_rate": 0.148,
    "avg_response_time_hours": 2.3
  }
}
```

---

### `knowrithm company related-data`

Inspect related data counts before deletion.

**Usage:**
```bash
knowrithm company related-data COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm company related-data company_789
```

**Response:**
```json
{
  "company_id": "company_789",
  "related_data": {
    "agents": 12,
    "users": 8,
    "leads": 342,
    "conversations": 1847,
    "documents": 156,
    "database_connections": 3
  },
  "warning": "Deleting this company will affect all related resources"
}
```

---

### `knowrithm company cascade-delete`

Trigger cascade deletion for a company (super admin).

**Usage:**
```bash
knowrithm company cascade-delete COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON payload with cascade options

**Payload Schema:**
```json
{
  "confirm": true,
  "delete_users": true,
  "delete_data": true,
  "backup": false
}
```

**Examples:**
```bash
# Simple cascade delete
knowrithm company cascade-delete company_789

# With confirmation and options
knowrithm company cascade-delete company_789 --payload '{
  "confirm": true,
  "delete_users": true,
  "delete_data": true,
  "backup": true
}'
```

---

## LLM Settings Management

### `knowrithm settings create`

Create LLM settings using provider/model IDs.

**Usage:**
```bash
knowrithm settings create [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload for settings creation (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Payload Schema:**
```json
{
  "name": "GPT-4 Settings",
  "provider_id": "provider_openai",
  "model_id": "model_gpt4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "api_key": "sk-...",
  "scope": "company",
  "agent_id": null
}
```

**Examples:**
```bash
knowrithm settings create --payload '{
  "name": "Production GPT-4",
  "provider_id": "provider_openai",
  "model_id": "model_gpt4",
  "temperature": 0.7,
  "api_key": "sk-..."
}'

knowrithm settings create --payload @settings.json --wait
```

---

### `knowrithm settings create-sdk`

Create settings using provider/model names (SDK endpoint).

**Usage:**
```bash
knowrithm settings create-sdk [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload using provider/model names (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Payload Schema:**
```json
{
  "name": "Custom Settings",
  "provider_name": "openai",
  "model_name": "gpt-4",
  "temperature": 0.8,
  "max_tokens": 500,
  "api_key": "sk-..."
}
```

**Examples:**
```bash
knowrithm settings create-sdk --payload '{
  "name": "Agent Settings",
  "provider_name": "anthropic",
  "model_name": "claude-3-opus",
  "temperature": 0.7,
  "api_key": "sk-ant-..."
}'
```

---

### `knowrithm settings list-company`

List settings for a company.

**Usage:**
```bash
knowrithm settings list-company COMPANY_ID [OPTIONS]
```

**Arguments:**
- `COMPANY_ID` - The company identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm settings list-company company_456
```

---

### `knowrithm settings list-agent`

List settings for a given agent.

**Usage:**
```bash
knowrithm settings list-agent AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm settings list-agent agent_123
```

---

### `knowrithm settings get`

Retrieve a settings record.

**Usage:**
```bash
knowrithm settings get SETTINGS_ID [OPTIONS]
```

**Arguments:**
- `SETTINGS_ID` - The settings identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm settings get settings_789
```

**Response:**
```json
{
  "id": "settings_789",
  "name": "Production GPT-4",
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "scope": "company",
  "created_at": "2024-10-15T10:00:00Z"
}
```

---

### `knowrithm settings update`

Update an LLM settings record.

**Usage:**
```bash
knowrithm settings update SETTINGS_ID [OPTIONS]
```

**Arguments:**
- `SETTINGS_ID` - The settings identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload with updated fields (required)
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Examples:**
```bash
knowrithm settings update settings_789 --payload '{
  "temperature": 0.9,
  "max_tokens": 1500
}'
```

---

### `knowrithm settings delete`

Delete an LLM settings record.

**Usage:**
```bash
knowrithm settings delete SETTINGS_ID [OPTIONS]
```

**Arguments:**
- `SETTINGS_ID` - The settings identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
knowrithm settings delete settings_789
```

---

### `knowrithm settings test`

Validate settings by executing a test call.

**Usage:**
```bash
knowrithm settings test SETTINGS_ID [OPTIONS]
```

**Arguments:**
- `SETTINGS_ID` - The settings identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON payload with overrides
- `--wait/--no-wait` - Wait for async task completion (default: True)

**Examples:**
```bash
# Simple test
knowrithm settings test settings_789

# Test with overrides
knowrithm settings test settings_789 --payload '{
  "temperature": 0.5,
  "test_prompt": "Say hello"
}'
```

**Response:**
```json
{
  "settings_id": "settings_789",
  "test_result": "success",
  "response": "Hello! How can I assist you today?",
  "latency_ms": 1234,
  "tokens_used": 42
}
```

---

## Website Awareness

### `knowrithm website list`

List website sources.

**Usage:**
```bash
knowrithm website list [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--agent-id TEXT` - Filter by agent ID

**Examples:**
```bash
# List all sources
knowrithm website list

# Filter by agent
knowrithm website list --agent-id agent_123
```

---

### `knowrithm website agent`

List website sources for a specific agent.

**Usage:**
```bash
knowrithm website agent AGENT_ID [OPTIONS]
```

**Arguments:**
- `AGENT_ID` - The agent identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm website agent agent_123
```

**Response:**
```json
{
  "agent_id": "agent_123",
  "sources": [
    {
      "id": "source_456",
      "url": "https://example.com",
      "status": "active",
      "last_crawled": "2024-11-01T10:00:00Z",
      "pages_discovered": 127
    }
  ]
}
```

---

### `knowrithm website register`

Register a website source for crawling.

**Usage:**
```bash
knowrithm website register [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - JSON payload describing the website source (required)

**Payload Schema:**
```json
{
  "agent_id": "agent_123",
  "url": "https://example.com",
  "max_depth": 3,
  "max_pages": 100,
  "include_patterns": ["*/docs/*", "*/blog/*"],
  "exclude_patterns": ["*/admin/*", "*/private/*"],
  "follow_external_links": false,
  "respect_robots_txt": true,
  "crawl_frequency": "daily"
}
```

**Examples:**
```bash
knowrithm website register --payload '{
  "agent_id": "agent_123",
  "url": "https://docs.example.com",
  "max_depth": 2,
  "max_pages": 50
}'

knowrithm website register --payload @website-config.json
```

---

### `knowrithm website crawl`

Trigger a crawl job for a website source.

**Usage:**
```bash
knowrithm website crawl SOURCE_ID [OPTIONS]
```

**Arguments:**
- `SOURCE_ID` - The website source identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--payload TEXT` - Optional JSON payload (e.g., max_pages override)
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
# Start crawl
knowrithm website crawl source_456

# With custom options
knowrithm website crawl source_456 --payload '{
  "max_pages": 200,
  "force_recrawl": true
}'

# Wait for completion
knowrithm website crawl source_456 --wait
```

---

### `knowrithm website pages`

List pages discovered for a website source.

**Usage:**
```bash
knowrithm website pages SOURCE_ID [OPTIONS]
```

**Arguments:**
- `SOURCE_ID` - The website source identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm website pages source_456
```

**Response:**
```json
{
  "source_id": "source_456",
  "total_pages": 127,
  "pages": [
    {
      "url": "https://example.com/page1",
      "title": "Page 1",
      "status": "crawled",
      "last_crawled": "2024-11-01T10:15:00Z",
      "content_hash": "abc123"
    }
  ]
}
```

---

### `knowrithm website delete`

Delete a website source.

**Usage:**
```bash
knowrithm website delete SOURCE_ID [OPTIONS]
```

**Arguments:**
- `SOURCE_ID` - The website source identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method
- `--wait/--no-wait` - Wait for async task completion (default: False)

**Examples:**
```bash
knowrithm website delete source_456
knowrithm website delete source_456 --wait
```

---

### `knowrithm website handshake`

Call the widget handshake endpoint (unauthenticated).

**Usage:**
```bash
knowrithm website handshake [OPTIONS]
```

**Options:**
- `--payload TEXT` - JSON payload describing the widget handshake (required)

**Payload Schema:**
```json
{
  "agent_id": "agent_123",
  "domain": "example.com",
  "widget_version": "1.0.0"
}
```

**Examples:**
```bash
knowrithm website handshake --payload '{
  "agent_id": "agent_123",
  "domain": "mysite.com"
}'
```

---

## System Utilities

### `knowrithm system health`

Call the /api/health endpoint.

**Usage:**
```bash
knowrithm system health
```

**Examples:**
```bash
knowrithm system health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-02T12:00:00Z",
  "services": {
    "database": "up",
    "redis": "up",
    "celery": "up"
  }
}
```

---

### `knowrithm system task-status`

Poll task status for asynchronous operations.

**Usage:**
```bash
knowrithm system task-status TASK_ID
```

**Arguments:**
- `TASK_ID` - The task identifier

**Examples:**
```bash
knowrithm system task-status task_abc123
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "completed",
  "progress": 100,
  "result": {
    "agent_id": "agent_123",
    "message": "Agent created successfully"
  },
  "created_at": "2024-11-02T11:55:00Z",
  "completed_at": "2024-11-02T11:56:30Z"
}
```

**Possible Status Values:**
- `pending` - Task queued but not started
- `started` - Task is running
- `completed` - Task finished successfully
- `failed` - Task encountered an error
- `cancelled` - Task was cancelled

---

### `knowrithm system address-seed`

Trigger address seed data population.

**Usage:**
```bash
knowrithm system address-seed
```

**Examples:**
```bash
knowrithm system address-seed
```

---

### `knowrithm system countries`

List countries.

**Usage:**
```bash
knowrithm system countries [OPTIONS]
```

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system countries
```

**Response:**
```json
{
  "countries": [
    {
      "id": "country_001",
      "name": "United States",
      "code": "US",
      "iso_code": "USA"
    },
    {
      "id": "country_002",
      "name": "Canada",
      "code": "CA",
      "iso_code": "CAN"
    }
  ]
}
```

---

### `knowrithm system country`

Get a country by ID.

**Usage:**
```bash
knowrithm system country COUNTRY_ID [OPTIONS]
```

**Arguments:**
- `COUNTRY_ID` - The country identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system country country_001
```

---

### `knowrithm system states`

List states for a country.

**Usage:**
```bash
knowrithm system states COUNTRY_ID [OPTIONS]
```

**Arguments:**
- `COUNTRY_ID` - The country identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system states country_001
```

**Response:**
```json
{
  "country_id": "country_001",
  "states": [
    {
      "id": "state_001",
      "name": "California",
      "code": "CA"
    },
    {
      "id": "state_002",
      "name": "New York",
      "code": "NY"
    }
  ]
}
```

---

### `knowrithm system state`

Get a state and its cities.

**Usage:**
```bash
knowrithm system state STATE_ID [OPTIONS]
```

**Arguments:**
- `STATE_ID` - The state identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system state state_001
```

---

### `knowrithm system cities`

List cities for a state.

**Usage:**
```bash
knowrithm system cities STATE_ID [OPTIONS]
```

**Arguments:**
- `STATE_ID` - The state identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system cities state_001
```

**Response:**
```json
{
  "state_id": "state_001",
  "cities": [
    {
      "id": "city_001",
      "name": "Los Angeles",
      "population": 3979576
    },
    {
      "id": "city_002",
      "name": "San Francisco",
      "population": 873965
    }
  ]
}
```

---

### `knowrithm system city`

Get a city by ID.

**Usage:**
```bash
knowrithm system city CITY_ID [OPTIONS]
```

**Arguments:**
- `CITY_ID` - The city identifier

**Options:**
- `--auth [jwt|api-key|none|auto]` - Authentication method

**Examples:**
```bash
knowrithm system city city_001
```

---

## Configuration Commands

### `knowrithm config show`

Display the current configuration with sensitive values masked.

**Usage:**
```bash
knowrithm config show
```

**Examples:**
```bash
knowrithm config show
```

**Response:**
```json
{
  "base_url": "https://app.knowrithm.org",
  "verify_ssl": true,
  "auth": {
    "jwt": {
      "access_token": "eyJ0eXAi...",
      "expires_at": 1735689600
    },
    "api_key": {
      "key": "ak_123456",
      "secret": "***"
    }
  }
}
```

---

### `knowrithm config set-base-url`

Persist the Knowrithm API base URL.

**Usage:**
```bash
knowrithm config set-base-url URL
```

**Arguments:**
- `URL` - The API base URL

**Examples:**
```bash
# Production
knowrithm config set-base-url https://app.knowrithm.org
```

---

### `knowrithm config set-verify-ssl`

Toggle TLS certificate verification.

**Usage:**
```bash
knowrithm config set-verify-ssl [OPTIONS]
```

**Options:**
- `--enable/--disable` - Enable or disable verification (default: enable)

**Examples:**
```bash
# Enable SSL verification (production)
knowrithm config set-verify-ssl --enable

# Disable SSL verification (development with self-signed certs)
knowrithm config set-verify-ssl --disable
```

---

### `knowrithm config path`

Print the path to the configuration file.

**Usage:**
```bash
knowrithm config path
```

**Examples:**
```bash
knowrithm config path
# Output: /home/user/.knowrithm/config.json
```

---

## Global Options

All commands support the following global options:

### `--help`

Display help information for any command.

**Examples:**
```bash
knowrithm --help
knowrithm agent --help
knowrithm agent create --help
```

---

## Response Formats

All CLI commands output JSON responses by default. The structure follows these patterns:

### Success Response
```json
{
  "data": { ... },
  "message": "Operation successful",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

### Paginated Response
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Async Task Response
```json
{
  "task_id": "task_abc123",
  "status": "pending",
  "message": "Task queued for processing"
}
```

---

## Exit Codes

The CLI uses standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Command line syntax error
- `3` - Authentication error
- `4` - Network error
- `5` - Server error

---

## Environment Variables

The CLI respects the following environment variables:

- `KNOWRITHM_BASE_URL` - Override the API base URL
- `KNOWRITHM_API_KEY` - Set API key
- `KNOWRITHM_API_SECRET` - Set API secret
- `KNOWRITHM_JWT_TOKEN` - Set JWT access token
- `KNOWRITHM_DEBUG` - Enable debug mode (set to `1` or `true`)
- `KNOWRITHM_CONFIG_PATH` - Custom config file location

**Example:**
```bash
export KNOWRITHM_BASE_URL=https://app.knowrithm.org
export KNOWRITHM_DEBUG=1
knowrithm agent list
```

---

## Best Practices

1. **Use configuration files for complex payloads**
   ```bash
   knowrithm agent create --payload @agent-config.json
   ```

2. **Leverage pagination for large datasets**
   ```bash
   knowrithm agent list --per-page 100
   ```

3. **Wait for important operations**
   ```bash
   knowrithm agent create --payload @config.json --wait
   ```

4. **Pipe output for processing**
   ```bash
   knowrithm agent list | jq '.data[].id'
   ```

5. **Store credentials securely**
   ```bash
   knowrithm auth login  # Interactive password prompt
   ```

6. **Use authentication strategies explicitly**
   ```bash
   knowrithm agent list --auth jwt
   ```

7. **Test database connections before analysis**
   ```bash
   knowrithm database test conn_123
   knowrithm database analyze conn_123 --wait
   ```

---

## Additional Resources

- **API Documentation**: https://docs.knowrithm.org
- **Support**: agentx@notifications.knowrithm.org
- **GitHub**: https://github.com/knowrithm/knowrithm-cli

---

**Last Updated**: November 2, 2024  
**CLI Version**: 1.0.0