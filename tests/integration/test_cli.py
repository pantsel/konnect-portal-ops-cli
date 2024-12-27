"""
Integration tests for the CLI.
"""

import subprocess
from typing import Generator, List
import pytest
import yaml
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
DOCS_PATH: str = "examples/docs/httpbin"
DOCS_EMPTY_PATH: str = "examples/docs_empty"
PORTAL_DEV: str = "dev_portal"
PORTAL_PROD: str = "prod_portal"
PRODUCT_NAME: str = "HTTPBin API"

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

def test_simple_state(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    """Test simple state."""
    state = tmp_path / "state.yaml"
    state.write_text(f"""
    _version: 1.0.0
    info:
        name: {PRODUCT_NAME}
        description: A simple API Product for requests to /httpbin
    documents:
        sync: true
        dir: examples/docs/httpbin
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
    """)

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

    # print("#################################### dev_portal_product_version_v1")
    # print(dev_portal_product_version_v1)

    # print("#################################### prod_portal_product_version_v1")
    # print(prod_portal_product_version_v1)
    
    assert dev_portal_product_version_v1["publish_status"] == "published"
    assert dev_portal_product_version_v2["publish_status"] == "published"

    assert prod_portal_product_version_v1["publish_status"] == "published"
    assert prod_portal_product_version_v2["publish_status"] == "published"

    # Assert product version deprecation
    # assert dev_portal_product_version_v1["deprecated"] is False
    # assert prod_portal_product_version_v1["deprecated"] is True

# def test_missing_gateway_service_args(sync_command: List[str]) -> None:
#     """Test missing gateway service arguments."""
#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--gateway-service-id", "test-id" # only --gateway-service-id is provided
#         ],
#         capture_output=True,
#         text=True,
#         check=False
#     )
#     assert result.returncode != 0
#     assert "the following arguments are required" in result.stderr

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--gateway-service-control-plane-id", "test-id" # only --gateway-service-control-plane-id is provided
#         ],
#         capture_output=True,
#         text=True,
#         check=False
#     )
#     assert result.returncode != 0
#     assert "the following arguments are required" in result.stderr

# def test_invalid_spec(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test invalid OpenAPI spec."""
#     spec = tmp_path / "oas.yaml"
#     spec.write_text("""
#     openapi: 3.0.0
#     info:
#       title: Sample API
#       version: 1.0.0
#     paths: {}
#     """)

#     result = subprocess.run(
#         sync_command + [
#             spec,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=False
#     )
#     assert result.returncode == 1

# def test_publish_product_v1_to_dev_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test publishing product v1 to dev portal."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     spec_v1_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert spec_v1_version["publish_status"] == "published"

#     konnect.check_product_document_structure(api_product["id"])

# def test_link_product_v1_to_gateway_service(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test linking product v1 to gateway service."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--gateway-service-id", "test-id",
#             "--gateway-service-control-plane-id", "test-control-plane-id"
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     assert "gateway_service" in product_version
#     assert product_version["gateway_service"]["id"] == "test-id"
#     assert product_version["gateway_service"]["control_plane_id"] == "test-control-plane-id"

# def test_unlink_product_v1_from_gateway_service(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test unlinking product v1 from gateway service."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     assert "gateway_service" not in product_version or product_version["gateway_service"] is None

# def test_publish_product_v1_to_prod_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test publishing product v1 to prod portal."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_PROD,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     spec_v1_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert spec_v1_version["publish_status"] == "published"

#     konnect.check_product_document_structure(api_product["id"])

# def test_publish_product_v2_to_dev_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test publishing product v2 to dev portal."""
#     spec_v2 = tmp_path / "oas.yaml"
#     spec_v2.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

#     spec_v2_content = yaml.safe_load(spec_v2.read_text())
#     spec_v2_version = spec_v2_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V2_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v2_version)
#     spec_v2_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert spec_v2_version["publish_status"] == "published"

#     konnect.check_product_document_structure(api_product["id"])

# def test_publish_product_v2_to_prod_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test publishing product v2 to prod portal."""
#     spec_v2 = tmp_path / "oas.yaml"
#     spec_v2.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

#     spec_v2_content = yaml.safe_load(spec_v2.read_text())
#     spec_v2_version = spec_v2_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V2_PATH,
#             "--documents-dir", DOCS_PATH,
#             "--konnect-portal", PORTAL_PROD,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
#     assert portal["id"] in api_product["portal_ids"]

#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v2_version)
#     spec_v2_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert spec_v2_version["publish_status"] == "published"

#     konnect.check_product_document_structure(api_product["id"])

# def test_deprecate_product_v1_from_prod_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test deprecating product v1 from prod portal."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--konnect-portal", PORTAL_PROD,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--deprecate"
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )

#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     portal_product_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert portal_product_version["deprecated"] is True

# def test_unpublish_product_v1_from_prod_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test unpublishing product v1 from prod portal."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     spec_v1_content = yaml.safe_load(spec_v1.read_text())
#     spec_v1_version = spec_v1_content.get("info", {}).get("version")

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--konnect-portal", PORTAL_PROD,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--unpublish", "version"
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )

#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
#     product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
#     portal_product_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
#     assert portal_product_version["publish_status"] == "unpublished"

# def test_unpublish_product_from_dev_portal(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test unpublishing product from dev portal."""
#     spec_v1 = tmp_path / "oas.yaml"
#     spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V1_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--unpublish", "product"
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )

#     assert result.returncode == 0

#     portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
#     assert portal["id"] not in api_product["portal_ids"]

# def test_delete_api_product_documents(sync_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
#     """Test deleting API product documents."""
#     spec = tmp_path / "oas.yaml"
#     spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

#     result = subprocess.run(
#         sync_command + [
#             SPEC_V2_PATH,
#             "--konnect-portal", PORTAL_DEV,
#             "--documents-dir", DOCS_EMPTY_PATH,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL
#         ],
#         capture_output=True,
#         text=True,
#         check=True
#     )

#     response = requests.get(f"{TEST_SERVER_URL}/v2/api-products", timeout=10)
#     api_product_id = response.json()["data"][0]["id"]

#     response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{api_product_id}/documents", timeout=10)
#     assert len(response.json()["data"]) == 0

#     assert result.returncode == 0

def test_delete_api_product(delete_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
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
