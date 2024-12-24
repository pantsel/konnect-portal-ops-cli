import subprocess
import pytest
from src.kptl import __version__
import yaml
import time
import requests

# Load OpenAPI Spec
def load_openapi_spec(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

spec_v1 = load_openapi_spec("examples/oasv1.yaml")
spec_v2 = load_openapi_spec("examples/oasv2.yaml")
test_server_url = "http://localhost:8080"

@pytest.fixture(scope="session", autouse=True)
def start_mock_server():
    # Start the mock server
    server_process = subprocess.Popen(["python3", "mock/app.py"])
    # Wait for the server to start
    for _ in range(10):
        try:
            response = requests.get(f"{test_server_url}/v2/portals")
            if response.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(1)

    yield

    # Teardown the mock server
    server_process.terminate()
    server_process.wait()

@pytest.fixture
def cli_command():
    return ["python3", "src/kptl/main.py"]

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

    result = subprocess.run(cli_command + ["--oas-spec", str(oas_spec), "--konnect-portal-name", "test-portal", "--konnect-token", "test-token", "--konnect-url", "https://example.com"], capture_output=True, text=True)
    assert result.returncode == 1

def test_valid_oas_spec(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v1))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--docs", "examples/docs",
            "--konnect-portal-name", "test-portal",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

def test_deprecate_portal_product_version(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v1))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", "test-portal",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}",
            "--deprecate"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{test_server_url}/v2/portals")
    portal_id = response.json()["data"][0]["id"]

    response = requests.get(f"{test_server_url}/v2/portals/{portal_id}/product-versions")
    assert response.json()["data"][0]["deprecated"] == True

    assert result.returncode == 0

def test_add_new_api_product_version(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v2))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--docs", "examples/docs",
            "--konnect-portal-name", "test-portal",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}"
        ],
        capture_output=True,
        text=True
    )

    # Get the API Product ID
    response = requests.get(f"{test_server_url}/v2/api-products")
    api_product_id = response.json()["data"][0]["id"]

    # Get the API Product Versions
    response = requests.get(f"{test_server_url}/v2/api-products/{api_product_id}/product-versions")
    assert len(response.json()["data"]) == 2

    assert result.returncode == 0

def test_delete_api_product_documents(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v2))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", "test-portal",
            "--docs", "examples/docs_empty",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}"
        ],
        capture_output=True,
        text=True
    )

    # Get the API Product ID
    response = requests.get(f"{test_server_url}/v2/api-products")
    api_product_id = response.json()["data"][0]["id"]

    # Get the API Product Documents
    response = requests.get(f"{test_server_url}/v2/api-products/{api_product_id}/documents")
    assert len(response.json()["data"]) == 0

    assert result.returncode == 0

def test_unpublish_api_product(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v2))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", "test-portal",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}",
            "--unpublish", "product"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{test_server_url}/v2/api-products")
    assert response.json()["data"][0]["portal_ids"] == []

    assert result.returncode == 0

def test_delete_api_product(cli_command, tmp_path):
    oas_spec = tmp_path / "oas.yaml"
    oas_spec.write_text(yaml.dump(spec_v2))

    result = subprocess.run(
        cli_command + [
            "--oas-spec", str(oas_spec),
            "--konnect-portal-name", "test-portal",
            "--konnect-token", "test-token",
            "--konnect-url", f"{test_server_url}",
            "--delete", "--yes"
        ],
        capture_output=True,
        text=True
    )

    response = requests.get(f"{test_server_url}/v2/api-products")
    assert len(response.json()["data"]) == 0

    assert result.returncode == 0
