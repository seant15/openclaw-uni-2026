#!/usr/bin/env python3
"""
Google Ads Configuration Setup
Creates YAML config file from environment variables
"""

import os
import yaml

config = {
    'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', ''),
    'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID', ''),
    'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET', ''),
    'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN', ''),
    'login_customer_id': os.getenv('GOOGLE_ADS_CUSTOMER_ID', '').replace('-', '') if os.getenv('GOOGLE_ADS_CUSTOMER_ID') else None,
    'use_proto_plus': True,
}

# Remove None values
config = {k: v for k, v in config.items() if v is not None}

# Write to YAML
config_path = '/data/workspace/config/google-ads.yaml'
os.makedirs(os.path.dirname(config_path), exist_ok=True)

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print(f"✓ Google Ads config saved to: {config_path}")
print("Contents:")
for key, value in config.items():
    if 'token' in key.lower() or 'secret' in key.lower():
        print(f"  {key}: {'*' * 10}...")
    else:
        print(f"  {key}: {value}")
