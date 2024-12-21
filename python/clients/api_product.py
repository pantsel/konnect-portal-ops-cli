import requests
from typing import Any, Dict, Optional

class ApiProductClient:
  def __init__(self, base_url: str, token: str):
    self.base_url = base_url
    self.headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
    }

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

  def create_api_product(self, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products"
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_api_products(self, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{self.base_url}/api-products"
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_api_product(self, api_product_id: str) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}"
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_api_product(self, api_product_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}"
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_api_product(self, api_product_id: str) -> None:
    url = f"{self.base_url}/api-products/{api_product_id}"
    response = requests.delete(url, headers=self.headers)
    self._handle_response(response)

  def create_api_product_document(self, api_product_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/documents"
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_api_product_documents(self, api_product_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/documents"
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_api_product_document(self, api_product_id: str, document_id: str) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_api_product_document(self, api_product_id: str, document_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_api_product_document(self, api_product_id: str, document_id: str) -> None:
    url = f"{self.base_url}/api-products/{api_product_id}/documents/{document_id}"
    response = requests.delete(url, headers=self.headers)
    self._handle_response(response)

  def create_api_product_version(self, api_product_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions"
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_api_product_versions(self, api_product_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions"
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_api_product_version(self, api_product_id: str, version_id: str) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_api_product_version(self, api_product_id: str, version_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_api_product_version(self, api_product_id: str, version_id: str) -> None:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}"
    response = requests.delete(url, headers=self.headers)
    self._handle_response(response)

  def create_api_product_version_spec(self, api_product_id: str, version_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications"
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_api_product_version_specs(self, api_product_id: str, version_id: str) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications"
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def get_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str, data: Dict[str, Any]) -> Any:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_api_product_version_spec(self, api_product_id: str, version_id: str, spec_id: str) -> None:
    url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{version_id}/specifications/{spec_id}"
    response = requests.delete(url, headers=self.headers)
    self._handle_response(response)

# Example usage:
# api = ApiProductClient(base_url="https://us.api.konghq.com/v2", token="your_token_here")
# api.create_api_product(data={"name": "API Product", "description": "Text describing the API product"})
