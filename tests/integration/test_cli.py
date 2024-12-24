import subprocess
import pytest
from src.kptl import __version__
import yaml
import time
import requests
from src.kptl.helpers.api_product_documents import generate_title_and_slug
import os
import re

# ==========================================
# Constants
# ==========================================
SPEC_V1_PATH = "examples/oasv1.yaml"
SPEC_V2_PATH = "examples/oasv2.yaml"
TEST_SERVER_URL = "http://localhost:8080"
DOCS_PATH = "examples/docs"
DOCS_EMPTY_PATH = "examples/docs_empty"
PORTAL_1 = "test-portal"

# ==========================================
# Helper Functions
# ==========================================
def load_openapi_spec(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def wait_for_the_server_to_start(retries=10):
    for _ in range(retries):
        try:
            response = requests.get(f"{TEST_SERVER_URL}/v2/portals")
            if response.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(1)

# ==========================================
# Fixtures
# ==========================================
@pytest.fixture(scope="session", autouse=True)
def start_mock_server():
    # Start the mock server
    server_process = subprocess.Popen(["python3", "mock/app.py"])
    wait_for_the_server_to_start()

    yield

    # Teardown the mock server
    server_process.terminate()
    server_process.wait()

@pytest.fixture
def cli_command():
    return ["python3", "src/kptl/main.py"]

# ==========================================
# Tests
# ==========================================
def test_version(cli_command):
    result = subprocess.run(cli_command + ["--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert __version__ in result.stdout

def test_help(cli_command):
    result = subprocess.run(cli_command + ["--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: main.py" in result.stdout

def test_missing_required_args(cli_command):
    result = subprocess.run(cli_command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr

def test_invalid_oas_spec(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text("""
    openapi: 3.0.0
    info:
      title: Sample API
      version: 1.0.0
    paths: {}
    """)

    result = subprocess.run(cli_command + ["--oas-spec", str(oas_spec), "--konnect-portal-name", PORTAL_1, "--konnect-token", "test-token", "--konnect-url", "https://example.com"], capture_output=True, text=True)
    assert result.returncode == 1

def test_valid_oas_spec(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_1,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    def check_document_status(documents, slug, expected_status):
        for document in documents:
            if document["slug"] == slug:
                assert document["status"] == expected_status

    def check_parent_document_id(documents, slug, parent_slug):
        parent_id = next(doc["id"] for doc in documents if doc["slug"] == parent_slug)
        for document in documents:
            if document["slug"] == slug:
                assert document["parent_document_id"] == parent_id

    def test_document_structure():

        # Get the API Product ID
        response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
        api_product_id = response.json()["data"][0]["id"]

        # Get the API Product Documents
        response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{api_product_id}/documents")
        documents = response.json()["data"]

        # Read filenames from examples/docs and generate the expected slugs list
        filenames = os.listdir(DOCS_PATH)
        expected_slugs = []
        for filename in filenames:
            # ref: src/kptl/helpers/api_product_documents.py@parse_directory
            match = re.match(r'^(\d+)(?:\.(\d+))?', os.path.basename(filename))
            expected_slugs = expected_slugs + [generate_title_and_slug(filename, match)[1]]

        document_slugs = [doc["slug"] for doc in documents]

        assert len(documents) == len(filenames)

        for expected_slug in expected_slugs:
            assert expected_slug in document_slugs

        check_document_status(documents, "0-5-api-philosophy", "unpublished")
        check_document_status(documents, "httpbin-api-documentation", "unpublished")

        check_parent_document_id(documents, "0-1-key-features", "0-introduction")
        check_parent_document_id(documents, "0-2-use-cases", "0-introduction")
        check_parent_document_id(documents, "0-3-architecture-overview", "0-introduction")
        check_parent_document_id(documents, "0-4-supported-environments", "0-introduction")
        check_parent_document_id(documents, "0-5-api-philosophy", "0-introduction")
        check_parent_document_id(documents, "1-1-child-of-authentication", "1-authentication")

    test_document_structure()

def test_deprecate_portal_product_version(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V1_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", PORTAL_1,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--deprecate"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{TEST_SERVER_URL}/v2/portals")
    portal_id = next(portal["id"] for portal in response.json()["data"] if portal["name"] == PORTAL_1)

    response = requests.get(f"{TEST_SERVER_URL}/v2/portals/{portal_id}/product-versions")
    assert response.json()["data"][0]["deprecated"] == True

    assert result.returncode == 0

def test_add_new_api_product_version(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--docs", DOCS_PATH,
            "--konnect-portal-name", PORTAL_1,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL
        ],
        capture_output=True,
        text=True
    )

    # Get the Portal by fetching th eportsal by name
    response = requests.get(f"{TEST_SERVER_URL}/v2/portals")
    portal_id = next(portal["id"] for portal in response.json()["data"] if portal["name"] == PORTAL_1)

    # Get the API Product ID
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
    api_product_id = response.json()["data"][0]["id"]

    # Get the API Product Versions
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{api_product_id}/product-versions")
    assert len(response.json()["data"]) == 2

    # Assert both versions are published to the portal
    response = requests.get(f"{TEST_SERVER_URL}/v2/portals/{portal_id}/product-versions")
    assert len(response.json()["data"]) == 2
    assert all([pv["publish_status"] == "published" for pv in response.json()["data"]])

    assert result.returncode == 0

def test_delete_api_product_documents(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", PORTAL_1,
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

def test_unpublish_api_product(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", PORTAL_1,
            "--konnect-token", "test-token",
            "--konnect-url", TEST_SERVER_URL,
            "--unpublish", "product"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
    assert response.json()["data"][0]["portal_ids"] == []

    assert result.returncode == 0

def test_delete_api_product(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", PORTAL_1,
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
