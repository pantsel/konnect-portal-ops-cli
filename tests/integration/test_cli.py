import subprocess
import pytest
from src.kptl import __version__
import yaml
import time
import requests
from src.kptl.helpers.api_product_documents import generate_title_and_slug
import os
import re
import json

# ==========================================
# Constants
# ==========================================
SPEC_V1_PATH = "examples/oasv1.yaml"
SPEC_V2_PATH = "examples/oasv2.yaml"
TEST_SERVER_URL = "http://localhost:8080"
DOCS_PATH = "examples/docs"
DOCS_EMPTY_PATH = "examples/docs_empty"
PORTAL_DEV = "dev_portal"
PORTAL_PROD = "prod_portal"

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

def check_document_status(documents, slug, expected_status):
    for document in documents:
        if document["slug"] == slug:
            assert document["status"] == expected_status

def check_parent_document_id(documents, slug, parent_slug):
    parent_id = next(doc["id"] for doc in documents if doc["slug"] == parent_slug)
    for document in documents:
        if document["slug"] == slug:
            assert document["parent_document_id"] == parent_id

def check_product_document_structure(product_id):

    # Get the API Product ID
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{product_id}")
    api_product_id = response.json()["id"]

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

def get_protal_product_version_by_product_version_id(portal_id, product_version_id):
    response = requests.get(f"{TEST_SERVER_URL}/v2/portals/{portal_id}/product-versions")
    version = next(pv for pv in response.json()["data"] if pv["product_version_id"] == product_version_id)
    return version

def get_api_product_version_by_name(api_product_id, version):
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products/{api_product_id}/product-versions")
    product_version = next(pv for pv in response.json()["data"] if pv["name"] == version)
    return product_version

def get_portal_and_product(portal_name):
    portal = get_portal_by_name(portal_name)

    api_product = get_api_product()
    return portal,api_product

def get_api_product():
    response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
    api_product = response.json()["data"][0]
    return api_product

def get_portal_by_name(portal_name):
    response = requests.get(f"{TEST_SERVER_URL}/v2/portals")
    portal = next(portal for portal in response.json()["data"] if portal["name"] == portal_name)
    return portal


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

    result = subprocess.run(cli_command + ["--oas-spec", str(oas_spec), "--konnect-portal-name", PORTAL_DEV, "--konnect-token", "test-token", "--konnect-url", "https://example.com"], capture_output=True, text=True)
    assert result.returncode == 1

def test_publish_product_v1_to_dev_portal(cli_command, tmp_path):
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
    portal, api_product = get_portal_and_product(PORTAL_DEV)
    assert portal["id"] in api_product["portal_ids"]

    product_version = get_api_product_version_by_name(api_product["id"], spec_v1_version)
    spec_v1_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v1_version["publish_status"] == "published"

    check_product_document_structure(api_product["id"])

def test_publish_product_v1_to_prod_portal(cli_command, tmp_path):
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
    portal, api_product = get_portal_and_product(PORTAL_PROD)
    assert portal["id"] in api_product["portal_ids"]

    product_version = get_api_product_version_by_name(api_product["id"], spec_v1_version)
    spec_v1_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v1_version["publish_status"] == "published"

    check_product_document_structure(api_product["id"])

def test_publish_product_v2_to_dev_portal(cli_command, tmp_path):
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
    portal, api_product = get_portal_and_product(PORTAL_DEV)
    assert portal["id"] in api_product["portal_ids"]

    product_version = get_api_product_version_by_name(api_product["id"], spec_v2_version)
    spec_v2_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v2_version["publish_status"] == "published"

    check_product_document_structure(api_product["id"])

def test_publish_product_v2_to_prod_portal(cli_command, tmp_path):
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
    portal, api_product = get_portal_and_product(PORTAL_PROD)
    assert portal["id"] in api_product["portal_ids"]

    product_version = get_api_product_version_by_name(api_product["id"], spec_v2_version)
    spec_v2_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert spec_v2_version["publish_status"] == "published"

    check_product_document_structure(api_product["id"])

def test_deprecate_product_v1_from_prod_portal(cli_command, tmp_path):
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

    portal, api_product = get_portal_and_product(PORTAL_PROD)
    product_version = get_api_product_version_by_name(api_product["id"], spec_v1_version)
    portal_product_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert portal_product_version["deprecated"] == True

def test_unpublish_product_v1_from_prod_portal(cli_command, tmp_path):
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

    portal, api_product = get_portal_and_product(PORTAL_PROD)
    product_version = get_api_product_version_by_name(api_product["id"], spec_v1_version)
    portal_product_version = get_protal_product_version_by_product_version_id(portal["id"], product_version["id"])
    assert portal_product_version["publish_status"] == "unpublished"

def test_delete_api_product_documents(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
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

# def test_unpublish_api_product(cli_command, tmp_path):
#     oas_spec = tmp_path / "oas.yaml"
#     oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

#     result = subprocess.run(
#         cli_command + [
#             "--oas-spec", str(oas_spec),
#             "--konnect-portal-name", PORTAL_DEV,
#             "--konnect-token", "test-token",
#             "--konnect-url", TEST_SERVER_URL,
#             "--unpublish", "product"
#         ],
#         capture_output=True,
#         text=True
#     )

#     response = requests.get(f"{TEST_SERVER_URL}/v2/api-products")
#     assert response.json()["data"][0]["portal_ids"] == []

#     assert result.returncode == 0

def test_delete_api_product(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(load_openapi_spec(SPEC_V2_PATH)))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
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
