import requests
import json
from logger import Logger


class PortalAPI:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.logger = Logger()

    def make_http_request(self, url, method='GET', params=None, data=None, json=None, headers=None):
        headers = headers or {}
        headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        })
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
            return {'error': f'An unexpected error occurred: {str(e)}'}

    def create_api_product(self, name, description, portal_ids):
        return self.make_http_request(
            f"{self.base_url}/v2/api-products",
            method="POST",
            json={"name": name, "description": description, "portal_ids": portal_ids}
        )

    def fetch_api_product_by_name(self, name):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products",
            method="GET",
            params={"filter[name]": name}
        )
        if response['status_code'] == 200:
            api_product = response['body']['data']
            return api_product[0] if api_product else None
        return None

    def update_api_product(self, api_product_id, name, description, portal_ids):
        return self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}",
            method="PATCH",
            json={"name": name, "description": description, "portal_ids": portal_ids}
        )

    def create_api_product_version(self, api_product_id, version, labels=None):
        json_data = {"name": version}
        if labels:
            json_data["labels"] = labels
        return self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions",
            method="POST",
            json=json_data
        )

    def update_api_product_version(self, api_product_id, product_version_id, name, labels=None):
        json_data = {"name": name}
        if labels:
            json_data["labels"] = labels
        return self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{product_version_id}",
            method="PATCH",
            json=json_data
        )

    def fetch_api_product_version_by_name(self, api_product_id, name):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions",
            method="GET",
            params={"filter[name]": name}
        )
        if response['status_code'] == 200:
            api_product_version = response['body']['data']
            return api_product_version[0] if api_product_version else None
        return None

    def create_portal_product_version(self, portal_id, product_version_id, deprecated=False, publish_status="published"):
        return self.make_http_request(
            f"{self.base_url}/v2/portals/{portal_id}/product-versions",
            method="POST",
            json={
                "product_version_id": product_version_id,
                "publish_status": publish_status,
                "deprecated": deprecated,
                "application_registration_enabled": False,
                "auto_approve_registration": False,
                "auth_strategy_ids": [],
            }
        )

    def update_portal_product_version(self, portal_id, product_version_id, deprecated=False, publish_status="published"):
        return self.make_http_request(
            f"{self.base_url}/v2/portals/{portal_id}/product-versions/{product_version_id}",
            method="PATCH",
            json={
                "publish_status": publish_status,
                "deprecated": deprecated,
                "application_registration_enabled": False,
                "auto_approve_registration": False,
                "auth_strategy_ids": [],
            }
        )

    def search_portal_product_version(self, portal_id, product_version_id):
        response = self.make_http_request(
            f"{self.base_url}/v2/portals/{portal_id}/product-versions",
            method="GET",
            params={"filter[product_version_id]": product_version_id}
        )
        if response['status_code'] == 200:
            portal_product_version = response['body']['data']
            return portal_product_version[0] if portal_product_version else None
        return None

    def create_api_product_version_spec(self, api_product_id, api_product_version_id, oas_file_base64):
        return self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications",
            method="POST",
            json={"content": oas_file_base64, "name": "oas.yaml"}
        )

    def update_api_product_version_spec(self, api_product_id, api_product_version_id, spec_id, oas_file_base64):
        return self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications/{spec_id}",
            method="PATCH",
            json={"content": oas_file_base64}
        )

    def fetch_api_product_version_spec(self, api_product_id, api_product_version_id):
        response = self.make_http_request(
            f"{self.base_url}/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications",
            method="GET"
        )
        if response['status_code'] == 200:
            api_product_version_spec = response['body']['data']
            return api_product_version_spec[0] if api_product_version_spec else None
        return None

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
            action = "Updated"
        else:
            api_product = self.create_api_product(api_name, api_description, [portal_id])
            action = "Created new"

        if 'error' in api_product:
            raise Exception(api_product['error'])

        self.logger.info(f"{action} API product: {api_product['body']['name']} ({api_product['body']['id']})")
        self.logger.debug(json.dumps(api_product['body'], indent=2))
        return api_product['body']

    def create_or_update_api_product_version(self, api_product, product_version):
        existing_api_product_version = self.fetch_api_product_version_by_name(api_product['id'], product_version)
        if existing_api_product_version:
            api_product_version = self.update_api_product_version(
                api_product['id'],
                existing_api_product_version['id'],
                product_version
            )
            action = "Updated"
        else:
            api_product_version = self.create_api_product_version(api_product['id'], product_version)
            action = "Created new"

        if 'error' in api_product_version:
            raise Exception(api_product_version['error'])

        self.logger.info(f"{action} API product version: {api_product_version['body']['name']} ({api_product_version['body']['id']})")
        self.logger.debug(json.dumps(api_product_version['body'], indent=2))
        return api_product_version['body']

    def create_or_update_api_product_version_spec(self, api_product_id, api_product_version_id, oas_file_base64):
        existing_api_product_version_spec = self.fetch_api_product_version_spec(api_product_id, api_product_version_id)
        if existing_api_product_version_spec:
            api_product_version_spec = self.update_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                existing_api_product_version_spec['id'],
                oas_file_base64
            )
            action = "Updated"
        else:
            api_product_version_spec = self.create_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                oas_file_base64
            )
            action = "Created new"

        if 'error' in api_product_version_spec:
            raise Exception(api_product_version_spec['error'])

        self.logger.info(f"{action} spec for API product version: {api_product_version_id}")
        self.logger.debug(json.dumps(api_product_version_spec['body'], indent=2))
        return api_product_version_spec

    def publish_api_product_version_to_portal(self, portal, api_product_version, api_product, deprecated=False, publish_status="published"):
        self.logger.info(f"Publishing API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")
        portal_product_version = self.search_portal_product_version(portal['id'], api_product_version['id'])
        if portal_product_version:
            if portal_product_version['deprecated'] != deprecated or portal_product_version['publish_status'] != publish_status:
                portal_product_version = self.update_portal_product_version(portal['id'], api_product_version['id'], deprecated, publish_status)
                action = "Updated"
            else:
                self.logger.info(f"API product version {api_product_version['name']} for {api_product['name']} on {portal['name']} is already published")
                return
        else:
            portal_product_version = self.create_portal_product_version(portal['id'], api_product_version['id'], deprecated, publish_status)
            action = "Published"

        if 'error' in portal_product_version:
            raise Exception(portal_product_version['error'])

        self.logger.info(f"{action} API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

    def find_portal_by_name(self, portal_name):
        portal = self.make_http_request(
            f"{self.base_url}/v2/portals",
            method="GET",
            params={"filter[name]": portal_name}
        )

        if 'error' in portal:
            raise Exception(portal['error'])

        if portal['status_code'] == 200:
            portal = portal['body']['data']
            return portal[0] if portal else None
        
        return None
