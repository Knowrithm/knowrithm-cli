# Knowrithm CLI - Python SDK Examples

This document provides Python code examples for using the Knowrithm CLI client programmatically.

## Installation

```bash
pip install -e .
```

## Basic Setup

```python
from knowrithm_cli.client import KnowrithmClient

# Initialize client
client = KnowrithmClient(
    base_url="https://app.knowrithm.org/api",
    verify_ssl=True
)

# Authenticate with JWT
client.login(email="user@example.com", password="your_password")

# Or use API keys
client.set_api_key(key="your_api_key", secret="your_api_secret")
```

## Agent Management

### Create Agent

```python
# Create agent with provider/model IDs
agent_data = {
    "name": "Support Bot",
    "description": "Customer support agent",
    "status": "active",
    "llm_provider_id": "0120d5ae-9bcb-4858-b13b-d9aeb5ef4374",  # Google Gemini
    "llm_model_id": "4e57a9ff-8132-425c-8bdf-a878735953ed",     # gemini-2.5-flash
    "embedding_provider_id": "f46a3f49-62aa-48c9-9f00-c7fb3310a8ca",  # HuggingFace
    "embedding_model_id": "c3661f33-8c7c-406b-9bb4-36e5334fc1a6",     # all-MiniLM-L6-v2
    "llm_api_key": "AIza...",  # Optional
}

response = client.post("/api/v1/agent", json=agent_data, require_auth=True)

# Handle async response
if response.get("task_id"):
    final_response = client.handle_async_response(response, wait=True)
    agent = final_response.get("agent")
    print(f"Agent created: {agent['name']} (ID: {agent['id']})")
```

### List Agents

```python
# List all agents
response = client.get("/api/v1/agent", require_auth=True)
agents = response.get("agents", [])

for agent in agents:
    print(f"{agent['name']}: {agent['status']}")

# With filters
params = {
    "status": "active",
    "search": "support",
    "page": 1,
    "per_page": 20
}
response = client.get("/api/v1/agent", params=params, require_auth=True)
```

### Get Agent Details

```python
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"
response = client.get(f"/api/v1/agent/{agent_id}", require_auth=True)
agent = response.get("agent")

print(f"Name: {agent['name']}")
print(f"Status: {agent['status']}")
print(f"Model: {agent['model_name']}")
```

### Update Agent

```python
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"
update_data = {
    "name": "Updated Support Bot",
    "status": "active",
    "description": "Enhanced customer support"
}

response = client.put(f"/api/v1/agent/{agent_id}", json=update_data, require_auth=True)

if response.get("task_id"):
    final_response = client.handle_async_response(response, wait=True)
```

### Test Agent

```python
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"
test_payload = {
    "query": "What is your refund policy?"
}

response = client.post(
    f"/api/v1/agent/{agent_id}/test",
    json=test_payload,
    require_auth=True
)

if response.get("task_id"):
    result = client.handle_async_response(response, wait=True)
    print(f"Response: {result.get('response')}")
```

## Document Management

### Upload Documents

```python
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"

# Upload file
with open("README.md", "rb") as f:
    files = {"file": f}
    data = {"agent_id": agent_id}
    
    response = client.post(
        "/api/v1/document/upload",
        data=data,
        files=files,
        require_auth=True
    )
    
    document = response.get("document")
    print(f"Uploaded: {document['original_filename']}")
```

### List Documents

```python
# List all documents
response = client.get("/api/v1/document", require_auth=True)
documents = response.get("documents", [])

# List for specific agent
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"
response = client.get(f"/api/v1/document/agent/{agent_id}", require_auth=True)
```

### Search Documents

```python
search_payload = {
    "query": "refund policy",
    "agent_id": "ecb41332-31a6-49ee-90ee-163da82dc5b5",
    "top_k": 5
}

response = client.post(
    "/api/v1/document/search",
    json=search_payload,
    require_auth=True
)

results = response.get("results", [])
for result in results:
    print(f"Score: {result['score']}, Text: {result['text'][:100]}...")
```

## Conversation Management

### Create Conversation

```python
conversation_data = {
    "agent_id": "ecb41332-31a6-49ee-90ee-163da82dc5b5",
    "entity_type": "lead",
    "entity_id": "lead-uuid-here"
}

response = client.post(
    "/api/v1/conversation",
    json=conversation_data,
    require_auth=True
)

if response.get("task_id"):
    result = client.handle_async_response(response, wait=True)
    conversation = result.get("conversation")
    print(f"Conversation ID: {conversation['id']}")
```

### Send Message

```python
conversation_id = "conversation-uuid-here"
message_data = {
    "message": "Hello, I need help with my order"
}

response = client.post(
    f"/api/v1/conversation/{conversation_id}/chat",
    json=message_data,
    require_auth=True
)

if response.get("task_id"):
    result = client.handle_async_response(response, wait=True)
    reply = result.get("reply")
    print(f"Agent: {reply}")
```

### List Messages

