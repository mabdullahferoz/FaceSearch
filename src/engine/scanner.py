import os
from pathlib import Path

def get_image_paths(root_dir):
    """
    Generator that yields paths to image files.
    Optimized for memory efficiency in large datasets.
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    for path in Path(root_dir).rglob('*'):
        if path.suffix.lower() in valid_extensions:
            yield str(path)
            