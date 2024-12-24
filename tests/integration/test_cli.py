import subprocess
import pytest
from src.kptl import __version__
from .helpers.utils import load_openapi_spec, wait_for_the_server_to_start
import yaml
import requests
from .helpers.konnect import KonnectHelper
from typing import Generator, List

# ==========================================
# Constants
# ==========================================
SPEC_V1_PATH: str = "examples/oasv1.yaml"
SPEC_V2_PATH: str = "examples/oasv2.yaml"
TEST_SERVER_URL: str = "http://localhost:8080"
DOCS_PATH: str = "examples/docs"
DOCS_EMPTY_PATH: str = "examples/docs_empty"
PORTAL_DEV: str = "dev_portal"
PORTAL_PROD: str = "prod_portal"

konnect: KonnectHelper = KonnectHelper(TEST_SERVER_URL, DOCS_PATH)

# ==========================================
# Fixtures
# ==========================================
@pytest.fixture(scope="session", autouse=True)
def start_mock_server() -> Generator[None, None, None]:
    # Start the mock server
    server_process = subprocess.Popen(["python3", "mock/app.py"])
    wait_for_the_server_to_start(TEST_SERVER_URL)

    yield

    # Teardown the mock server
    server_process.terminate()
    server_process.wait()

@pytest.fixture
def cli_command() -> List[str]:
    return ["python3", "src/kptl/main.py"]

# ==========================================
# Tests
# ==========================================
def test_version(cli_command: List[str]) -> None:
    result = subprocess.run(cli_command + ["--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert __version__ in result.stdout

def test_help(cli_command: List[str]) -> None:
    result = subprocess.run(cli_command + ["--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: main.py" in result.stdout

def test_missing_required_args(cli_command: List[str]) -> None:
    result = subprocess.run(cli_command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr

def test_invalid_spec(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec = tmp_path / "oas.yaml"
    spec.write_text("""
    openapi: 3.0.0
    info:
      title: Sample API
      version: 1.0.0
    paths: {}
    """)

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec),
            "--konnect-portal-name", PORTAL_DEV,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1

def test_publish_product_v1_to_dev_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v1 = tmp_path / "oas.yaml"
    spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    spec_v1_content = yaml.safe_load(spec_v1.read_text())
    spec_v1_version = spec_v1_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v1),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_DEV,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # Assert product and product version are published to the dev portal
    portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
    assert portal["id"] in api_product["portal_ids"]

    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
    spec_v1_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v1_version["publish_status"] == "published"

    konnect.check_product_document_structure(api_product["id"])

def test_publish_product_v1_to_prod_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v1 = tmp_path / "oas.yaml"
    spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    spec_v1_content = yaml.safe_load(spec_v1.read_text())
    spec_v1_version = spec_v1_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v1),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_PROD,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # Assert product and product version are published to the prod portal
    portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
    assert portal["id"] in api_product["portal_ids"]

    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
    spec_v1_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v1_version["publish_status"] == "published"

    konnect.check_product_document_structure(api_product["id"])

def test_publish_product_v2_to_dev_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v2 = tmp_path / "oas.yaml"
    spec_v2.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    spec_v2_content = yaml.safe_load(spec_v2.read_text())
    spec_v2_version = spec_v2_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v2),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_DEV,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # Assert product and product version are published to the dev portal
    portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
    assert portal["id"] in api_product["portal_ids"]

    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v2_version)
    spec_v2_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v2_version["publish_status"] == "published"

    konnect.check_product_document_structure(api_product["id"])

def test_publish_product_v2_to_prod_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v2 = tmp_path / "oas.yaml"
    spec_v2.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    spec_v2_content = yaml.safe_load(spec_v2.read_text())
    spec_v2_version = spec_v2_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v2),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_PROD,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # Assert product and product version are published to the prod portal
    portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
    assert portal["id"] in api_product["portal_ids"]

    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v2_version)
    spec_v2_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v2_version["publish_status"] == "published"

    konnect.check_product_document_structure(api_product["id"])

def test_deprecate_product_v1_from_prod_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v1 = tmp_path / "oas.yaml"
    spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    spec_v1_content = yaml.safe_load(spec_v1.read_text())
    spec_v1_version = spec_v1_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v1),
            "--konnect-portal-name", PORTAL_PROD,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--deprecate"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
    portal_product_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert portal_product_version["deprecated"] == True

def test_unpublish_product_v1_from_prod_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v1 = tmp_path / "oas.yaml"
    spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    spec_v1_content = yaml.safe_load(spec_v1.read_text())
    spec_v1_version = spec_v1_content.get("info", {}).get("version")

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v1),
            "--konnect-portal-name", PORTAL_PROD,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--unpublish", "version"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    portal, api_product = konnect.get_portal_and_product(PORTAL_PROD)
    product_version = konnect.get_api_product_version_by_name(api_product["id"], spec_v1_version)
    portal_product_version = konnect.get_portal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert portal_product_version["publish_status"] == "unpublished"

def test_unpublish_product_from_dev_portal(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec_v1 = tmp_path / "oas.yaml"
    spec_v1.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec_v1),
            "--konnect-portal-name", PORTAL_DEV,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--unpublish", "product"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    portal, api_product = konnect.get_portal_and_product(PORTAL_DEV)
    assert portal["id"] not in api_product["portal_ids"]

def test_delete_api_product_documents(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec = tmp_path / "oas.yaml"
    spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec),
            "--konnect-portal-name", PORTAL_DEV,
            "--docs", DOCS_EMPTY_PATH,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )

    # Get the API Product ID
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
    api_product_id = response.json()["data"][0]["id"]

    # Get the API Product Documents
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{api_product_id}/documents")
    assert len(response.json()["data"]) == 0

    assert result.returncode == 0

def test_delete_api_product(cli_command: List[str], tmp_path: pytest.TempPathFactory) -> None:
    spec = tmp_path / "oas.yaml"
    spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(spec),
            "--konnect-portal-name", PORTAL_DEV,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--delete", "--yes"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
    assert len(response.json()["data"]) == 0

    assert result.returncode == 0
