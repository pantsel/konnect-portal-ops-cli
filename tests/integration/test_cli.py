"""
Integration tests for the CLI.
"""

import subprocess
from typing import Generator, List
import pytest
import requests
from src.kptl import __version__
from .helpers.utils import load_openapi_spec, wait_for_the_server_to_start
from .helpers.konnect import KonnectHelper

# ==========================================
# Constants
# ==========================================
SPEC_V1_PATH: str = "examples/api-specs/v1/httpbin.yaml"
SPEC_V2_PATH: str = "examples/api-specs/v2/httpbin.yaml"
TEST_SERVER_URL: str = "http://localhost:8080"
DOCS_PATH: str = "examples/products/httpbin/docs"
DOCS_EMPTY_PATH: str = "examples/docs_empty"
PORTAL_DEV: str = "dev_portal"
PORTAL_PROD: str = "prod_portal"
PRODUCT_NAME: str = "HTTPBin API"
TEST_STATE = f"""
    _version: 1.0.0
    info:
        name: {PRODUCT_NAME}
        description: A simple API Product for requests to /httpbin
    documents:
        sync: true
        dir: {DOCS_PATH}
    portals:
        - portal_name: {PORTAL_DEV}
        - portal_name: {PORTAL_PROD}
    versions:
        - spec: {SPEC_V1_PATH}
          gateway_service:
            id: test-id
            control_plane_id: test-control-plane-id
          portals:
            - portal_name: {PORTAL_DEV}
            - portal_name: {PORTAL_PROD}
              publish_status: published  
              deprecated: true
        - spec: {SPEC_V2_PATH}
          portals:
            - portal_name: {PORTAL_DEV}
            - portal_name: {PORTAL_PROD}
    """

konnect: KonnectHelper = KonnectHelper(TEST_SERVER_URL, DOCS_PATH)

# ==========================================
# Fixtures
# ==========================================
@pytest.fixture(scope="session", autouse=True)
def start_mock_server() -> Generator[None, None, None]:
    """Fixture to start and stop the mock server."""
    server_process = subprocess.Popen(["python3", "mock/app.py"])
    wait_for_the_server_to_start(TEST_SERVER_URL)

    yield

    server_process.terminate()
    server_process.wait()

@pytest.fixture
def cli_command() -> List[str]:
    """Fixture to return the CLI command."""
    return ["python3", "src/kptl/main.py"]

@pytest.fixture
def sync_command(cli_command: List[str]) -> List[str]:
    """Fixture to return the Sync CLI command."""
    return cli_command + ["sync"]

@pytest.fixture
def delete_command(cli_command: List[str]) -> List[str]:
    """Fixture to return the Delete CLI command."""
    return cli_command + ["delete"]

# ==========================================
# Tests
# ==========================================
def test_version(cli_command: List[str]) -> None:
    """Test the version command."""
    result = subprocess.run(cli_command + ["--version"], capture_output=True, text=True, check=True)
    assert result.returncode == 0
    assert __version__ in result.stdout

def test_help(cli_command: List[str]) -> None:
    """Test the help command."""
    result = subprocess.run(cli_command + ["--help"], capture_output=True, text=True, check=True)
    assert result.returncode == 0
    assert "usage: main.py" in result.stdout

def test_missing_required_args(sync_command: List[str]) -> None:
    """Test missing required arguments."""
    result = subprocess.run(sync_command, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr

def test_explain(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    """Test the explain command."""
    state = tmp_path / "state.yaml"
    state.write_text(TEST_STATE)
    result = subprocess.run(cli_command + ["explain", tmp_path / "state.yaml"], capture_output=True, text=True, check=True)
    assert result.returncode == 0

