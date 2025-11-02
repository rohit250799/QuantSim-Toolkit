import sys
import os
from pathlib import Path

def setup_root(marker_filename: str = "pyproject.toml") -> str:
    """
    Locate and add the project root (containing marker_filename) to sys.path[0].
    Returns the root path string.
    Raises RuntimeError if not found
    """

    # Locate project root by looking upward until pyproject.toml is found 
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent /  marker_filename).exists():
            root_path = parent
            break

    else:
        raise RuntimeError(f"Project root not found (no {marker_filename} upward from {current})") 
        
    #Add root to sys.path
    root_str = str(root_path)
    if sys.path[0] != root_str:
        sys.path.insert(0, root_str)

    #exposing for subprocesses if necessary later
    os.environ.setdefault("PROJECT_ROOT", root_str)
    return root_str
