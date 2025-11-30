# HuggingFace API Key Issue - Backend Fix Required

## Issue Description

When testing an agent configured with HuggingFace embedding models using `knowrithm agent test`, the following error occurs:

```
╭───────────────────────────────────────────────────┬─────────────┬───────────────────────────┬────────╮
│ Data                                              │ Http Status │ Message                   │ Status │
├───────────────────────────────────────────────────┼─────────────┼───────────────────────────┼────────┤
│ {"details": ["API key required for HuggingFace"]} │ 400         │ Invalid LLM configuration │ error  │
╰───────────────────────────────────────────────────┴─────────────┴───────────────────────────┴────────╯
```

## Root Cause

The backend is incorrectly validating that HuggingFace requires an API key. However, **HuggingFace embedding models do NOT require API keys** when:
1. Using local inference with sentence-transformers
2. Using open-source models like `all-MiniLM-L6-v2`
3. Running models through the transformers library

## Backend Logs

```
2025-11-30 11:02:59,319 INFO app: Request started id=a720c5127eed4d3c9f56655541b64a9b method=POST path=/api/v1/agent/43ce76ef-b132-4e10-8458-c842762dc344/test
2025-11-30 11:02:59,335 INFO app.services.task_dispatcher: Dispatching task agents.test_agent
2025-11-30 11:02:59,348 INFO app.services.task_dispatcher: Task agents.test_agent enqueued with id=b9b01856-1fde-4543-b8a4-e5c649c42586
2025-11-30 11:02:59,349 INFO app: Request completed id=a720c5127eed4d3c9f56655541b64a9b status=202
```

The request is accepted (202) and queued, but the task fails during validation.

## Where to Fix (Backend)

The issue is in the **backend validation logic**, likely in one of these locations:

### 1. LLM Settings Validation
**File**: `app/services/llm_settings.py` or `app/models/llm_settings.py`

Look for validation code that checks for API keys based on provider type:

```python
# INCORRECT - Current implementation
if provider.name == "HuggingFace" and not llm_api_key:
    raise ValidationError("API key required for HuggingFace")
```

**Fix**:
```python
# CORRECT - HuggingFace doesn't require API keys for local models
PROVIDERS_REQUIRING_API_KEY = [
    "OpenAI",
    "Anthropic", 
    "Google",
    "Cohere",
    # HuggingFace is NOT in this list
]

if provider.name in PROVIDERS_REQUIRING_API_KEY and not llm_api_key:
    raise ValidationError(f"API key required for {provider.name}")
```

### 2. Agent Test Task
**File**: `app/tasks/agents.py` - `test_agent` function

The validation might be happening in the agent test task:

```python
# Look for code like this:
def test_agent(agent_id, payload):
    agent = Agent.query.get(agent_id)
    settings = agent.llm_settings
    
    # INCORRECT validation
    if settings.embedding_provider.name == "HuggingFace":
        if not settings.embedding_api_key:
            return {
                "status": "error",
                "message": "Invalid LLM configuration",
                "details": ["API key required for HuggingFace"]
            }
```

**Fix**: Remove this validation for HuggingFace or make it conditional based on the specific model/endpoint being used.

### 3. Provider Configuration
**File**: `app/models/provider.py` or provider seed data

Check if HuggingFace provider has `requires_api_key=True` set incorrectly:

```python
# INCORRECT
{
    "name": "HuggingFace",
    "type": "embedding",
    "requires_api_key": True,  # ❌ Should be False
}

# CORRECT
{
    "name": "HuggingFace",
    "type": "embedding",
    "requires_api_key": False,  # ✅ Correct
}
```

## Recommended Backend Changes

### Option 1: Make API Key Optional for HuggingFace
```python
# In validation logic
OPTIONAL_API_KEY_PROVIDERS = ["HuggingFace"]

if provider.name not in OPTIONAL_API_KEY_PROVIDERS:
    if provider.requires_api_key and not api_key:
        raise ValidationError(f"API key required for {provider.name}")
```

### Option 2: Model-Specific Validation
```python
# More granular - check if specific model requires API key
MODELS_REQUIRING_API_KEY = {
    "HuggingFace": ["gpt2", "bloom"],  # Only certain models
    "OpenAI": "*",  # All models
}

def requires_api_key(provider_name, model_name):
    if provider_name not in MODELS_REQUIRING_API_KEY:
        return False
    
    required_models = MODELS_REQUIRING_API_KEY[provider_name]
    if required_models == "*":
        return True
    
    return model_name in required_models
```

### Option 3: Environment-Based Configuration
```python
# Allow override via environment variable
import os

HUGGINGFACE_API_KEY_REQUIRED = os.getenv("HUGGINGFACE_REQUIRE_API_KEY", "false").lower() == "true"

if provider.name == "HuggingFace" and HUGGINGFACE_API_KEY_REQUIRED:
    if not api_key:
        raise ValidationError("API key required for HuggingFace")
```

## Testing the Fix

After implementing the backend fix, test with:

```bash
# CLI test
knowrithm agent test

# Or with specific agent
knowrithm agent test --agent-id <agent-id>

# Python SDK test
from knowrithm_cli.client import KnowrithmClient

client = KnowrithmClient(base_url="https://app.knowrithm.org/api")
client.login(email="user@example.com", password="password")

response = client.post(
    "/api/v1/agent/<agent-id>/test",
    json={"query": "Test query"},
    require_auth=True
)

result = client.handle_async_response(response, wait=True)
print(result)
```

## HuggingFace Models That Don't Require API Keys

These models work without API keys:
- `all-MiniLM-L6-v2` (embedding)
- `all-mpnet-base-v2` (embedding)
- `paraphrase-multilingual-MiniLM-L12-v2` (embedding)
- Most sentence-transformers models

## HuggingFace Models That MAY Require API Keys

Only when using the **Inference API** (not local):
- Gated models (require HuggingFace account)
- Models behind HuggingFace Inference Endpoints
- Pro/Enterprise tier models

## Workaround (Temporary)

Until the backend is fixed, you can:

1. **Add a dummy API key** (if validation is the only issue):
   ```python
   agent_data = {
       "name": "Test Agent",
       "embedding_provider_id": "f46a3f49-62aa-48c9-9f00-c7fb3310a8ca",
       "embedding_model_id": "c3661f33-8c7c-406b-9bb4-36e5334fc1a6",
       "embedding_api_key": "not-required-but-added-for-validation"
   }
   ```

2. **Use a different embedding provider** temporarily:
   - OpenAI (requires real API key)
   - Cohere (requires real API key)
   - Local models through different providers

## Summary

- **Issue**: Backend incorrectly requires API key for HuggingFace
- **Location**: Backend validation logic (not CLI)
- **Fix Required**: Update backend to make HuggingFace API key optional
- **CLI Status**: ✅ Working correctly - sending proper requests
- **Backend Status**: ❌ Needs fix - incorrect validation

## Related Files

- Backend: `app/services/llm_settings.py`
- Backend: `app/tasks/agents.py`
- Backend: `app/models/provider.py`
- CLI: Working as expected - no changes needed

---

**Note**: This is a backend issue. The CLI is functioning correctly and sending the appropriate requests. The fix must be implemented in the backend codebase.
