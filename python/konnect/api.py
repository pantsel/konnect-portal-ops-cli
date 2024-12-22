import json
import os
from logger import Logger
from clients import ApiProductClient, PortalManagementClient
import constants
from typing import List, Optional, Dict, Any
import helpers.utils as utils
from helpers.api_product_documents import parse_directory

class KonnectApi:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url
        self.token = token
        self.logger = Logger()
        self.api_product_client = ApiProductClient(f"{base_url}/v2", token)
        self.portal_client = PortalManagementClient(f"{base_url}/v2", token)

    def find_api_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        response = self.api_product_client.list_api_products({"filter[name]": name})
        return response['data'][0] if response['data'] else None
    
    def find_api_product_version_by_name(self, api_product_id: str, name: str) -> Optional[Dict[str, Any]]:
        response = self.api_product_client.list_api_product_versions(api_product_id, {"filter[name]": name})
        return response['data'][0] if response['data'] else None

    def find_portal_by_name(self, portal_name: str) -> Optional[Dict[str, Any]]:
        portal = self.portal_client.list_portals({"filter[name]": portal_name})
        return portal['data'][0] if portal['data'] else None

    def find_portal_product_version(self, portal_id: str, product_version_id: str) -> Optional[Dict[str, Any]]:
        response = self.portal_client.list_portal_product_versions(portal_id, {"filter[product_version_id]": product_version_id})
        return response['data'][0] if response['data'] else None

    def create_or_update_api_product(self, api_name: str, api_description: str, portal_id: str, unpublish: bool) -> Dict[str, Any]:
        existing_api_product = self.find_api_product_by_name(api_name)
        new_portal_ids = existing_api_product['portal_ids'][:] if existing_api_product else []

        if existing_api_product:
            if unpublish:
                if portal_id in new_portal_ids:
                    new_portal_ids.remove(portal_id)
            else:
                if portal_id not in new_portal_ids:
                    new_portal_ids.append(portal_id)
            
            if existing_api_product['description'] != api_description or new_portal_ids != existing_api_product['portal_ids']:
                api_product = self.api_product_client.update_api_product(
                    existing_api_product['id'],
                    {
                        "name": api_name,
                        "description": api_description,
                        "portal_ids": new_portal_ids
                    }
                )
                action = "Updated"
            else:
                api_product = existing_api_product
                action = "No changes detected for"
        else:
            api_product = self.api_product_client.create_api_product(
                {
                    "name": api_name,
                    "description": api_description,
                    "portal_ids": [portal_id if not unpublish else None],
                }
            )
            action = "Created new"

        self.logger.info(f"{action} API product: {api_product['name']} ({api_product['id']})")
        self.logger.debug(json.dumps(api_product, indent=2))
        return api_product

    def create_or_update_api_product_version(self, api_product: Dict[str, Any], version_name: str) -> Dict[str, Any]:
        
        self.logger.info(f"Processing API product version")

        existing_api_product_version = self.find_api_product_version_by_name(api_product['id'], version_name)
        if existing_api_product_version:
            api_product_version = existing_api_product_version
            action = "No changes detected for"
        else:
            api_product_version = self.api_product_client.create_api_product_version(
                api_product['id'],
                {
                    "name": version_name
                }
            )
            action = "Created new"

        self.logger.info(f"{action} API product version: {api_product_version['name']} ({api_product_version['id']})")
        self.logger.debug(json.dumps(api_product_version, indent=2))
        return api_product_version

    def create_or_update_api_product_version_spec(self, api_product_id: str, api_product_version_id: str, oas_file_base64: str) -> Dict[str, Any]:

        self.logger.info(f"Processing API product version spec")

        existing_api_product_version_specs = self.api_product_client.list_api_product_version_specs(api_product_id, api_product_version_id)
        existing_api_product_version_spec = existing_api_product_version_specs['data'][0] if existing_api_product_version_specs['data'] else None

        if existing_api_product_version_spec:
            if utils.encode_content(existing_api_product_version_spec['content']) != oas_file_base64:
                api_product_version_spec = self.api_product_client.update_api_product_version_spec(
                    api_product_id,
                    api_product_version_id,
                    existing_api_product_version_spec['id'],
                    {"content": oas_file_base64}
                )
                action = "Updated"
            else:
                api_product_version_spec = existing_api_product_version_spec
                action = "No changes detected for"
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

    def create_or_update_portal_api_product_version(self, portal: Dict[str, Any], api_product_version: Dict[str, Any], api_product: Dict[str, Any], deprecated: bool = False, publish_status: str = "published") -> None:
                
        if publish_status not in ["published", "unpublished"]:
            raise ValueError("Invalid publish status. Must be 'published' or 'unpublished'")
        if deprecated not in [True, False]:
            raise ValueError("Invalid deprecation status. Must be True or False")

        if publish_status == "published":
            self.logger.info(f"Publishing API product version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")
        else:
            self.logger.info(f"Unpublishing API product version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

        if deprecated:
            self.logger.info(f"Deprecating API product version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

        portal_product_version = self.find_portal_product_version(portal['id'], api_product_version['id'])

        if portal_product_version:
            if portal_product_version['deprecated'] != deprecated or portal_product_version['publish_status'] != publish_status:
                portal_product_version = self.portal_client.update_portal_product_version(
                    portal['id'],
                    api_product_version['id'],
                    {
                        "deprecated": deprecated,
                        "publish_status": publish_status
                    }
                )
                action = "Updated"
            else:
                self.logger.info(f"API product version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}' is up to date. No further action required.")
                return
        else:
            portal_product_version = self.portal_client.create_portal_product_version(
                portal['id'],
                {
                    "product_version_id": api_product_version['id'],
                    "deprecated": deprecated,
                    "publish_status": publish_status,
                    "application_registration_enabled": False,  # @TODO: Make this configurable
                    "auto_approve_registration": False,  # @TODO: Make this configurable
                    "auth_strategy_ids": [],  # @TODO: Make this configurable
                }
            )
            action = "Published"

        self.logger.info(f"{action} API product version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

    def delete_api_product(self, api_name: str) -> None:
        api_product = self.find_api_product_by_name(api_name)
        if api_product:
            self.logger.info(f"Deleting API product: '{api_product['name']}' ({api_product['id']})")
            self.api_product_client.delete_api_product(api_product['id'])
            self.logger.info(f"API product '{api_name}' deleted successfully.")
        else:
            self.logger.warning(f"API product '{api_name}' not found. Nothing to delete.")
        
    def _sync_pages(self, local_pages: List[Dict[str, str]], remote_pages: List[Dict[str, str]], api_product_id: str) -> None:
        slug_to_id = {page['slug']: page['id'] for page in remote_pages}

        # Handle creation and updates
        for page in local_pages:
            parent_id = slug_to_id.get(page['parent_slug']) if page['parent_slug'] else None
            existing_page_from_list = next((p for p in remote_pages if p['slug'].split('/')[-1] == page['slug'].split('/')[-1]), None)

            existing_page = self.api_product_client.get_api_product_document(api_product_id, existing_page_from_list['id']) if existing_page_from_list else None

            if not existing_page:
                self.logger.info(f"Creating page: '{page['title']}' ({page['slug']})")
                page = self.api_product_client.create_api_product_document(api_product_id, {
                    "slug": page['slug'],
                    "title": page['title'],
                    "content": page['content'],
                    "status":  page['status'],
                    "parent_document_id": parent_id
                })
                slug_to_id[page['slug']] = page['id']
            elif utils.encode_content(existing_page['content']) != page['content'] or existing_page.get('parent_document_id') != parent_id or existing_page.get('status') != page['status']:
                self.logger.info(f"Updating page: '{page['title']}' ({page['slug']})")
                self.api_product_client.update_api_product_document(api_product_id, existing_page['id'], {
                    "slug": page['slug'],
                    "title": page['title'],
                    "content": page['content'],
                    "status": page['status'],
                    "parent_document_id": parent_id
                })
            else:
                self.logger.info(f"No changes detected for page: '{page['title']}' ({page['slug']})")

        # Handle deletions
        local_slugs = {page['slug'] for page in local_pages}
        for remote_page in remote_pages:
            if remote_page['slug'].split('/')[-1] not in local_slugs:
                self.logger.warning(f"Deleting page: '{remote_page['title']}' ({remote_page['slug']})")
                self.api_product_client.delete_api_product_document(api_product_id, remote_page['id'])

    def sync_api_product_documents(self, api_product_id: str, directory: str) -> Dict[str, Any]:
        directory = os.path.join(os.getcwd(), directory)
        local_pages = parse_directory(directory)

        existing_documents = self.api_product_client.list_api_product_documents(api_product_id)
        remote_pages = existing_documents['data']

        self.logger.info(f"Processing documents in '{directory}'")
        self._sync_pages(local_pages, remote_pages, api_product_id)
