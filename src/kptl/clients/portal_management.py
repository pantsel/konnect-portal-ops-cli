import requests
from typing import Any, Dict, Optional, List

class PortalManagementClient:
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
    else:
      self._handle_error(response)

  def _handle_error(self, response: requests.Response):
    try:
      error = response.json()
    except ValueError:
      response.raise_for_status()
    status = error.get('status', response.status_code)
    title = error.get('title', 'Error')
    detail = error.get('detail', response.text)
    raise Exception(f"{status} {title}: {detail}")

  def list_portals(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals'
    response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies)
    return self._handle_response(response)

  def create_portal(self, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals'
    response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies)
    return self._handle_response(response)

  def get_portal(self, portal_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.get(url, headers=self.headers, proxies=self.proxies)
    return self._handle_response(response)

  def update_portal(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies)
    return self._handle_response(response)

  def delete_portal(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> None:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.delete(url, headers=self.headers, params=params, proxies=self.proxies)
    return self._handle_response(response)

  def list_portal_products(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/products'
    response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies)
    return self._handle_response(response)

  def list_portal_product_versions(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions'
    response = requests.get(url, headers=self.headers, params=params, proxies=self.proxies)
    return self._handle_response(response)

  def create_portal_product_version(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions'
    response = requests.post(url, headers=self.headers, json=data, proxies=self.proxies)
    return self._handle_response(response)

  def get_portal_product_version(self, portal_id: str, product_version_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.get(url, headers=self.headers, proxies=self.proxies)
    return self._handle_response(response)

  def update_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.patch(url, headers=self.headers, json=data, proxies=self.proxies)
    return self._handle_response(response)

  def replace_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.put(url, headers=self.headers, json=data, proxies=self.proxies)
    return self._handle_response(response)

  def delete_portal_product_version(self, portal_id: str, product_version_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.delete(url, headers=self.headers, proxies=self.proxies)
    return self._handle_response(response)
  
# Example usage:
# portal_client = PortalManagementClient(base_url="https://us.api.konghq.com/v2", token="your_token_here", proxies={"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"})
# portal_client.list_portals()
