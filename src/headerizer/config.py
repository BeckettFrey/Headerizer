# File: src/headerizer/config.py
from pathlib import Path
import json
import sys

def load_config():
    config_path = Path(__file__).parent / 'config.json'

    if not config_path.exists():
        print(f"❌ Error: config.json not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return (
                config['file_types'],
                config.get('default_ignore', [])
            )
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error: Invalid config.json: {e}")
        sys.exit(1)
