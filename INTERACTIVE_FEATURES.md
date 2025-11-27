# Interactive Features Guide

This document describes the new interactive features added to the Knowrithm CLI.

## Overview

The Knowrithm CLI now includes enhanced interactive features:

1. **Command Auto-Completion** - Tab completion for all CLI commands
2. **Arrow-Key Navigation** - Navigate menus using arrow keys instead of typing numbers
3. **Interactive Prompts** - Beautiful, user-friendly prompts for all inputs

## Auto-Completion

### In Interactive Mode

When you run `knowrithm` without any arguments, you enter interactive mode. In this mode, you can:

- **Tab to complete commands**: Start typing a command and press `Tab` to see suggestions
- **Command history**: Use `↑` and `↓` arrow keys to navigate through command history
- **Search history**: Press `Ctrl+R` to search through command history

Example:
```bash
knowrithm> ag<Tab>
# Autocompletes to: knowrithm> agent

knowrithm> agent <Tab>
# Shows: create, list, get, update, delete, etc.
```

### Available Commands

The auto-completion includes:
- All Knowrithm CLI commands: `agent`, `auth`, `conversation`, `document`, etc.
- Common shell commands: `cd`, `ls`, `dir`, `pwd`, `clear`, `exit`, `quit`

## Arrow-Key Navigation

### Menu Selection

Instead of typing numbers to select from a menu, you can now:

1. **Use arrow keys** (`↑` and `↓`) to navigate options
2. **Press Enter** to select the highlighted option
3. **Type to filter** - Start typing to filter the list

### Example: Creating an Agent

When you run `knowrithm agent create --interactive`, you'll see:

```
=== Create New Agent ===

? Agent name: My Support Bot
? Description: A helpful customer support agent

📋 Select LLM Provider:
? Select LLM provider (Use arrow keys)
 ❯ OpenAI (llm)
   Anthropic (llm)
   Google (both)
```

Simply use the arrow keys to navigate and press Enter to select!

### Example: Selecting an Agent to Chat

When you run `knowrithm agent chat` without specifying an agent:

```
Select an agent to chat with:
? Select an agent (Use arrow keys)
 ❯ Support Bot (Status: active, Model: gpt-4)
   Sales Assistant (Status: active, Model: claude-3)
   Research Agent (Status: inactive, Model: gemini-pro)
```

## Interactive Prompts

### Text Input

All text inputs now show a clear prompt:

```
? Agent name: _
```

You can:
- Type your input
- Use `Ctrl+A` to go to start of line
- Use `Ctrl+E` to go to end of line
- Use `Ctrl+K` to delete to end of line

### Confirmation Prompts

Yes/No questions are now interactive:

```
? Do you want to provide API keys? (y/N)
```

- Press `y` or `Y` for yes
- Press `n` or `N` for no
- Press `Enter` to use the default (shown in uppercase)

### List Selection

Choose from a list of options:

```
? Select agent status (Use arrow keys)
 ❯ active
   inactive
   training
```

## Benefits

### Better User Experience

- **Visual feedback**: See what you're selecting before confirming
- **No typos**: Can't accidentally enter an invalid number
- **Faster navigation**: Arrow keys are faster than typing numbers
- **Discoverable**: Auto-completion helps you discover available commands

### Accessibility

- **Keyboard-only navigation**: No mouse required
- **Clear visual indicators**: Highlighted selections and pointers
- **Consistent styling**: Cyan theme matching the Knowrithm brand

## Technical Details

### Dependencies

The interactive features use:
- `prompt_toolkit` - For command auto-completion and history
- `questionary` - For arrow-key navigation and interactive prompts

### Styling

All interactive prompts use a custom cyan theme that matches the Knowrithm CLI branding:

```python
custom_style = Style([
    ('qmark', 'fg:#00d4aa bold'),       # Question mark
    ('answer', 'fg:#00d4aa bold'),      # Selected answer
    ('pointer', 'fg:#00d4aa bold'),     # Pointer (arrow)
    ('highlighted', 'fg:#00d4aa bold'), # Highlighted choice
])
```

## Commands with Interactive Features

