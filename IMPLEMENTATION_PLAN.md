# Knowrithm CLI Enhancement - Implementation Plan

## Overview
This document outlines the comprehensive enhancement plan for the Knowrithm CLI to make it significantly more user-friendly and powerful.

## Key Improvements

### 1. User-Friendly Identification System
**Problem**: Current CLI requires UUIDs for all operations
**Solution**: 
- Add name-based lookups for agents, conversations, databases
- Implement fuzzy matching for names
- Cache frequently used IDs locally
- Add `--by-name` flag to all get/update/delete commands

### 2. Interactive Mode
**Problem**: Requires complex JSON payloads
**Solution**:
- Add interactive prompts for common operations
- Wizard-style agent creation
- Step-by-step document upload
- Interactive conversation mode

### 3. Enhanced Agent Management
**Features**:
- `agent create-interactive` - Wizard for agent creation
- `agent train` - Simplified training with documents/databases
- `agent chat` - Direct chat interface
- `agent list --mine` - Show only user's agents
- `agent switch <name>` - Set active agent context

### 4. Conversation Improvements
**Features**:
- `conversation start <agent-name>` - Start new conversation by agent name
- `conversation continue [name]` - Resume last or named conversation
- `conversation chat` - Interactive chat mode
- `conversation history` - Show recent conversations
- `conversation export <id> --format [txt|json|md]` - Export conversations

### 5. Smart Context Management
**Features**:
- Store active agent, conversation, organization
- Commands use context when IDs not provided
- `context show` - Display current context
- `context set agent/conversation/org <name>`
- `context clear`

### 6. Role-Based Commands
**Admin Commands**:
- `admin users list/add/remove/update`
- `admin analytics dashboard`
- `admin audit-log`

**Super Admin Commands**:
- `superadmin companies list/create/manage`
- `superadmin analytics <type>`
- `superadmin system health/metrics`

### 7. Document & Training Management
**Features**:
- `train upload <files...> --agent <name>`
- `train url <url> --agent <name> --crawl`
- `train database connect --agent <name>`
- `train status --agent <name>`
- `train list --agent <name>`

### 8. Better Output Formatting
**Features**:
- Table format for lists (using rich/tabulate)
- Tree view for hierarchical data
- Progress bars for async operations
- Color-coded status indicators
- `--format [table|json|yaml|csv]` option

### 9. Configuration Profiles
**Features**:
- Multiple environment profiles (dev, staging, prod)
- `config profile create/switch/delete`
- Per-profile credentials
- Default profile selection

### 10. Error Handling & Help
**Features**:
- Meaningful error messages with suggestions
- Context-aware help
- Examples in help text
- Did-you-mean suggestions for typos

## Implementation Phases

### Phase 1: Core Enhancements (Week 1)
- [ ] Name-based lookups for agents
- [ ] Context management system
- [ ] Enhanced output formatting
- [ ] Better error messages

### Phase 2: Interactive Features (Week 2)
- [ ] Interactive agent creation
- [ ] Interactive chat mode
- [ ] Training wizard
- [ ] Conversation management

### Phase 3: Advanced Features (Week 3)
- [ ] Role-based command separation
- [ ] Analytics commands
- [ ] Configuration profiles
- [ ] Export/import features

### Phase 4: Polish & Documentation (Week 4)
- [ ] Comprehensive help text
- [ ] Usage examples
- [ ] Tutorial mode
- [ ] Performance optimization

## File Structure

```
knowrithm_cli/
├── commands/
│   ├── admin/          # Admin-specific commands
│   │   ├── users.py
│   │   ├── analytics.py
│   │   └── audit.py
│   ├── superadmin/     # Super admin commands
│   │   ├── companies.py
│   │   ├── analytics.py
│   │   └── system.py
│   ├── agent.py        # Enhanced agent commands
│   ├── conversation.py # Enhanced conversation commands
│   ├── train.py        # New training commands
│   ├── context.py      # Context management
│   └── ...
├── core/
│   ├── context.py      # Context manager
│   ├── cache.py        # ID/name caching
│   ├── formatters.py   # Output formatting
│   └── interactive.py  # Interactive prompts
├── utils/
│   ├── name_resolver.py # Name to ID resolution
│   ├── validators.py    # Input validation
│   └── helpers.py       # Common utilities
└── ...
```

