"""
Module for integration tests with Konnect.
"""

from typing import List, Dict, Any, Tuple
import os
import re
import requests
from src.kptl.helpers.api_product_documents import generate_title_and_slug

class KonnectHelper:
    """
    Helper class for interacting with Konnect API.
    """

    def __init__(self, test_server_url: str, docs_path: str) -> None:
        """
        Initialize the helper with the test server URL and docs path.
        """
        self.test_server_url = test_server_url
        self.docs_path = docs_path

    def check_document_status(self, documents: List[Dict[str, Any]], slug: str, expected_status: str) -> None:
        """
        Check the status of a document by its slug.
        """
        for document in documents:
            if document["slug"] == slug:
                assert document["status"] == expected_status

    def check_parent_document_id(self, documents: List[Dict[str, Any]], slug: str, parent_slug: str) -> None:
        """
        Check the parent document ID of a document by its slug.
        """
        parent_id = next(doc["id"] for doc in documents if doc["slug"] == parent_slug)
        for document in documents:
            if document["slug"] == slug:
                assert document["parent_document_id"] == parent_id

    def check_product_document_structure(self, product_id: str) -> None:
        """
        Check the structure of product documents.
        """
        response = requests.get(f"{self.test_server_url}/v2/api-products/{product_id}", timeout=10)
        api_product_id = response.json()["id"]

        response = requests.get(f"{self.test_server_url}/v2/api-products/{api_product_id}/documents", timeout=10)
        documents = response.json()["data"]

        filenames = os.listdir(self.docs_path)
        expected_slugs = []
        for filename in filenames:
            match = re.match(r'^(\d+)(?:\.(\d+))?', os.path.basename(filename))
            expected_slugs = expected_slugs + [generate_title_and_slug(filename, match)[1]]

        document_slugs = [doc["slug"] for doc in documents]

        assert len(documents) == len(filenames)

        for expected_slug in expected_slugs:
            assert expected_slug in document_slugs

        self.check_document_status(documents, "0-5-api-philosophy", "unpublished")
        self.check_document_status(documents, "httpbin-api-documentation", "unpublished")

        self.check_parent_document_id(documents, "0-1-key-features", "0-introduction")
        self.check_parent_document_id(documents, "0-2-use-cases", "0-introduction")
        self.check_parent_document_id(documents, "0-3-architecture-overview", "0-introduction")
        self.check_parent_document_id(documents, "0-4-supported-environments", "0-introduction")
        self.check_parent_document_id(documents, "0-5-api-philosophy", "0-introduction")
        self.check_parent_document_id(documents, "1-1-child-of-authentication", "1-authentication")

    def get_portal_product_version_by_product_version_id(self, portal_id: str, product_version_id: str) -> Dict[str, Any]:
        """
        Get the portal product version by product version ID.
        """
        response = requests.get(f"{self.test_server_url}/v2/portals/{portal_id}/product-versions", timeout=10)
        version = next(pv for pv in response.json()["data"] if pv["product_version_id"] == product_version_id)
        return version

    def get_api_product_version_by_name(self, api_product_id: str, version: str) -> Dict[str, Any]:
        """
        Get the API product version by name.
        """
        response = requests.get(f"{self.test_server_url}/v2/api-products/{api_product_id}/product-versions", timeout=10)
        product_version = next(pv for pv in response.json()["data"] if pv["name"] == version)
        return product_version

    def get_portal_and_product(self, portal_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get the portal and API product by portal name.
        """
        portal = self.get_portal_by_name(portal_name)
        api_product = self.get_api_product()
        return portal, api_product

    def get_api_product(self) -> Dict[str, Any]:
        """
        Get the API product.
        """
        response = requests.get(f"{self.test_server_url}/v2/api-products", timeout=10)
        api_product = response.json()["data"][0]
        return api_product

    def get_portal_by_name(self, portal_name: str) -> Dict[str, Any]:
        """
        Get the portal by name.
        """
        response = requests.get(f"{self.test_server_url}/v2/portals", timeout=10)
        portal = next(portal for portal in response.json()["data"] if portal["name"] == portal_name)
        return portal
    
    def get_api_product_by_name(self, product_name: str) -> Dict[str, Any]:
        """
        Get the API product by name.
        """
        response = requests.get(f"{self.test_server_url}/v2/api-products", timeout=10)
        api_product = next(api_product for api_product in response.json()["data"] if api_product["name"] == product_name)
        return api_product