The following commands now support arrow-key navigation and interactive resource selection:

### Agent Commands
- `agent create --interactive`
- `agent delete` (select agent)
- `agent update` (select agent)
- `agent chat` (select agent)
- `agent get` (select agent)

### Document Commands
- `document delete` (select document)
- `document restore` (select document)
- `document agent` (select agent)
- `document delete-chunks` (select document)
- `document restore-chunks` (select document)

### Conversation Commands
- `conversation chat` (select conversation)
- `conversation messages` (select conversation)
- `conversation delete` (select conversation)
- `conversation restore` (select conversation)
- `conversation agent` (select agent)

### Database Commands
- `database get` (select connection)
- `database delete` (select connection)
- `database restore` (select connection)
- `database test` (select connection)
- `database analyze` (select connection)
- `database tables` (select connection)
- `database text-to-sql` (select connection)

### Company Commands
- `company get` (select company)
- `company update` (select company)
- `company delete` (select company)
- `company restore` (select company)
- `company statistics` (select company)

### Lead Commands
- `lead get` (select lead)
- `lead update` (select lead)
- `lead delete` (select lead)

### Settings Commands
- `settings get` (select settings)
- `settings update` (select settings)
- `settings delete` (select settings)
- `settings test` (select settings)
- `settings list-company` (select company)
- `settings list-agent` (select agent)

### Website Commands
- `website get` (select source)
- `website update` (select source)
- `website delete` (select source)
- `website crawl` (select source)
- `website pages` (select source)
- `website agent` (select agent)

## Tips & Tricks

1. **Quick Selection**: In list menus, start typing to filter options
2. **Cancel Anytime**: Press `Ctrl+C` to cancel any interactive prompt
3. **History Search**: In interactive mode, use `Ctrl+R` to search command history
4. **Clear Screen**: Type `clear` or `cls` to clear the screen while keeping the logo

## Troubleshooting

### Auto-completion not working

Make sure you're in interactive mode (run `knowrithm` without arguments).

### Arrow keys not working

Ensure your terminal supports ANSI escape sequences. Most modern terminals do, including:
- Windows Terminal
- PowerShell
- CMD (Windows 10+)
- iTerm2 (macOS)
- GNOME Terminal (Linux)
- VS Code integrated terminal

### Prompts look weird

If you see strange characters instead of arrows, your terminal might not support Unicode. Try:
1. Updating your terminal
2. Setting your terminal encoding to UTF-8
3. Using a different terminal emulator

## Examples

### Complete Agent Creation Flow

```bash
knowrithm> agent create --interactive

=== Create New Agent ===

? Agent name: Customer Support Bot
? Description: Handles customer inquiries and support tickets

📋 Select LLM Provider:
? Select LLM provider (Use arrow keys)
 ❯ OpenAI (llm)

🤖 Available Models for OpenAI:
? Select LLM model (Use arrow keys)
 ❯ gpt-4 (context: 8192)
   gpt-3.5-turbo (context: 4096)

✓ LLM: OpenAI / gpt-4

📋 Select Embedding Provider:
? Select embedding provider (Use arrow keys)
 ❯ OpenAI (both)

🔤 Available Embedding Models for OpenAI:
? Select embedding model (Use arrow keys)
 ❯ text-embedding-3-small (dimension: 1536)

✓ Embeddings: OpenAI / text-embedding-3-small

? Do you want to provide API keys? (y/N) n

? Configure advanced settings? (y/N) n

Creating agent... (this may take a moment)

✅ Agent created successfully!

  Name: Customer Support Bot
  ID: agent_abc123
  Status: active
  Model: gpt-4
```

### Interactive Mode Session

```bash
knowrithm> ag<Tab>
knowrithm> agent list

# ... agent list output ...

knowrithm> agent chat

? Select an agent (Use arrow keys)
 ❯ Customer Support Bot (Status: active, Model: gpt-4)

Starting chat with Customer Support Bot...
Type 'exit' or 'quit' to end the conversation.

You: Hello!
Assistant: Hello! How can I help you today?

You: exit

Goodbye!

knowrithm> exit
```
