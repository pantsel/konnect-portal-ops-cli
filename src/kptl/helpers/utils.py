"""
Utility functions.
"""

import base64
import re
import sys
import yaml
import os
import json


from kptl.config.logger import Logger
from kptl.helpers.validator import ProductStateValidator


def read_file_content(file_path: str) -> str:
    """Read the content of a file and return it as a string."""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        Logger().error("File not found: %s", file_path)
        sys.exit(1)


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
        minor = float(match.group(2)) if match.group(
            2) else 0  # The number after the dot, default to 0
        return (major, minor)
    return (float('inf'),)  # Files without numeric prefixes go at the end


def slugify(title: str) -> str:
    """Convert a title into a slug-friendly format."""
    return re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower().strip().replace(' ', '-')


def is_valid_uuid(uuid: str) -> bool:
    """Check if the given string is a valid UUID."""
    return re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uuid) is not None


def parse_yaml(file_content: str) -> dict:
    """
    Parse YAML content.
    """
    try:
        return yaml.safe_load(file_content)
    except yaml.YAMLError as e:
        Logger().error("Error parsing YAML content: %s", e)
        sys.exit(1)


def load_state(state_file: str) -> dict:
    """
    Load and parse the state file.
    """
    state_content = read_file_content(state_file)
    state_parsed = parse_yaml(state_content)

    v = ProductStateValidator(state_parsed)

    is_valid, errors = v.validate()
    if not is_valid:
        Logger().error("Invalid state file:")
        print(" - " + "\n - ".join(errors))
        sys.exit(1)
    
    return state_parsed


def load_oas_data(spec_file: str) -> tuple:
    """Load and parse OAS data from a specification file."""
    oas_file = read_file_content(spec_file)
    oas_data = parse_yaml(oas_file)
    oas_data_base64 = encode_content(oas_file)
    return oas_data, oas_data_base64


def read_config_file(config_file: str) -> dict:
    """
    Read the configuration file.
    """
    try:
        config_file = config_file or os.path.join(
            os.getenv("HOME"), ".kptl.config.yaml")
        file = read_file_content(config_file)
        return yaml.safe_load(file)
    except Exception as e:
        Logger().error("Error reading config file: %s", str(e))
        sys.exit(1)


def is_file_path(path: str) -> bool:
    """Check if the given path is a file path."""
    return os.path.isfile(path)