## Command Examples

### Agent Management
```bash
# Create agent interactively
knowrithm agent create-interactive

# Create agent with name
knowrithm agent create --name "Support Bot" --description "Customer support"

# List agents (formatted table)
knowrithm agent list --format table

# Get agent by name
knowrithm agent get "Support Bot"

# Set active agent
knowrithm context set agent "Support Bot"

# Chat with agent
knowrithm agent chat "Support Bot"
# or use context
knowrithm agent chat  # uses active agent
```

### Training
```bash
# Upload documents
knowrithm train upload docs/*.pdf --agent "Support Bot"

# Add website
knowrithm train url https://example.com --agent "Support Bot" --crawl

# Connect database
knowrithm train database connect --agent "Support Bot"

# Check training status
knowrithm train status --agent "Support Bot"
```

### Conversations
```bash
# Start new conversation
knowrithm conversation start "Support Bot"

# Continue last conversation
knowrithm conversation continue

# Interactive chat
knowrithm chat  # uses active agent and conversation

# List conversations
knowrithm conversation list --agent "Support Bot" --format table

# Export conversation
knowrithm conversation export <id> --format markdown
```

### Context Management
```bash
# Show current context
knowrithm context show

# Set active agent
knowrithm context set agent "Support Bot"

# Set active conversation
knowrithm context set conversation "Latest Support Chat"

# Clear context
knowrithm context clear
```

### Admin Commands
```bash
# List users
knowrithm admin users list --role admin --status active

# Add user
knowrithm admin users add --email user@example.com --role user

# View analytics
knowrithm admin analytics dashboard --days 30

# Audit log
knowrithm admin audit-log --entity-type agent --limit 50
```

### Super Admin Commands
```bash
# List companies
knowrithm superadmin companies list --format table

# Company analytics
knowrithm superadmin analytics user-engagement --company-id <id>

# System health
knowrithm superadmin system health

# System metrics
knowrithm superadmin system metrics --interval day
```

## Technical Implementation Details

### Name Resolution System
```python
class NameResolver:
    """Resolve names to IDs with caching and fuzzy matching."""
    
    def resolve_agent(self, name: str) -> str:
        # Check cache first
        # Query API if not cached
        # Use fuzzy matching if exact match fails
        # Return UUID
        
    def resolve_conversation(self, name: str) -> str:
        # Similar logic for conversations
```

### Context Manager
```python
class Context:
    """Manage CLI context (active agent, conversation, etc.)."""
    
    def __init__(self):
        self.agent_id = None
        self.agent_name = None
        self.conversation_id = None
        self.organization_id = None
        
    def set_agent(self, name_or_id: str):
        # Resolve and set active agent
        
    def get_agent(self) -> Optional[str]:
        # Return active agent ID
```

### Interactive Prompts
```python
def interactive_agent_creation():
    """Wizard for creating agents."""
    name = click.prompt("Agent name")
    description = click.prompt("Description")
    # ... more prompts
    # Create agent with collected data
```

### Output Formatting
```python
class Formatter:
    """Format output in various formats."""
    
    def format_table(self, data: List[Dict]) -> str:
        # Use rich or tabulate for tables
        
    def format_tree(self, data: Dict) -> str:
        # Tree view for hierarchical data
        
    def format_json(self, data: Any) -> str:
        # Pretty JSON output
```

## Success Metrics

1. **Reduced Command Complexity**: 50% reduction in average command length
2. **Improved Discoverability**: Users can complete tasks without documentation
3. **Error Reduction**: 70% reduction in user errors
4. **Faster Workflows**: 3x faster for common operations
5. **User Satisfaction**: Positive feedback from beta users

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Create test suite for new features
5. Beta testing with select users
6. Documentation and tutorials
7. Production release

