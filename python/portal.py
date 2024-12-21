import requests
import json
from logger import Logger
from clients import ApiProductClient, PortalClient

class PortalAPI:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.logger = Logger()
        self.api_product_client = ApiProductClient(f"{base_url}/v2", token)
        self.portal_client = PortalClient(f"{base_url}/v2", token)

    def find_api_product_by_name(self, name):
        response = self.api_product_client.get_api_products({"filter[name]": name})
        return response['data'][0] if len(response['data']) > 0 else None

    def find_api_product_version_by_name(self, api_product_id, name):
        response = self.api_product_client.get_api_product_versions(api_product_id, {"filter[name]": name})
        return response['data'][0] if len(response['data']) > 0 else None
    
    def find_portal_by_name(self, portal_name):
        portal = self.portal_client.list_portals({"filter[name]": portal_name})
        return portal['data'][0] if len(portal['data']) > 0 else None

    def find_portal_product_version(self, portal_id, product_version_id):
        response = self.portal_client.list_portal_product_versions(portal_id, {"filter[product_version_id]": product_version_id})
        return response['data'][0] if len(response['data']) > 0 else None

    def create_or_update_api_product(self, api_name, api_description, portal_id):
        existing_api_product = self.find_api_product_by_name(api_name)
        if existing_api_product:
            if portal_id not in existing_api_product['portal_ids']:
                existing_api_product['portal_ids'].append(portal_id)
            api_product = self.api_product_client.update_api_product(existing_api_product['id'], {
                "name": api_name,
                "description": api_description,
                "portal_ids": existing_api_product['portal_ids']
            })
            action = "Updated"
        else:
            api_product = self.api_product_client.create_api_product({
                "name": api_name,
                "description": api_description,
                "portal_ids": [portal_id]
            })
            action = "Created new"

        self.logger.info(f"{action} API product: {api_product['name']} ({api_product['id']})")
        self.logger.debug(json.dumps(api_product, indent=2))
        return api_product

    def create_or_update_api_product_version(self, api_product, version_name):
        existing_api_product_version = self.find_api_product_version_by_name(api_product['id'], version_name)
        if existing_api_product_version:
            api_product_version = self.api_product_client.update_api_product_version(
                api_product['id'],
                existing_api_product_version['id'],
                {
                    "name": version_name
                }
            )
            action = "Updated"
        else:
            api_product_version = self.api_product_client.create_api_product_version(api_product['id'], {
                "name": version_name,
                "labels": {
                    "generated_by": "cli"
                }
            })
            action = "Created new"

        self.logger.info(f"{action} API product version: {api_product_version['name']} ({api_product_version['id']})")
        self.logger.debug(json.dumps(api_product_version, indent=2))
        return api_product_version

    def create_or_update_api_product_version_spec(self, api_product_id, api_product_version_id, oas_file_base64):
        existing_api_product_version_specs = self.api_product_client.get_api_product_version_specs(api_product_id, api_product_version_id)

        # Always update the first spec if it exists
        existing_api_product_version_spec = existing_api_product_version_specs['data'][0] if len(existing_api_product_version_specs['data']) > 0 else None
        
        if existing_api_product_version_spec:
            api_product_version_spec = self.api_product_client.update_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                existing_api_product_version_spec['id'],
                {
                    "content": oas_file_base64
                }
            )

            action = "Updated"
        else:
            api_product_version_spec = self.api_product_client.create_api_product_version_spec(
                api_product_id,
                api_product_version_id,
                {
                    "content": oas_file_base64,
                    "name": "oas.yaml"
                }
            )
            action = "Created new"

        self.logger.info(f"{action} spec for API product version: {api_product_version_id}")
        self.logger.debug(json.dumps(api_product_version_spec, indent=2))
        return api_product_version_spec

    def create_or_update_portal_api_product_version(self, portal, api_product_version, api_product, deprecated=False, publish_status="published"):

        if publish_status not in ["published", "unpublished"]:
            raise ValueError("Invalid publish status. Must be 'published' or 'unpublished'")
        if deprecated not in [True, False]:
            raise ValueError("Invalid deprecation status. Must be True or False")
        
        if publish_status == "published":
            self.logger.info(f"Publishing API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")
        else:
            self.logger.info(f"Unpublishing API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

        if deprecated:
            self.logger.info(f"Deprecating API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

        portal_product_version = self.find_portal_product_version(portal['id'], api_product_version['id'])

        if portal_product_version:
            if portal_product_version['deprecated'] != deprecated or portal_product_version['publish_status'] != publish_status:
                portal_product_version = self.portal_client.update_portal_product_version(portal['id'], api_product_version['id'], {
                    "deprecated": deprecated,
                    "publish_status": publish_status
                })
                action = "Updated"
            else:
                self.logger.info(f"API product version {api_product_version['name']} for {api_product['name']} on {portal['name']} updated")
                return
        else:
            portal_product_version = self.portal_client.create_portal_product_version(portal['id'], {
                "product_version_id": api_product_version['id'],
                "deprecated": deprecated,
                "publish_status": publish_status,
                "application_registration_enabled": False,
                "auto_approve_registration": False,
                "auth_strategy_ids": []
            })
            action = "Published"

        self.logger.info(f"{action} API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

 