```python
conversation_id = "conversation-uuid-here"
response = client.get(
    f"/api/v1/conversation/{conversation_id}/messages",
    require_auth=True
)

messages = response.get("messages", [])
for msg in messages:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    print(f"{role}: {content}")
```

## Analytics

### Get Dashboard

```python
response = client.get("/api/v1/analytic/dashboard", require_auth=True)

# Extract key metrics
core_metrics = response.get("core_metrics", {})
print(f"Total Agents: {core_metrics.get('total_agents')}")
print(f"Total Conversations: {core_metrics.get('total_conversations')}")
print(f"Total Messages: {core_metrics.get('total_messages')}")
```

### Agent Analytics

```python
agent_id = "ecb41332-31a6-49ee-90ee-163da82dc5b5"
params = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}

response = client.get(
    f"/api/v1/analytic/agent/{agent_id}",
    params=params,
    require_auth=True
)

analytics = response.get("analytics", {})
print(f"Total Conversations: {analytics.get('total_conversations')}")
print(f"Average Rating: {analytics.get('average_rating')}")
```

## Database Integration

### Create Connection

```python
db_config = {
    "name": "Production DB",
    "database_type": "postgresql",
    "host": "db.example.com",
    "port": 5432,
    "database": "production",
    "username": "readonly",
    "password": "secure_password",
    "agent_id": "ecb41332-31a6-49ee-90ee-163da82dc5b5"
}

response = client.post(
    "/api/v1/database",
    json=db_config,
    require_auth=True
)

connection = response.get("connection")
print(f"Connection ID: {connection['id']}")
```

### Text-to-SQL

```python
connection_id = "connection-uuid-here"
query_data = {
    "question": "Show me total sales by month for the last year"
}

response = client.post(
    f"/api/v1/database/{connection_id}/text-to-sql",
    json=query_data,
    require_auth=True
)

sql = response.get("sql")
print(f"Generated SQL: {sql}")
```

## Error Handling

```python
from knowrithm_cli.client import KnowrithmClient
from knowrithm_cli.exceptions import APIError, AuthenticationError

client = KnowrithmClient(base_url="https://app.knowrithm.org/api")

try:
    # Attempt API call
    response = client.get("/api/v1/agent", require_auth=True)
    agents = response.get("agents", [])
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Re-authenticate
    client.login(email="user@example.com", password="password")
    
except APIError as e:
    print(f"API Error: {e.status_code} - {e.message}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced: Custom Request Handling

```python
# Custom headers
headers = {"X-Custom-Header": "value"}
response = client.get("/api/v1/agent", headers=headers, require_auth=True)

# Disable SSL verification (development only)
client = KnowrithmClient(
    base_url="http://localhost:8000/api",
    verify_ssl=False
)

# Custom timeout
response = client.get("/api/v1/agent", timeout=30, require_auth=True)

# Use specific auth method
response = client.get("/api/v1/agent", use_jwt=True, use_api_key=False)
```

## Complete Example: Agent Workflow

```python
from knowrithm_cli.client import KnowrithmClient

# Initialize
client = KnowrithmClient(base_url="https://app.knowrithm.org/api")
client.login(email="admin@example.com", password="password")

# 1. Create agent
agent_data = {
    "name": "Sales Bot",
    "description": "Handles sales inquiries",
    "status": "active",
    "llm_provider_id": "0120d5ae-9bcb-4858-b13b-d9aeb5ef4374",
    "llm_model_id": "4e57a9ff-8132-425c-8bdf-a878735953ed",
    "embedding_provider_id": "f46a3f49-62aa-48c9-9f00-c7fb3310a8ca",
    "embedding_model_id": "c3661f33-8c7c-406b-9bb4-36e5334fc1a6",
}

response = client.post("/api/v1/agent", json=agent_data, require_auth=True)
agent = client.handle_async_response(response, wait=True).get("agent")
agent_id = agent["id"]

print(f"✅ Created agent: {agent['name']} ({agent_id})")

# 2. Upload training documents
with open("sales_guide.pdf", "rb") as f:
    files = {"file": f}
    data = {"agent_id": agent_id}
    doc_response = client.post(
        "/api/v1/document/upload",
        data=data,
        files=files,
        require_auth=True
    )
    print(f"✅ Uploaded document: {doc_response['document']['original_filename']}")

# 3. Test the agent
test_payload = {"query": "What are your pricing plans?"}
test_response = client.post(
    f"/api/v1/agent/{agent_id}/test",
    json=test_payload,
    require_auth=True
)
result = client.handle_async_response(test_response, wait=True)
print(f"✅ Test response: {result.get('response')}")

# 4. Get agent statistics
stats = client.get(f"/api/v1/agent/{agent_id}/stats", require_auth=True)
print(f"✅ Agent stats: {stats}")

print("\n🎉 Agent workflow completed successfully!")
```

## See Also

- [README.md](README.md) - CLI command reference
- [USER_GUIDE.md](USER_GUIDE.md) - Comprehensive user guide
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Full API documentation
