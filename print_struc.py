import os

def print_directory_structure(start_path='.'):
    """Recursively prints the structure of directories and files from the given start path."""
    for root, dirs, files in os.walk(start_path):
        # Determine the current level by counting the directory separators
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

if __name__ == "__main__":
    # By default, it prints the structure of the current directory
    print_directory_structure(".")
