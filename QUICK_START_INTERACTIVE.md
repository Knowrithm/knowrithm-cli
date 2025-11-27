# Quick Start: Interactive Features

## 🎯 What's New?

The Knowrithm CLI now has **interactive features** that make it easier and faster to use!

### ✨ Key Features

1. **Tab Completion** - Press `Tab` to auto-complete commands
2. **Arrow Key Menus** - Use `↑` and `↓` to navigate menus
3. **Command History** - Use `↑` and `↓` to browse previous commands
4. **Visual Feedback** - See what you're selecting before you confirm

## 🚀 Getting Started

### Step 1: Update Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Try Interactive Mode

```bash
knowrithm
```

You'll see the Knowrithm logo and a prompt:

```
knowrithm>
```

### Step 3: Use Tab Completion

Start typing and press `Tab`:

```bash
knowrithm> ag<Tab>
# Completes to: agent

knowrithm> agent cr<Tab>
# Completes to: agent create
```

### Step 4: Create an Agent Interactively

```bash
knowrithm> agent create --interactive
```

Now use **arrow keys** to navigate menus instead of typing numbers!

## 📝 Quick Examples

### Example 1: Auto-Completion

```bash
knowrithm> a<Tab>
# Shows: agent, analytics, auth

knowrithm> agent <Tab>
# Shows: create, list, get, update, delete, chat, etc.
```

### Example 2: Arrow-Key Navigation

When creating an agent:

```
? Select LLM provider (Use arrow keys)
 ❯ OpenAI (llm)          ← Use ↑↓ to move
   Anthropic (llm)
   Google (both)
```

Press `Enter` to select the highlighted option!

### Example 3: Command History

```bash
knowrithm> agent list
# ... output ...

knowrithm> <Press ↑>
# Shows: agent list

knowrithm> <Press ↑ again>
# Shows previous command
```

### Example 4: Search History

```bash
knowrithm> <Press Ctrl+R>
# Type to search: agent
# Shows matching commands from history
```

## ⌨️ Keyboard Shortcuts

### In Interactive Mode

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete command |
| `↑` / `↓` | Navigate command history |
| `Ctrl+R` | Search command history |
| `Ctrl+C` | Cancel current operation |
| `Ctrl+D` or `exit` | Exit interactive mode |

### In Arrow-Key Menus

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Navigate options |
| `Enter` | Select highlighted option |
| `Ctrl+C` | Cancel and go back |
| Type letters | Filter options (in some menus) |

### In Text Input

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Go to start of line |
| `Ctrl+E` | Go to end of line |
| `Ctrl+K` | Delete to end of line |
| `Ctrl+U` | Delete entire line |

## 💡 Tips

1. **Start with Interactive Mode**: Run `knowrithm` alone to explore commands with tab completion

2. **Use Arrow Keys**: In menus, arrow keys are faster than typing numbers

3. **Search History**: `Ctrl+R` is great for finding commands you ran before

4. **Cancel Anytime**: `Ctrl+C` works everywhere to cancel and go back

5. **Clear Screen**: Type `clear` to clear the screen while keeping the logo

## 🎨 What It Looks Like

### Before (Old Way)
```
Select LLM provider:
  1. OpenAI (llm)
  2. Anthropic (llm)
  3. Google (both)

Select LLM provider (number) [1]: 2
```

### After (New Way)
```
📋 Select LLM Provider:
? Select LLM provider (Use arrow keys)
   OpenAI (llm)
 ❯ Anthropic (llm)        ← Highlighted with arrow
   Google (both)
```

Much better! 🎉

## 🔧 Troubleshooting

### Tab completion not working?
- Make sure you're in interactive mode (`knowrithm` without arguments)
- Try pressing `Tab` twice

### Arrow keys showing weird characters?
- Update your terminal to a modern version
- Try using Windows Terminal, PowerShell, or VS Code terminal

### Prompts look strange?
- Make sure your terminal supports UTF-8 encoding
- Try a different terminal emulator

## 📚 Learn More

- See `INTERACTIVE_FEATURES.md` for detailed documentation
- See `INTERACTIVE_IMPLEMENTATION.md` for technical details
- Run `knowrithm --help` for command reference

## 🎯 Try It Now!

```bash
# Enter interactive mode
knowrithm

# Try tab completion
knowrithm> agent <Tab>

# Create an agent with arrow-key menus
knowrithm> agent create --interactive

# Use arrow keys to navigate!
```

Enjoy the new interactive experience! 🚀
