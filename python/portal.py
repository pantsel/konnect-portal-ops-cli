import requests
import json

class PortalAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    # Makes an HTTP request and handles errors
    def make_http_request(self, url, method='GET', params=None, data=None, json=None, headers=None):
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers
            )
            response.raise_for_status()
            return {
                'status_code': response.status_code,
                'headers': response.headers,
                'body': response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'response_body': getattr(e.response, 'text', None)
            }
        except Exception as e:
            return {
                'error': f'An unexpected error occurred: {str(e)}'
            }

    # Creates a new API product
    def create_api_product(self, name, description, portal_ids):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json={
                "name": name,
                "description": description,
                "portal_ids": portal_ids
            }
        )
        return response

    # Fetches an API product by its name
    def fetch_api_product_by_name(self, name):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products",
            method="GET",
            params= {
                "filter[name]": name
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        if response['status_code'] == 200:
            api_product = response['body']['data']
            return api_product[0] if api_product else None
        return None

    # Updates an existing API product
    def update_api_product(self, api_product_id, name, description, portal_ids):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}",
            method="PATCH",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json={
                "name": name,
                "description": description,
                "portal_ids": portal_ids
            }
        )
        return response

    # Creates a new version of an API product
    def create_api_product_version(self, api_product_id, version, labels=None):
        json_data = {
            "name": version
        }
        if labels is not None:
            json_data["labels"] = labels

        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json=json_data
        )
        return response

    # Updates an existing version of an API product
    def update_api_product_version(self, api_product_id, product_version_id, name, labels=None):
        json_data = {
            "name": name
        }
        if labels is not None:
            json_data["labels"] = labels

        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{product_version_id}",
            method="PATCH",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json=json_data
        )
        return response

    # Fetches a version of an API product by its name
    def fetch_api_product_version_by_name(self, api_product_id, name):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions",
            method="GET",
            params= {
                "filter[name]": name
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        if response['status_code'] == 200:
            api_product_version = response['body']['data']
            return api_product_version[0] if api_product_version else None
        return None

    # Creates a new portal product version
    def create_portal_product_version(self, portal_id, product_version_id):
        response = self.make_http_request(
            f"{self.base_url}/v2/portals/{portal_id}/product-versions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json={
                "product_version_id": product_version_id,
                "publish_status": "published",
                "deprecated": False,
                "application_registration_enabled": False,
                "auto_approve_registration": False,
                "auth_strategy_ids": [],
            }
        )

        print("Portal product version response:", response)

        return response

    # Searches for a portal product version by its ID
    def search_portal_product_version(self, portal_id, product_version_id):
        response = self.make_http_request(
            f"{self.base_url}/v2/portals/{portal_id}/product-versions",
            method="GET",
            params= {
                "filter[product_version_id]": product_version_id
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        if response['status_code'] == 200:
            portal_product_version = response['body']['data']
            return portal_product_version[0] if portal_product_version else None
        return None

    # Creates a new specification for an API product version
    def create_api_product_version_spec(self, api_product_id, api_product_version_id, oas_file_base64):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json={
                "content": oas_file_base64,
                "name": "oas.yaml"
            }
        )
        return response

    # Updates an existing specification for an API product version
    def update_api_product_version_spec(self, api_product_id, api_product_version_id, spec_id, oas_file_base64):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications/{spec_id}",
            method="PATCH",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            json={
                "content": oas_file_base64
            }
        )
        return response

    # Fetches the specification for an API product version
    def fetch_api_product_version_spec(self, api_product_id, api_product_version_id):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications",
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        if response['status_code'] == 200:
            api_product_version_spec = response['body']['data']
            return api_product_version_spec[0] if api_product_version_spec else None
        return None

    # Creates or updates an API product
    def create_or_update_api_product(self, api_name, api_description, portal_id):
        existing_api_product = self.fetch_api_product_by_name(api_name)
        if existing_api_product:
            if portal_id not in existing_api_product['portal_ids']:
                existing_api_product['portal_ids'].append(portal_id)
            api_product = self.update_api_product(
                existing_api_product['id'],
                api_name,
                api_description,
                existing_api_product['portal_ids']
            )
            if 'error' in api_product:
                raise Exception(api_product['error'])
            print("Updated API product:", json.dumps(api_product['body'], indent=2))
        else:
            api_product = self.create_api_product(
                api_name,
                api_description,
                [portal_id]
            )
            if 'error' in api_product:
                raise Exception(api_product['error'])
            print("Created new API product:", json.dumps(api_product['body'], indent=2))
        return api_product

    # Creates or updates an API product version
    def create_or_update_api_product_version(self, api_product_id, product_version):
        existing_api_product_version = self.fetch_api_product_version_by_name(api_product_id, product_version)
        if existing_api_product_version:
            api_product_version = self.update_api_product_version(
                api_product_id,
                existing_api_product_version['id'],
                product_version
            )
            if 'error' in api_product_version:
                raise Exception(api_product_version['error'])
            print(f"Updated API product version for {api_product_id}:", json.dumps(api_product_version['body'], indent=2))
        else:
            api_product_version = self.create_api_product_version(
                api_product_id,
                product_version
            )
            if 'error' in api_product_version:
                raise Exception(api_product_version['error'])
            print(f"Created new API product version for {api_product_id}:", json.dumps(api_product_version['body'], indent=2))
        return api_product_version

    # Creates or updates a specification for an API product version
    def create_or_update_api_product_version_spec(self, api_product_id, api_product_version_id, oas_file_base64):
        existing_api_product_version_spec = self.fetch_api_product_version_spec(api_product_id, api_product_version_id)
        if existing_api_product_version_spec:
            api_product_version_spec = self.update_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                existing_api_product_version_spec['id'],
                oas_file_base64
            )
            if 'error' in api_product_version_spec:
                raise Exception(api_product_version_spec['error'])
            print(f"Updated API product version spec for {api_product_id}:", json.dumps(api_product_version_spec['body'], indent=2))
        else:
            api_product_version_spec = self.create_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                oas_file_base64
            )
            if 'error' in api_product_version_spec:
                raise Exception(api_product_version_spec['error'])
            print(f"Created new API product version spec for {api_product_id}:", json.dumps(api_product_version_spec['body'], indent=2))
        return api_product_version_spec

    # Ensures that a version of an API product is published to a portal
    def ensure_version_published_to_portal(self, portal_id, api_product_version_id, api_product_version_name, api_product_name, environment):
        portal_product_version = self.search_portal_product_version(portal_id, api_product_version_id)
        if portal_product_version:
            print(f"API product version {api_product_version_name} for {api_product_name} on {environment} is already published")
        else:
            portal_product_version = self.create_portal_product_version(portal_id, api_product_version_id)
            if 'error' in portal_product_version:
                raise Exception(portal_product_version['error'])
            print(f"Published API product version {api_product_version_name} for {api_product_name} on {environment}:", json.dumps(portal_product_version['body'], indent=2))