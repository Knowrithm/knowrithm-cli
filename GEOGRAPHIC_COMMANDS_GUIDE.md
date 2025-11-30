# Quick Reference: Interactive Geographic Commands

## Overview
All geographic data commands now support interactive menu selection when called without arguments.

## Commands

### 1. View All Countries
```bash
knowrithm system countries
```
Lists all available countries in table format.

### 2. View a Specific Country
```bash
# Interactive mode - shows menu
knowrithm system country

# Direct mode - requires country ID
knowrithm system country 123
```

### 3. View States in a Country
```bash
# Interactive mode - shows country selection menu first
knowrithm system states

# Direct mode - requires country ID
knowrithm system states 123
```

### 4. View a Specific State
```bash
# Interactive mode - shows country → state selection menus
knowrithm system state

# Direct mode - requires state ID
knowrithm system state 456
```

### 5. View Cities in a State
```bash
# Interactive mode - shows country → state selection menus
knowrithm system cities

# Direct mode - requires state ID
knowrithm system cities 456
```

### 6. View a Specific City
```bash
# Interactive mode - shows country → state → city selection menus
knowrithm system city

# Direct mode - requires city ID
knowrithm system city 789
```

## Interactive Flow Examples

### Example 1: Finding a City
```bash
$ knowrithm system city

🗺️  First, select a state:

🌍 First, select a country:
? Select country (Use arrow keys)
 » United States (US)
   Canada (CA)
   United Kingdom (GB)
   ...

? Select state (Use arrow keys)
 » California (CA)
   Texas (TX)
   New York (NY)
   ...

🏙️  Select a city to view:
? Select city (Use arrow keys)
 » San Francisco
   Los Angeles
   San Diego
   ...

[City details displayed in table format]
```

### Example 2: Listing States
```bash
$ knowrithm system states

🌍 Select a country to view its states:
? Select country (Use arrow keys)
 » United States (US)
   Canada (CA)
   ...

[Table of all states in selected country]
```

## Output Formats

All commands support multiple output formats using the `--format` option:

```bash
knowrithm system country --format json
knowrithm system states --format yaml
knowrithm system cities --format csv
knowrithm system city --format table  # default
```

## Tips

1. **Use arrow keys** to navigate menus
2. **Press Enter** to select
3. **Use Ctrl+C** to cancel at any time
4. **Combine with format options** for different output styles
5. **Use direct IDs** for scripting/automation

## Navigation Hierarchy

```
Countries (List all)
    ↓
Country (Select one)
    ↓
States (List for country)
    ↓
State (Select one)
    ↓
Cities (List for state)
    ↓
City (Select one)
```

## Authentication

Most geographic commands require authentication. Use the `--auth` option:

```bash
knowrithm system country --auth jwt
knowrithm system country --auth api-key
knowrithm system country --auth auto  # default
```
