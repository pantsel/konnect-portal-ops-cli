import requests

class ApiProductClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}" if api_key else "",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response):
        """Handle response and raise appropriate exceptions."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 201:
            return response.json()
        elif response.status_code == 204:
            return None
        elif response.status_code == 400:
            raise ValueError("Bad Request: Check your request parameters.")
        elif response.status_code == 401:
            raise PermissionError("Unauthorized: Check your API key.")
        elif response.status_code == 403:
            raise PermissionError("Forbidden: You do not have access.")
        elif response.status_code == 404:
            raise FileNotFoundError("Not Found: The resource doesn't exist.")
        elif response.status_code == 415:
            raise TypeError("Unsupported Media Type: Ensure correct content type.")
        else:
            response.raise_for_status()

    def create_api_product(self, product_data):
        """Create an API product."""
        url = f"{self.base_url}/api-products"
        response = requests.post(url, json=product_data, headers=self.headers)
        return self._handle_response(response)

    def get_api_products(self, params=None):
        """List all API products."""
        url = f"{self.base_url}/api-products"
        response = requests.get(url, params=params, headers=self.headers)
        return self._handle_response(response)

    def get_api_product(self, product_id):
        """Fetch a single API product by ID."""
        url = f"{self.base_url}/api-products/{product_id}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def update_api_product(self, product_id, product_data):
        """Update an existing API product."""
        url = f"{self.base_url}/api-products/{product_id}"
        response = requests.patch(url, json=product_data, headers=self.headers)
        return self._handle_response(response)

    def delete_api_product(self, product_id):
        """Delete an API product."""
        url = f"{self.base_url}/api-products/{product_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

    def create_api_product_document(self, product_id, document_data):
        """Create a document for an API product."""
        url = f"{self.base_url}/api-products/{product_id}/documents"
        response = requests.post(url, json=document_data, headers=self.headers)
        return self._handle_response(response)

    def get_api_product_documents(self, product_id):
        """List all documents for an API product."""
        url = f"{self.base_url}/api-products/{product_id}/documents"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def get_api_product_document(self, product_id, document_id):
        """Fetch a document for an API product."""
        url = f"{self.base_url}/api-products/{product_id}/documents/{document_id}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def update_api_product_document(self, product_id, document_id, document_data):
        """Update an API product document."""
        url = f"{self.base_url}/api-products/{product_id}/documents/{document_id}"
        response = requests.patch(url, json=document_data, headers=self.headers)
        return self._handle_response(response)

    def delete_api_product_document(self, product_id, document_id):
        """Delete an API product document."""
        url = f"{self.base_url}/api-products/{product_id}/documents/{document_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)
    
    def get_api_product_versions(self, product_id, params=None):
        """List all versions of an API product."""
        url = f"{self.base_url}/api-products/{product_id}/product-versions"
        response = requests.get(url, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def get_api_product_version(self, product_id, version_id):
        """Fetch a version of an API product."""
        url = f"{self.base_url}/api-products/{product_id}/product-versions/{version_id}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def create_api_product_version(self, product_id, version_data):
        """Create a version of an API product."""
        url = f"{self.base_url}/api-products/{product_id}/product-versions"
        response = requests.post(url, json=version_data, headers=self.headers)
        return self._handle_response(response)
    
    def update_api_product_version(self, product_id, version_id, version_data):
        """Update a version of an API product."""
        url = f"{self.base_url}/api-products/{product_id}/product-versions/{version_id}"
        response = requests.patch(url, json=version_data, headers=self.headers)
        return self._handle_response(response)
    
    def delete_api_product_version(self, product_id, version_id):
        """Delete a version of an API product."""
        url = f"{self.base_url}/api-products/{product_id}/product-versions/{version_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)
    
    def create_api_product_version_spec(self, api_product_id, api_product_version_id, spec_data):
        """Create an API Product Version Specification."""
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications"
        response = requests.post(url, json=spec_data, headers=self.headers)
        return self._handle_response(response)

    def get_api_product_version_specs(self, api_product_id, api_product_version_id):
        """Fetch API Product Version Specifications."""
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def get_api_product_version_spec(self, api_product_id, api_product_version_id, specification_id):
        """Fetch a specific API Product Version Specification."""
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications/{specification_id}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def update_api_product_version_spec(self, api_product_id, api_product_version_id, specification_id, spec_data):
        """Update an API Product Version Specification."""
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications/{specification_id}"
        response = requests.patch(url, json=spec_data, headers=self.headers)
        return self._handle_response(response)

    def delete_api_product_version_spec(self, api_product_id, api_product_version_id, specification_id):
        """Delete an API Product Version Specification."""
        url = f"{self.base_url}/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications/{specification_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)
