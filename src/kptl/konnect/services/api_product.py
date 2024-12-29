"""
Module for API product client.
"""

from typing import Any, Dict, Optional
import requests

class ApiProductClient:
    """
    Client for interacting with API products.
    """
    def __init__(self, base_url: str, token: str, proxies: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.proxies = proxies

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle the response from the API.
        """
        if response.status_code in {200, 201, 204}:
            if response.content:
                return response.json()
            return None
        self._handle_error(response)

    def _handle_error(self, response: requests.Response):
        """
        Handle errors from the API.
        """
        try:
            error = response.json()
        except ValueError:
            response.raise_for_status()
        status = error.get('status', response.status_code)
        title = error.get('title', 'Error')
        detail = error.get('detail', response.text)
        raise Exception(f"{status} {title}: {detail}")

    def create_api_product(self, data: Dict[str, Any]) -> Any:
        """
        Create a new API product.
        """
        url = f"{self.base_url}/api-products"
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_api_products(self, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        List all API products.
        """
        url = f"{self.base_url}/api-products"
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_api_product(self, api_product_id: str) -> Any:
        """
        Get an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}"
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_api_product(self, api_product_id: str, data: Dict[str, Any]) -> Any:
        """
        Update an existing API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}"
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_api_product(self, api_product_id: str) -> None:
        """
        Delete an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}"
        response = requests.delete(url, headers=self.headers, proxies=self.proxies, timeout=10)
        self._handle_response(response)

    def create_api_product_document(self, api_product_id: str, data: Dict[str, Any]) -> Any:
        """
        Create a new document for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/documents"
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_api_product_documents(self, api_product_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        List all documents for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/documents"
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_api_product_document(self, api_product_id: str, document_id: str) -> Any:
        """
        Get a document for an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_api_product_document(self, api_product_id: str, document_id: str, data: Dict[str, Any]) -> Any:
        """
        Update an existing document for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_api_product_document(self, api_product_id: str, document_id: str) -> None:
        """
        Delete a document for an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
        response = requests.delete(url, headers=self.headers, proxies=self.proxies, timeout=10)
        self._handle_response(response)

    def create_api_product_version(self, api_product_id: str, data: Dict[str, Any]) -> Any:
        """
        Create a new version for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions"
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_api_product_versions(self, api_product_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        List all versions for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions"
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_api_product_version(self, api_product_id: str, version_id: str) -> Any:
        """
        Get a version for an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_api_product_version(self, api_product_id: str, version_id: str, data: Dict[str, Any]) -> Any:
        """
        Update an existing version for an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_api_product_version(self, api_product_id: str, version_id: str) -> None:
        """
        Delete a version for an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
        response = requests.delete(url, headers=self.headers, proxies=self.proxies, timeout=10)
        self._handle_response(response)

    def create_api_product_version_spec(self, api_product_id: str, version_id: str, data: Dict[str, Any]) -> Any:
        """
        Create a new specification for a version of an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications"
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_api_product_version_specs(self, api_product_id: str, version_id: str) -> Any:
        """
        List all specifications for a version of an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications"
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str) -> Any:
        """
        Get a specification for a version of an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str, data: Dict[str, Any]) -> Any:
        """
        Update an existing specification for a version of an API product.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str) -> None:
        """
        Delete a specification for a version of an API product by ID.
        """
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
        response = requests.delete(url, headers=self.headers, proxies=self.proxies, timeout=10)
        self._handle_response(response)

# Example usage:
# api = ApiProductClient(base_url="https://us.api.konghq.com/v2", token="your_token_here", proxies={"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"})
# api.create_api_product(data={"name": "API Product", "description": "Text describing the API product"})
