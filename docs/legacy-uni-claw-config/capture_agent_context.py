#!/usr/bin/env python3

import json
import os
from datetime import datetime

def capture_agent_context(agent_name, context_dict):
    """
    Capture and archive an agent's context
    
    :param agent_name: Name of the agent
    :param context_dict: Dictionary containing agent's context
    """
    # Ensure archive directory exists
    archive_dir = "/data/agent_archives"
    os.makedirs(archive_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{archive_dir}/{agent_name.lower()}_context_{timestamp}.json"
    
    # Add metadata
    full_context = {
        "agent_name": agent_name,
        "captured_at": timestamp,
        "context": context_dict
    }
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(full_context, f, indent=2)
    
    print(f"Context for {agent_name} captured to {filename}")
    
    # Update registry
    registry_path = "/data/workspace/AGENT_REGISTRY.md"
    with open(registry_path, 'r') as f:
        registry_content = f.readlines()
    
    # Check if agent already exists
    agent_exists = any(agent_name in line for line in registry_content)
    
    if not agent_exists:
        with open(registry_path, 'a') as f:
            f.write(f"\n5. {agent_name}\n   - Last Archived: {timestamp}\n")
    
    return filename

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python capture_agent_context.py <agent_name> <context_key1> <context_value1> [<context_key2> <context_value2> ...]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    context_dict = {}
    
    # Parse context from command line arguments
    for i in range(2, len(sys.argv), 2):
        if i+1 < len(sys.argv):
            context_dict[sys.argv[i]] = sys.argv[i+1]
    
    capture_agent_context(agent_name, context_dict)