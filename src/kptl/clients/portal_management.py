"""
This module provides a client for managing portal operations.
"""

from typing import Any, Dict, Optional, List
import requests

class PortalManagementClient:
    """
    Client for managing portal operations.
    """
    def __init__(self, base_url: str, token: str, proxies: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.proxies = proxies

    def _handle_response(self, response: requests.Response) -> Any:
        if response.status_code in {200, 201, 204}:
            if response.content:
                return response.json()
            return None
        self._handle_error(response)

    def _handle_error(self, response: requests.Response):
        try:
            error = response.json()
        except ValueError:
            response.raise_for_status()
        status = error.get('status', response.status_code)
        title = error.get('title', 'Error')
        detail = error.get('detail', response.text)
        raise RuntimeError(f"{status} {title}: {detail}")

    def list_portals(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all portals.
        """
        url = f'{self.base_url}/portals'
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def create_portal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new portal.
        """
        url = f'{self.base_url}/portals'
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_portal(self, portal_id: str) -> Dict[str, Any]:
        """
        Get portal details by ID.
        """
        url = f'{self.base_url}/portals/{portal_id}'
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_portal(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update portal details by ID.
        """
        url = f'{self.base_url}/portals/{portal_id}'
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_portal(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Delete portal by ID.
        """
        url = f'{self.base_url}/portals/{portal_id}'
        response = requests.delete(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_portal_products(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all products for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/products'
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def list_portal_product_versions(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all product versions for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions'
        response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def create_portal_product_version(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product version for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions'
        response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def get_portal_product_version(self, portal_id: str, product_version_id: str) -> Dict[str, Any]:
        """
        Get product version details by ID for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def update_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update product version details by ID for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def replace_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace product version details by ID for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        response = requests.put(url, headers=self.headers, json=data, proxies=self.proxies, timeout=10)
        return self._handle_response(response)

    def delete_portal_product_version(self, portal_id: str, product_version_id: str) -> None:
        """
        Delete product version by ID for a portal.
        """
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        response = requests.delete(url, headers=self.headers, proxies=self.proxies, timeout=10)
        return self._handle_response(response)
  
# Example usage:
# portal_client = PortalManagementClient(base_url="https://us.api.konghq.com/v2", token="your_token_here", proxies={"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"})
# portal_client.list_portals()
