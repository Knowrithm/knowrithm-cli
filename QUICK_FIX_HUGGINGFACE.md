# Quick Fix Guide: HuggingFace API Key Error

## The Problem

```bash
$ knowrithm agent test

Testing agent 'Knowrithm Support'...
⠇ Agent is thinking...
╭───────────────────────────────────────────────────┬─────────────┬───────────────────────────┬────────╮
│ Data                                              │ Http Status │ Message                   │ Status │
├───────────────────────────────────────────────────┼─────────────┼───────────────────────────┼────────┤
│ {"details": ["API key required for HuggingFace"]} │ 400         │ Invalid LLM configuration │ error  │
╰───────────────────────────────────────────────────┴─────────────┴───────────────────────────┴────────╯
```

## The Issue

**This is a BACKEND bug, not a CLI issue.**

The backend is incorrectly validating that HuggingFace requires an API key. However:
- ✅ HuggingFace embedding models (like `all-MiniLM-L6-v2`) **do NOT require API keys**
- ✅ The CLI is working correctly
- ❌ The backend validation logic needs to be fixed

## Backend Fix Required

The backend team needs to update the validation logic to make API keys **optional** for HuggingFace providers.

**Location**: Backend codebase (likely `app/services/llm_settings.py` or `app/tasks/agents.py`)

**Change needed**:
```python
# Remove HuggingFace from required API key providers
PROVIDERS_REQUIRING_API_KEY = [
    "OpenAI",
    "Anthropic",
    "Google",
    "Cohere",
    # NOT HuggingFace
]
```

## Temporary Workarounds

### Option 1: Add Dummy API Key (Recommended)

Update your agent settings to include a placeholder API key:

```bash
knowrithm agent update <agent-id> --payload '{
  "embedding_api_key": "not-required"
}'
```

Or when creating an agent:
```bash
knowrithm agent create --payload '{
  "name": "My Agent",
  "llm_provider_id": "...",
  "llm_model_id": "...",
  "embedding_provider_id": "f46a3f49-62aa-48c9-9f00-c7fb3310a8ca",
  "embedding_model_id": "c3661f33-8c7c-406b-9bb4-36e5334fc1a6",
  "embedding_api_key": "not-required"
}'
```

### Option 2: Use Different Embedding Provider

Switch to a provider that's correctly configured:

```bash
# List available providers
knowrithm settings providers

# Update agent to use different embedding provider
knowrithm agent update <agent-id> --payload '{
  "embedding_provider_id": "<different-provider-id>",
  "embedding_model_id": "<different-model-id>",
  "embedding_api_key": "<real-api-key-if-required>"
}'
```

## For Backend Developers

See the detailed analysis in: **BACKEND_ISSUE_HUGGINGFACE_API_KEY.md**

Key points:
1. HuggingFace sentence-transformers models don't require API keys
2. Validation should check provider-specific requirements
3. Make `embedding_api_key` optional for HuggingFace provider
4. Test with models: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`

## Verification

After the backend fix is deployed, test with:

```bash
# Test agent without API key
knowrithm agent test

# Should work without errors
```

## Status

- **CLI**: ✅ Working correctly
- **Backend**: ❌ Needs fix
- **Workaround**: ✅ Available (add dummy API key)
- **Permanent Fix**: ⏳ Pending backend update

---

**Last Updated**: 2025-11-30
