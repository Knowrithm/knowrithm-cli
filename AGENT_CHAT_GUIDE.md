# Agent Chat Feature Guide

## Overview

The Knowrithm CLI now includes a user-friendly interactive chat feature that allows you to have conversations with your AI agents directly from the command line, without needing to manually manage conversations or send JSON payloads.

## Features

### 1. Interactive Agent Selection
When you run `knowrithm agent chat` without specifying an agent, the CLI will:
- Fetch all available agents from your company
- Display them in a numbered list with their status and model information
- Allow you to select one by entering its number

### 2. Direct Agent Chat
You can also specify an agent directly by name or ID:
```bash
knowrithm agent chat "Agent Name"
knowrithm agent chat <agent-id>
```

### 3. Automatic Conversation Management
The CLI automatically:
- Creates a new conversation with the selected agent
- Starts an interactive chat session
- Handles all API communication in the background
- Displays agent responses in real-time

## Usage Examples

### Example 1: Interactive Selection
```bash
knowrithm agent chat
```

**Output:**
```
Fetching agents...

Select an agent to chat with:
  1. Support Bot (Status: active, Model: gpt-4)
  2. Sales Assistant (Status: active, Model: claude-3-sonnet)
  3. Documentation Helper (Status: active, Model: gpt-3.5-turbo)

Enter number: 1

Starting chat with Support Bot...
=== Interactive Chat (Conversation: abc-123-def) ===
Type your messages below. Press Ctrl+C to exit.

You: Hello! How can you help me?
