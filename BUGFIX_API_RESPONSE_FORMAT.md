# Bug Fix: API Response Format Handling

## Issue
The geographic selection helpers were failing with the error:
```
❌ Error fetching countries: 'list' object has no attribute 'get'
```

## Root Cause
The API endpoints for countries, states, and cities return a **list directly** instead of a dictionary with a data key. The original code assumed the response would always be a dictionary with keys like `countries`, `states`, or `cities`.

## Solution
Updated all three selection helper functions to handle **both response formats**:
1. Direct list response (actual API behavior)
2. Dictionary response with data keys (defensive programming)

### Changes Made

#### Before (Assumed dict response):
```python
response = client.get("/api/v1/country", require_auth=True)
countries = response.get("countries", [])  # ❌ Fails if response is a list
```

#### After (Handles both formats):
```python
response = client.get("/api/v1/country", require_auth=True)

# Handle both response formats: list or dict with 'countries' key
if isinstance(response, list):
    countries = response
else:
    countries = response.get("countries", response.get("data", []))
```

### Files Modified
- `knowrithm_cli/interactive.py`
  - `select_country()` - Fixed line 586-593
  - `select_state()` - Fixed line 627-634
  - `select_city()` - Fixed line 673-680

## Testing
After reinstalling the package, the commands should now work correctly:
```bash
knowrithm system country   # ✅ Should show country selection menu
knowrithm system states    # ✅ Should show country selection menu
knowrithm system state     # ✅ Should show country → state selection
knowrithm system cities    # ✅ Should show state selection menu
knowrithm system city      # ✅ Should show country → state → city selection
```

## Status
✅ **FIXED** - Package reinstalled successfully with the corrections.
