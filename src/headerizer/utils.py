# File: src/headerizer/utils.py
import subprocess
import fnmatch
from pathlib import Path

def find_git_root(start_path="."):
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, cwd=start_path, check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    
def load_headerignore(root_dir, extra_patterns=None):
    headerignore_path = root_dir / '.headerignore'
    patterns = extra_patterns or []

    if headerignore_path.exists():
        try:
            with open(headerignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .headerignore: {e}")

    return patterns

def should_ignore(file_path, root_dir, ignore_patterns):
    if not ignore_patterns:
        return False

    try:
        rel_path = file_path.relative_to(root_dir)
        rel_path_str = str(rel_path)
        path_parts = rel_path.parts

        for pattern in ignore_patterns:
            if fnmatch.fnmatch(rel_path_str, pattern):
                return True
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i+1])
                if fnmatch.fnmatch(partial_path, pattern) or fnmatch.fnmatch(path_parts[i], pattern):
                    return True

    except ValueError:
        return False

    return False

def get_file_type_config(file_path, file_types):
    suffix = file_path.suffix.lower()
    for config in file_types.values():
        if suffix in config['extensions']:
            return config
    return None
