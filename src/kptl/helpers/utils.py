"""
Utility functions.
"""

import argparse
import base64
import re

def read_file_content(file_path: str) -> str:
    """Read the content of a file and return it as a string."""
    with open(file_path, 'rb') as f:
        return f.read()

def encode_content(content) -> str:
    """Encode the given content to a base64 string."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return base64.b64encode(content).decode('utf-8')

def sort_key_for_numbered_files(filename):
    """Generate a sort key for filenames with numeric prefixes."""
    # Extract the numeric parts from the filename
    match = re.match(r"(\d+)(\.\d+)?_", filename)
    if match:
        major = int(match.group(1))  # The number before the dot
        minor = float(match.group(2)) if match.group(2) else 0  # The number after the dot, default to 0
        return (major, minor)
    return (float('inf'),)  # Files without numeric prefixes go at the end

def slugify(title: str) -> str:
    """Convert a title into a slug-friendly format."""
    return re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower().strip().replace(' ', '-')

def is_valid_uuid(uuid: str) -> bool:
    """Check if the given string is a valid UUID."""
    return re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uuid) is not None
