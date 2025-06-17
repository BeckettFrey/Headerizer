# File: src/headerizer/cli.py
import sys
from headerizer.config import load_config
from headerizer.processor import find_and_process_files

def cli():
    use_relative = False
    target_dir = "."
    print_written=False
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            if arg == '--relative':
                use_relative = True
            elif arg == '--print':
                print_written = True
            elif arg == '--help':
                print_help()
                return
        elif arg.startswith('-') and len(arg) > 2:
            # Split grouped flags like -rp into ['-r', '-p']
            for flag in arg[1:]:
                if flag == 'r':
                    use_relative = True
                elif flag == 'p':
                    print_written = True
                elif flag == 'h':
                    print_help()
                    return
        elif arg == '-r':
            use_relative = True
        elif arg == '-p':
            print_written = True
        elif arg == '-h':
            print_help()
            return
        else:
            target_dir = arg

    file_types, default_ignore = load_config()
    print("Starting header insertion...")
    find_and_process_files(
        target_dir,
        file_types,
        use_relative=use_relative,
        default_ignore=default_ignore,
        print_written=print_written
    )

def print_help():
    print("Usage: headerizer [options] [directory]")
    print("\nOptions:")
    print("  -r, --relative     Use paths relative to Git root in headers")
    print("  -p, --print        Print each file that a header was added to")
    print("  -h, --help         Show this help message")

if __name__ == "__main__":
    cli()