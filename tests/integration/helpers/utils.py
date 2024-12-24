import time
import requests
import yaml
from typing import Any, Dict

def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def wait_for_the_server_to_start(server_url: str, retries: int = 10) -> None:
    for _ in range(retries):
        try:
            response = requests.get(f"{server_url}/v2/portals")
            if response.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(1)