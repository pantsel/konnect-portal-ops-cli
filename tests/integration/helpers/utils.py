"""
Utility functions for integration tests.
"""

import time
from typing import Any, Dict
import requests
import yaml

def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    """
    Load an OpenAPI specification from a YAML file.

    Args:
        file_path (str): The path to the OpenAPI spec file.

    Returns:
        Dict[str, Any]: The loaded OpenAPI spec as a dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def wait_for_the_server_to_start(server_url: str, retries: int = 10) -> None:
    """
    Wait for the server to start by making repeated requests.

    Args:
        server_url (str): The URL of the server to check.
        retries (int): The number of times to retry the request.

    Raises:
        RuntimeError: If the server does not start within the given retries.
    """
    for _ in range(retries):
        try:
            response = requests.get(f"{server_url}/v2/portals", timeout=5)
            if response.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(1)
    else:
        raise RuntimeError(f"Server at {server_url} did not start within {retries} retries.")