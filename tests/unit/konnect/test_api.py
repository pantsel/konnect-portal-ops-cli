import pytest
from unittest.mock import MagicMock
from src.kptl.helpers.utils import encode_content
from src.kptl.konnect.api import KonnectApi
from typing import List, Dict, Any

@pytest.fixture
def konnect_api() -> KonnectApi:
    return KonnectApi(base_url="https://example.com", token="dummy_token")

def test_sync_pages_create_new_page(konnect_api: KonnectApi, mocker: Any) -> None:
    local_pages: List[Dict[str, Any]] = [{
        "slug": "1-file1",
        "title": "File1",
        "content": encode_content("Content of file1"),
        "status": "published",
        "parent_slug": None
    }, {
        "slug": "1-1-file11",
        "title": "File11",
        "content": encode_content("Content of file11"),
        "status": "published",
        "parent_slug": "1-file1"
    }, {
        "slug": "1-2-file12",
        "title": "File12",
        "content": encode_content("Content of file12"),
        "status": "published",
        "parent_slug": "1-file1"
    }, {
        "slug": "2-file2",
        "title": "File2",
        "content": encode_content("Content of file2"),
        "status": "unpublished",
        "parent_slug": None
    }]
    remote_pages: List[Dict[str, Any]] = []

    mocker.patch.object(konnect_api.api_product_client, 'get_api_product_document', return_value=None)
    mocker.patch.object(konnect_api.api_product_client, 'create_api_product_document', side_effect=[
        {"id": "1-file1-id", "slug": "1-file1"},
        {"id": "1-1-file11-id", "slug": "1-1-file11"},
        {"id": "1-2-file12-id", "slug": "1-2-file12"},
        {"id": "2-file2-id", "slug": "2-file2"}
    ])

    konnect_api._sync_pages(local_pages, remote_pages, "api_product_id")

    assert konnect_api.api_product_client.create_api_product_document.call_count == 4
    konnect_api.api_product_client.create_api_product_document.assert_any_call(
        "api_product_id",
        {
            "slug": "1-file1",
            "title": "File1",
            "content": encode_content("Content of file1"),
            "status": "published",
            "parent_document_id": None
        }
    )
    konnect_api.api_product_client.create_api_product_document.assert_any_call(
        "api_product_id",
        {
            "slug": "1-1-file11",
            "title": "File11",
            "content": encode_content("Content of file11"),
            "status": "published",
            "parent_document_id": "1-file1-id"
        }
    )
    konnect_api.api_product_client.create_api_product_document.assert_any_call(
        "api_product_id",
        {
            "slug": "1-2-file12",
            "title": "File12",
            "content": encode_content("Content of file12"),
            "status": "published",
            "parent_document_id": "1-file1-id"
        }
    )
    konnect_api.api_product_client.create_api_product_document.assert_any_call(
        "api_product_id",
        {
            "slug": "2-file2",
            "title": "File2",
            "content": encode_content("Content of file2"),
            "status": "unpublished",
            "parent_document_id": None
        }
    )

def test_sync_pages_update_existing_page(konnect_api: KonnectApi, mocker: Any) -> None:
    local_pages: List[Dict[str, Any]] = [
        {"slug": "existing_page", "title": "Existing Page", "parent_slug": None, "content": encode_content("Updated content"), "status": "published"}
    ]
    remote_pages: List[Dict[str, Any]] = [
        {"slug": "existing_page", "id": "existing_page_id"}
    ]

    mocker.patch.object(konnect_api.api_product_client, 'get_api_product_document', return_value={"id": "existing_page_id", "content": encode_content("Old content")})
    mocker.patch.object(konnect_api.api_product_client, 'update_api_product_document', return_value={"id": "existing_page_id"})

    konnect_api._sync_pages(local_pages, remote_pages, "api_product_id")

    konnect_api.api_product_client.update_api_product_document.assert_called_once_with(
        "api_product_id",
        "existing_page_id",
        {
            "slug": "existing_page",
            "title": "Existing Page",
            "content": encode_content("Updated content"),
            "status": "published",
            "parent_document_id": None
        }
    )

def test_sync_pages_no_changes(konnect_api: KonnectApi, mocker: Any) -> None:
    local_pages: List[Dict[str, Any]] = [
        {"slug": "existing_page", "title": "Existing Page", "parent_slug": None, "content": encode_content("Same content"), "status": "published"}
    ]
    remote_pages: List[Dict[str, Any]] = [
        {"slug": "existing_page", "id": "existing_page_id", "title": "Existing Page", "content": "Same content", "status": "published"}
    ]

    mocker.patch.object(konnect_api.api_product_client, 'get_api_product_document', return_value={"id": "existing_page_id", "content": "Same content", "status": "published"})
    mocker.patch.object(konnect_api.api_product_client, 'create_api_product_document')
    mocker.patch.object(konnect_api.api_product_client, 'update_api_product_document')

    konnect_api._sync_pages(local_pages, remote_pages, "api_product_id")

    konnect_api.api_product_client.create_api_product_document.assert_not_called()
    konnect_api.api_product_client.update_api_product_document.assert_not_called()