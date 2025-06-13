from pathlib import Path
from utils import load_headerignore, should_ignore, get_file_type_config, find_git_root

def add_header_to_file(file_path, file_types, header_path, comment_prefix):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.splitlines()
        new_header = f"{comment_prefix}File: {header_path}"

        # Check for an existing header in the first 3 lines
        header_line_index = next(
            (i for i, line in enumerate(lines[:3]) if "File:" in line), None
        )

        if header_line_index is not None:
            lines[header_line_index] = new_header
        else:
            lines.insert(0, new_header)

        new_content = "\n".join(lines) + ("\n" if content.endswith("\n") else "")

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return "written"
        else:
            return "skipped"

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return "error"

def find_and_process_files(
    root_dir,
    file_types,
    use_relative=False,
    default_ignore=None,
    print_written=False
):
    root_path = Path(root_dir).resolve()
    if not root_path.exists():
        print(f"Error: {root_path} doesn't exist.")
        return

    git_root = find_git_root(root_path) if use_relative else None
    all_extensions = [ext for config in file_types.values() for ext in config['extensions']]
    ignore_patterns = load_headerignore(root_path, extra_patterns=default_ignore)

    seen = set()
    files = []
    for ext in all_extensions:
        for p in root_path.rglob(f'*{ext}'):
            if p not in seen:
                seen.add(p)
                files.append(p)

    target_files = [f for f in files if not should_ignore(f, root_path, ignore_patterns)]

    print(f"Found {len(target_files)} file(s) to process.")
    confirm = input("⚠️  Proceed with header insertion? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Operation canceled.")
        return

    for file_path in target_files:
        config = get_file_type_config(file_path, file_types)
        if not config:
            continue

        # Determine header path (relative or absolute)
        try:
            resolved_path = file_path.resolve()
            if use_relative and git_root:
                header_path = str(resolved_path.relative_to(git_root))
                display_path = header_path
            else:
                header_path = str(resolved_path)
                display_path = str(file_path)
        except ValueError:
            header_path = str(file_path.resolve())
            display_path = str(file_path)

        result = add_header_to_file(
            file_path,
            file_types,
            header_path,
            config['comment_prefix']
        )

        if print_written:
            if result == "written":
                print(f"📝 Wrote header to: {display_path}")
            elif result == "skipped":
                print(f"✅ Already headerized: {display_path}")

