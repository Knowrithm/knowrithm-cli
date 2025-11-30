# Agent Test Command Enhancement

## Overview

The `knowrithm agent test` command has been completely revamped to provide a beautiful, user-friendly testing experience with rich formatting and interactive chat capabilities.

## New Features

### 1. **Beautiful Output Formatting**

Instead of showing raw JSON in a table, the test results are now displayed in a clean, organized format:

#### Before:
```
╭───────────────────────────────────────────────────┬─────────────┬──────────────────────┬─────────╮
│ Data                                              │ Http Status │ Message              │ Status  │
├───────────────────────────────────────────────────┼─────────────┼──────────────────────┼─────────┤
│ {"agent": {"id": "43ce76ef...", "name": ...       │ 200         │ Agent test completed │ success │
╰───────────────────────────────────────────────────┴─────────────┴──────────────────────┴─────────╯
```

#### After:
```
🧪 Testing agent 'Knowrithm Support'...

🤖 Agent: Knowrithm Support
Model: google/gemini-2.5-flash

❓ Query:
╭─────────────────────────────────────────────────────────╮
│ Hello, can you introduce yourself?                     │
╰─────────────────────────────────────────────────────────╯

💬 Response:
╭─────────────────────────────────────────────────────────╮
│ Hello! I'm Knowrithm Support, a professional AI        │
│ assistant designed to provide accurate and helpful      │
│ information.                                            │
│                                                         │
│ Knowrithm offers a platform where the same governance, │
│ telemetry, and knowledge layer travel with you [Source │
│ 1]...                                                   │
╰─────────────────────────────────────────────────────────╯

📚 Sources (1):
  #   Source                                    Cited
 ─────────────────────────────────────────────────────
  1   https://www.knowrithm.org/                 ✓

ℹ️  Metadata:
  Total Sources    1
  Cited Sources    1

✅ Test completed successfully!
```

### 2. **Interactive Chat Session**

New `--interactive` (or `-i`) flag allows you to start a chat session immediately after testing:

```bash
# Test and automatically start chat
knowrithm agent test --interactive

# Or with short flag
knowrithm agent test -i
```

After the test completes, you'll be prompted:
```
💬 Would you like to start an interactive chat session with this agent? (Y/n)
```

If you select "Yes", it will:
1. Create a new conversation
2. Launch the interactive chat interface
3. Allow you to continue chatting with the agent

### 3. **Rich Spinner Animation**

While the agent is processing, you'll see an animated spinner:
```
⠋ Agent is thinking...
```

## Usage Examples

### Basic Test
```bash
# Test with default query
knowrithm agent test

# Test with custom query
knowrithm agent test --query "What are your pricing plans?"

# Test specific agent
knowrithm agent test "Support Bot" --query "Hello"
```

### Interactive Mode
```bash
# Test and start chat session
knowrithm agent test --interactive

# Test with custom query and start chat
knowrithm agent test -q "Hello" -i

# Test specific agent and start chat
knowrithm agent test "Sales Bot" --interactive
```

### Different Output Formats
```bash
# JSON format (raw data)
knowrithm agent test --format json

# YAML format
knowrithm agent test --format yaml

# Table format (default, with beautiful formatting)
knowrithm agent test --format table
```

## Display Sections

The new formatted output includes:

1. **Agent Info**
   - Agent name
   - LLM provider and model

2. **Query Section**
   - Shows the question sent to the agent
   - Displayed in a yellow-bordered panel

3. **Response Section**
   - Agent's full response
   - Displayed in a green-bordered panel
   - Properly formatted with line breaks

4. **Sources Section**
   - Table of all sources/citations
   - Shows source number, document name, and whether it was cited
   - ✓ for cited sources, ✗ for uncited

5. **Metadata Section**
   - Total sources count
   - Cited sources count
   - Any warnings (if present)

6. **Status Indicator**
   - ✅ Success message if test passed
   - ❌ Error message if test failed

## Command Options

| Option | Short | Description |
|--------|-------|-------------|
| `--query` | `-q` | Custom test query to send |
| `--payload` | | JSON payload for advanced testing |
| `--format` | | Output format (table, json, yaml, csv) |
| `--interactive` | `-i` | Start chat session after test |
| `--wait/--no-wait` | | Wait for async response (default: yes) |
| `--auth` | | Authentication method |

## Interactive Chat Flow

When using `--interactive`:

1. **Test Execution**
   ```
   🧪 Testing agent 'Support Bot'...
   ⠋ Agent is thinking...
   ```

2. **Test Results Display**
   ```
   [Beautiful formatted output as shown above]
   ```

3. **Chat Prompt**
   ```
   💬 Would you like to start an interactive chat session with this agent? (Y/n)
   ```

4. **Chat Session Start**
   ```
   🚀 Starting chat with Support Bot...
   
   Chat started with Support Bot
   Type your message (or 'exit' to quit, 'help' for commands)
   
   You: 
   ```

5. **Interactive Conversation**
   - Continue chatting with the agent
   - Full conversation history maintained
   - Type `exit` to end the session

## Benefits

### For Users
- **Easier to Read**: Clean, organized output vs. raw JSON
- **Visual Hierarchy**: Color-coded sections with emojis
- **Source Tracking**: Clear indication of which sources were used
- **Seamless Testing**: Test and chat in one flow

### For Developers
- **Better Debugging**: Clearly see query, response, and sources
- **Quick Iteration**: Test changes and immediately interact
- **Source Validation**: Verify citation accuracy at a glance

## Technical Details

### Rich Library Integration
The new formatting uses the `rich` library for:
- Colored text and panels
- Tables with custom styling
- Animated spinners
- Box drawing characters

### Response Parsing
The formatter handles various response structures:
- Direct response objects
- Nested `data` fields
- String-encoded JSON
- Fallback to original format for unknown structures

### Error Handling
- Gracefully handles missing fields
- Shows "N/A" for unavailable data
- Maintains compatibility with all output formats
- Falls back to standard formatting for non-table formats

## Comparison

### Old Behavior
```bash
$ knowrithm agent test
Testing agent 'Support Bot'...
⠇ Agent is thinking...
╭─────────────────────────────────────╮
│ [Long JSON string in table cell]    │
╰─────────────────────────────────────╯
```

### New Behavior
```bash
$ knowrithm agent test

🧪 Testing agent 'Support Bot'...
⠋ Agent is thinking...

🤖 Agent: Support Bot
Model: google/gemini-2.5-flash

❓ Query:
╭──────────────────────────────────────╮
│ Hello, can you introduce yourself?  │
╰──────────────────────────────────────╯

💬 Response:
╭──────────────────────────────────────╮
│ [Beautifully formatted response]     │
╰──────────────────────────────────────╯

📚 Sources (2):
  #   Source                    Cited
 ────────────────────────────────────
  1   https://example.com         ✓
  2   https://docs.example.com    ✓

✅ Test completed successfully!

💬 Would you like to start an interactive chat session? (Y/n)
```

## See Also

- [Agent Commands](COMMAND_REFERENCE.md#agent-commands) - Full agent command reference
- [Interactive Chat](INTERACTIVE_FEATURES.md) - Interactive chat documentation
- [Context Management](QUICK_START.md#context) - Using context for default agents
