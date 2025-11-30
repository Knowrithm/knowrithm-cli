# Quick Reference: Enhanced Agent Test

## 🚀 Quick Commands

```bash
# Basic test (beautiful output)
knowrithm agent test

# Test with custom query
knowrithm agent test -q "What are your features?"

# Test and start chat session
knowrithm agent test --interactive

# Test specific agent
knowrithm agent test "Support Bot" -q "Hello"

# Test and chat (short form)
knowrithm agent test -i
```

## 🎨 What's New?

### Beautiful Formatting ✨
- **Color-coded sections** with emojis
- **Clean panels** for query and response
- **Organized tables** for sources
- **Clear status indicators**

### Interactive Chat 💬
- Add `-i` or `--interactive` flag
- Automatically start chat after test
- Seamless conversation flow

### Better UX 🎯
- **Animated spinner** while waiting
- **Readable layout** instead of raw JSON
- **Source tracking** with checkmarks
- **Metadata display** for debugging

## 📊 Output Sections

| Section | Icon | Color | Content |
|---------|------|-------|---------|
| Agent Info | 🤖 | Cyan | Name, model, provider |
| Query | ❓ | Yellow | Your question |
| Response | 💬 | Green | Agent's answer |
| Sources | 📚 | Blue | Citations table |
| Metadata | ℹ️ | Magenta | Stats & warnings |
| Status | ✅/❌ | Green/Red | Success/failure |

## 🎬 Example Output

```
🧪 Testing agent 'Support Bot'...
⠋ Agent is thinking...

🤖 Agent: Support Bot
Model: google/gemini-2.5-flash

❓ Query:
╭──────────────────────────────────────╮
│ What are your features?              │
╰──────────────────────────────────────╯

💬 Response:
╭──────────────────────────────────────╮
│ I can help you with:                 │
│ • Customer support                   │
│ • Product information                │
│ • Technical assistance               │
╰──────────────────────────────────────╯

📚 Sources (2):
  #   Source                    Cited
 ────────────────────────────────────
  1   https://docs.example.com    ✓
  2   https://help.example.com    ✓

✅ Test completed successfully!

💬 Would you like to start an interactive chat? (Y/n)
```

## 🔧 Options

| Flag | Short | Description |
|------|-------|-------------|
| `--query "text"` | `-q` | Custom test query |
| `--interactive` | `-i` | Start chat after test |
| `--format json` | | Output as JSON |
| `--format yaml` | | Output as YAML |
| `--no-wait` | | Don't wait for response |

## 💡 Pro Tips

1. **Set Default Agent**
   ```bash
   knowrithm context set agent "Support Bot"
   knowrithm agent test  # Uses default agent
   ```

2. **Quick Test & Chat**
   ```bash
   knowrithm agent test -i  # Fastest way to start chatting
   ```

3. **Debug Mode**
   ```bash
   knowrithm agent test --format json  # See raw response
   ```

4. **Custom Queries**
   ```bash
   knowrithm agent test -q "Complex question here"
   ```

## 🔄 Workflow

```
1. Test Agent
   ↓
2. View Beautiful Results
   ↓
3. (Optional) Start Chat
   ↓
4. Interactive Conversation
```

## 📝 Notes

- Default format is `table` (beautiful output)
- Use `--format json` for raw data
- Interactive mode requires confirmation
- Chat creates a new conversation
- All conversation history is saved

---

**See Also**: [AGENT_TEST_ENHANCEMENT.md](AGENT_TEST_ENHANCEMENT.md) for full documentation
