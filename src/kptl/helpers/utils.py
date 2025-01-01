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


def validate_state_file(state: dict) -> bool:
    """ Validate the state file. """

    logger = Logger()
    errors = []

    # Validate info
    if 'info' not in state or 'name' not in state['info']:
        errors.append("Error: 'info' must be defined and must contain 'name'.")

    # Validate documents
    if 'documents' in state:
        documents = state['documents']
        if documents.get('sync') and 'dir' not in documents:
            errors.append(
                "Error: 'documents.dir' must be defined if 'documents.sync' is true.")

    # Validate portals
    if 'portals' in state:
        for portal in state['portals']:
            if 'portal_name' not in portal and 'portal_id' not in portal:
                errors.append(
                    "Error: Each portal must have either 'portal_name' or 'portal_id' defined.")

    # Validate versions
    if 'versions' in state:
        for version in state['versions']:
            if 'spec' not in version:
                errors.append(f"Error: Version '{version.get(
                    'name', 'unknown')}' must have 'spec' defined.")

            if 'portals' in version:
                for portal in version['portals']:
                    if 'portal_name' not in portal and 'portal_id' not in portal:
                        errors.append(f"Error: Each portal in version '{version.get(
                            'name', 'unknown')}' must have either 'portal_name' or 'portal_id' defined.")

            if 'gateway_service' in version:
                gateway_service = version['gateway_service']
                if gateway_service['id'] is not None or gateway_service['control_plane_id'] is not None:
                    if 'id' not in gateway_service or 'control_plane_id' not in gateway_service:
                        errors.append(f"Error: Gateway service in version '{version.get(
                            'name', 'unknown')}' must have both 'id' and 'control_plane_id' defined.")
                    if not is_valid_uuid(gateway_service['id']) or not is_valid_uuid(gateway_service['control_plane_id']):
                        errors.append(f"Error: 'id' and 'control_plane_id' in gateway service of version '{
                                      version.get('name', 'unknown')}' must be valid UUIDs.")

            if 'portals' in version:
                for portal in version['portals']:
                    if 'auth_strategies' in portal:
                        auth_strategies = portal['auth_strategies']
                        if not isinstance(auth_strategies, list):
                            errors.append(f"Error: 'auth_strategies' in portal '{portal.get(
                                'portal_name', 'unknown')}' of version '{version.get('name', 'unknown')}' must be a list.")
                        for strategy in auth_strategies:
                            if 'id' not in strategy:
                                errors.append(f"Error: Each 'auth_strategy' in portal '{portal.get(
                                    'portal_name', 'unknown')}' of version '{version.get('name', 'unknown')}' must have an 'id'.")

    if errors:
        logger.error("State validation errors:\n - %s", "\n - ".join(errors))
        return False

    return True
