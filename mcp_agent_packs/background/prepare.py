
import os
from pathlib import Path


def prepare():
    # Ensure the mcp-server-filesystem directory exists
    filesystem_dir = Path(os.environ['TEMP']) / 'mcp-server-filesystem'
    filesystem_dir.mkdir(parents=True, exist_ok=True)

    # Print the path for verification
    print(f"Prepared filesystem directory at: {filesystem_dir}")


if __name__ == "__main__":
    prepare()