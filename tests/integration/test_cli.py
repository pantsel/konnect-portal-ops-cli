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
        - name: {PORTAL_DEV}
        - name: {PORTAL_PROD}
    versions:
        - spec: {SPEC_V1_PATH}
          gateway_service:
            id: test-id
            control_plane_id: test-control-plane-id
          portals:
            - name: {PORTAL_DEV}
            - name: {PORTAL_PROD}
              config:
                  publish_status: published  
                  deprecated: true
        - spec: {SPEC_V2_PATH}
          portals:
            - name: {PORTAL_DEV}
            - name: {PORTAL_PROD}
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

def test_sync(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    """Test state."""
    state = tmp_path / "state.yaml"
    state.write_text(TEST_STATE)

    result = subprocess.run(
        sync_command + [
            str(state),
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True,
        check=True
    )
    assert result.returncode == 0

    # Assert product is created
    api_product = konnect.get_api_product_by_name("HTTPBin API")
    assert api_product["name"] == "HTTPBin API"

    # Assert product is published to dev and prod portals
    dev_portal, prod_portal = konnect.get_portal_by_name("dev_portal"), konnect.get_portal_by_name("prod_portal")
    assert dev_portal["id"] in api_product["portal_ids"]
    assert prod_portal["id"] in api_product["portal_ids"]

    # Assert product documents are properly created
    konnect.check_product_document_structure(api_product["id"])

    # Assert product versions are created
    product_version_v1 = konnect.get_api_product_version_by_name(api_product["id"], "1.0.0")
    product_version_v2 = konnect.get_api_product_version_by_name(api_product["id"], "2.0.0")

    assert product_version_v1 is not None
    assert product_version_v2 is not None

    # Assert product versions are linked to gateway service
    assert product_version_v1["gateway_service"]["id"] == "test-id"
    assert product_version_v1["gateway_service"]["control_plane_id"] == "test-control-plane-id"


    # Assert product publish status to dev and prod portals
    dev_portal_product_version_v1 = konnect.get_portal_product_version_by_product_version_id(dev_portal["id"], product_version_v1["id"])
    dev_portal_product_version_v2 = konnect.get_portal_product_version_by_product_version_id(dev_portal["id"], product_version_v2["id"])
    prod_portal_product_version_v1 = konnect.get_portal_product_version_by_product_version_id(prod_portal["id"], product_version_v1["id"])
    prod_portal_product_version_v2 = konnect.get_portal_product_version_by_product_version_id(prod_portal["id"], product_version_v2["id"])

    
    assert dev_portal_product_version_v1["publish_status"] == "published"
    assert dev_portal_product_version_v2["publish_status"] == "published"

    assert prod_portal_product_version_v1["publish_status"] == "published"
    assert prod_portal_product_version_v2["publish_status"] == "published"

    # Assert product version deprecation
    assert dev_portal_product_version_v1["deprecated"] is False
    assert prod_portal_product_version_v1["deprecated"] is True

    
def test_delete_api_product_by_name(delete_command: List[str]) -> None:
    """Test deleting API product."""

    result = subprocess.run(
        delete_command + [
            PRODUCT_NAME,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--yes"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products", timeout=10)
    assert len(response.json()["data"]) == 0

    assert result.returncode == 0

def test_sync_product_conflicts(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    """
        Test sync product conflict. Since the sync command relies on the product name to create or update the product,
        there should be a maximum of one product with the same name in Konnect. If there are multiple products with the same name,
        the sync command should fail.
    """
    state = tmp_path / "state.yaml"
    state.write_text(TEST_STATE)

    konnect.create_api_product({
        "name": PRODUCT_NAME,
        "description": "A simple API Product for requests to /httpbin",
        "portal_ids": []
    })

    result = subprocess.run(
        sync_command + [
            str(state),
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # We're good so far. Only one product with the same name exists so the sync command 
    # will use that product for subsequent operations.
    assert result.returncode == 0

    konnect.create_api_product({
        "name": PRODUCT_NAME,
        "description": "Another simple API Product for requests to /httpbin",
        "portal_ids": []
    })

    all_products = konnect.list_api_products()
    assert len(all_products) == 2
    assert all(p["name"] == PRODUCT_NAME for p in all_products)

    result = subprocess.run(
        sync_command + [
            str(state),
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # The sync command should fail because there are multiple products with the same name
    assert result.returncode == 1

    # Clean up
    for product in all_products:
        konnect.delete_api_product(product["id"])


def test_delete_product_conflicts(sync_command: List[str], delete_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    """Test delete product conflict."""
    state = tmp_path / "state.yaml"
    state.write_text(TEST_STATE)

    result = subprocess.run(
        sync_command + [
            str(state),
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True,
        check=True
    )

    assert result.returncode == 0

    api_product = konnect.get_api_product_by_name(PRODUCT_NAME)

    # Create API product with the same name
    konnect.create_api_product({
        "name": PRODUCT_NAME,
        "description": "A simple API Product for requests to /httpbin"
    })

    result = subprocess.run(
        delete_command + [
            PRODUCT_NAME,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--yes"
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # The deletion should fail because there are multiple products with the same name
    assert result.returncode == 1
    
    # Ensure there are still 2 products available
    all_products = konnect.list_api_products()
    assert len(all_products) == 2

    result = subprocess.run(
        delete_command + [
            api_product["id"],
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--yes"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # The deletion should succeed because the product ID is provided
    assert result.returncode == 0

     # Ensure there's only 1 product available
    all_products = konnect.list_api_products()
    assert len(all_products) == 1

    # Ensure the remaining product is not the one that was deleted
    assert all_products[0]["id"] != api_product["id"]
    
    
