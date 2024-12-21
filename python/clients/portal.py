import requests

class PortalClient:
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

    def list_portals(self, params=None):
        """List all portals."""
        url = f'{self.base_url}/portals'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to list portals: {err}')
            return None

    def list_portal_products(self, portal_id, params=None):
        """List Portal Products."""
        url = f'{self.base_url}/portals/{portal_id}/products'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to list portal products: {err}')
            return None

    def list_portal_product_versions(self, portal_id, params=None):
        """List portal product versions."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to list portal product versions: {err}')
            return None

    def create_portal_product_version(self, portal_id, product_version_data):
        """Create a portal product version."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions'
        try:
            response = requests.post(url, headers=self.headers, json=product_version_data)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to create portal product version: {err}')
            return None

    def get_portal_product_version(self, portal_id, product_version_id):
        """Get a portal product version."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        try:
            response = requests.get(url, headers=self.headers)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to get portal product version {product_version_id}: {err}')
            return None

    def update_portal_product_version(self, portal_id, product_version_id, product_version_data):
        """Update a portal product version."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        try:
            response = requests.patch(url, headers=self.headers, json=product_version_data)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to update portal product version {product_version_id}: {err}')
            return None

    def replace_portal_product_version(self, portal_id, product_version_id, product_version_data):
        """Replace a portal product version."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        try:
            response = requests.put(url, headers=self.headers, json=product_version_data)
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to replace portal product version {product_version_id}: {err}')
            return None

    def delete_portal_product_version(self, portal_id, product_version_id):
        """Delete a portal product version."""
        url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 204:
                print(f'Portal product version {product_version_id} deleted successfully.')
                return True
            return self._handle_response(response)
        except Exception as err:
            print(f'Failed to delete portal product version {product_version_id}: {err}')
            return None
