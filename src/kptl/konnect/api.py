import json
import os
from typing import List, Optional, Dict, Any

from kptl.logger import Logger
from kptl.clients import ApiProductClient, PortalManagementClient
from kptl.helpers import utils
from kptl.helpers.api_product_documents import parse_directory, get_slug_tail

class KonnectApi:
    def __init__(self, base_url: str, token: str, api_product_client: Optional[ApiProductClient] = None, portal_client: Optional[PortalManagementClient] = None, logger: Optional[Logger] = None) -> None:
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

    def create_or_update_api_product(self, api_title: str, api_description: str, portal_id: str, unpublish: bool) -> Dict[str, Any]:
        existing_api_product = self.find_api_product_by_name(api_title)
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
                        "name": api_title,
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
                    "name": api_title,
                    "description": api_description,
                    "portal_ids": [portal_id if not unpublish else None],
                }
            )
            action = "Created new"

        self.logger.info(f"{action} API product: {api_product['name']} ({api_product['id']})")
        self.logger.debug(json.dumps(api_product, indent=2))
        return api_product

    def create_or_update_api_product_version(self, api_product: Dict[str, Any], version_name: str) -> Dict[str, Any]:
        
        self.logger.info(f"Processing API Product Version")

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

        self.logger.info(f"{action} API Product Version: {api_product_version['name']} ({api_product_version['id']})")
        self.logger.debug(json.dumps(api_product_version, indent=2))
        return api_product_version

    def create_or_update_api_product_version_spec(self, api_product_id: str, api_product_version_id: str, oas_file_base64: str) -> Dict[str, Any]:

        self.logger.info(f"Processing API Product Version Spec")

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

        self.logger.info(f"{action} API Product Version Spec: {api_product_version_id}")
        self.logger.debug(json.dumps(api_product_version_spec, indent=2))
        return api_product_version_spec

    def create_or_update_portal_product_version(self, portal: Dict[str, Any], api_product_version: Dict[str, Any], api_product: Dict[str, Any], options: Dict[str, Any]) -> None:
        """
        Create or update a Portal Product Version.
        This method handles the creation or updating of a Portal Product Version based on the provided parameters.
        It ensures that the product version is published or unpublished, deprecated or not, and updates the registration
        and authentication strategies as specified.
        Args:
            portal (Dict[str, Any]): The portal information containing the portal ID and name.
            api_product_version (Dict[str, Any]): The API product version details including its ID and name.
            api_product (Dict[str, Any]): The API product details including its name.
            options (Dict[str, Any]): Additional options for the product version, including:
                - publish_status (str): The publish status, either 'published' or 'unpublished'. Defaults to 'published'.
                - deprecated (bool): The deprecation status. Defaults to False.
                - application_registration_enabled (bool): Whether application registration is enabled. Defaults to False.
                - auto_approve_registration (bool): Whether auto-approve registration is enabled. Defaults to False.
                - auth_strategy_ids (List[str]): List of authentication strategy IDs. Defaults to an empty list.
        Raises:
            ValueError: If the publish status is not 'published' or 'unpublished'.
            ValueError: If the deprecated status is not a boolean.
        Returns:
            None
        """
                
        publish_status = options.get("publish_status", "published")
        deprecated = options.get("deprecated", False)
        application_registration_enabled = options.get("application_registration_enabled", False)
        auto_approve_registration = options.get("auto_approve_registration", False)
        auth_strategy_ids = options.get("auth_strategy_ids", [])

        if publish_status not in ["published", "unpublished"]:
            raise ValueError("Invalid publish status. Must be 'published' or 'unpublished'")
        if deprecated not in [True, False]:
            raise ValueError("Invalid deprecation status. Must be True or False")

        if publish_status == "published":
            self.logger.info(f"Publishing Portal Product Version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")
        else:
            self.logger.info(f"Unpublishing Portal Product Version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

        if deprecated:
            self.logger.info(f"Deprecating Portal Product Version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

        portal_product_version = self.find_portal_product_version(portal['id'], api_product_version['id'])

        if portal_product_version:
            if (portal_product_version['deprecated'] != deprecated or 
                portal_product_version['publish_status'] != publish_status or
                portal_product_version['application_registration_enabled'] != application_registration_enabled or
                portal_product_version['auto_approve_registration'] != auto_approve_registration or
                [strategy['id'] for strategy in portal_product_version['auth_strategies']] != auth_strategy_ids):
                
                portal_product_version = self.portal_client.update_portal_product_version(
                    portal['id'],
                    api_product_version['id'],
                    {
                        "deprecated": deprecated,
                        "publish_status": publish_status,
                        "application_registration_enabled": application_registration_enabled,
                        "auto_approve_registration": auto_approve_registration,
                        "auth_strategy_ids": auth_strategy_ids
                    }
                )
                action = "Updated"
            else:
                self.logger.info(f"Portal Product Version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}' is up to date.")
                return
        else:
            portal_product_version = self.portal_client.create_portal_product_version(
                portal['id'],
                {
                    "product_version_id": api_product_version['id'],
                    "deprecated": deprecated,
                    "publish_status": publish_status,
                    "application_registration_enabled": application_registration_enabled,
                    "auto_approve_registration": auto_approve_registration,
                    "auth_strategy_ids": auth_strategy_ids
                }
            )
            action = "Published"

        self.logger.info(f"{action} Portal Product Version '{api_product_version['name']}' for '{api_product['name']}' on '{portal['name']}'")

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
            existing_page_from_list = next((p for p in remote_pages if get_slug_tail(p['slug']) == get_slug_tail(page['slug'])), None)

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
            if get_slug_tail(remote_page['slug']) not in local_slugs:
                self.logger.warning(f"Deleting page: '{remote_page['title']}' ({remote_page['slug']})")
                self.api_product_client.delete_api_product_document(api_product_id, remote_page['id'])


    def sync_api_product_documents(self, api_product_id: str, directory: str) -> Dict[str, Any]:
        directory = os.path.join(os.getcwd(), directory)
        local_pages = parse_directory(directory)

        existing_documents = self.api_product_client.list_api_product_documents(api_product_id)
        remote_pages = existing_documents['data']

        self.logger.info(f"Processing documents in '{directory}'")
        self._sync_pages(local_pages, remote_pages, api_product_id)
