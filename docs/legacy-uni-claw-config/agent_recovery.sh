#!/bin/bash

# Simple Agent Recovery Script

REGISTRY_FILE="/data/workspace/AGENT_REGISTRY.md"
ARCHIVE_DIR="/data/agent_archives"

# Function to list known agents
list_agents() {
    echo "Known Agents:"
    grep "^[0-9]\. " "$REGISTRY_FILE" | cut -d. -f2 | cut -d' ' -f2
}

# Function to spawn a previously known agent
spawn_agent() {
    local agent_name="$1"
    
    if [ -z "$agent_name" ]; then
        echo "Please provide an agent name to spawn."
        exit 1
    }
    
    # Check if agent exists in registry
    if ! grep -q "^[0-9]\. $agent_name" "$REGISTRY_FILE"; then
        echo "Agent $agent_name not found in registry."
        exit 1
    }
    
    # Look for archived context
    ARCHIVE_FILE="$ARCHIVE_DIR/${agent_name,,}_context.json"
    
    if [ -f "$ARCHIVE_FILE" ]; then
        echo "Recovering context for $agent_name from archive..."
        # Here you would add logic to actually restore the agent's context
        echo "Archived context found. Restoration logic to be implemented."
    else
        echo "No archived context found for $agent_name."
    fi
}

# Main script logic
case "$1" in
    list)
        list_agents
        ;;
    spawn)
        spawn_agent "$2"
        ;;
    *)
        echo "Usage: $0 {list|spawn} [agent_name]"
        exit 1
        ;;
esac