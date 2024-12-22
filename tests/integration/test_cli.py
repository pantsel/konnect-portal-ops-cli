import subprocess
import os
import pytest

@pytest.fixture
def cli_command():
    return ["python3", "src/main.py"]

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
