"""
This module provides the KonnectApi class for interacting with the Konnect API.
"""

import json
import os
from typing import List, Optional, Dict, Any

from kptl.logger import Logger
from kptl.clients import ApiProductClient, PortalManagementClient
from kptl.helpers import utils
from kptl.helpers.api_product_documents import parse_directory, get_slug_tail

class KonnectApi:
    """
    A class to interact with the Konnect API.
    """
    def __init__(self, base_url: str, token: str, proxies: Optional[Dict[str, str]] = None) -> None:
        self.base_url = base_url
        self.token = token
        self.logger = Logger()
        self.api_product_client = ApiProductClient(f"{base_url}/v2", token, proxies)
        self.portal_client = PortalManagementClient(f"{base_url}/v2", token, proxies)

    def find_api_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find an API product by its name.

        Args:
            name (str): The name of the API product.

        Returns:
            Optional[Dict[str, Any]]: The API product details if found, else None.
        """
        response = self.api_product_client.list_api_products({"filter[name]": name})

        if len(response['data']) > 1:
            self.logger.error("Multiple API products found with the name: %s. Please resolve the duplicate names manually before proceeding.", name)
            exit(1)

        return response['data'][0] if response['data'] else None
    
    def find_api_product_by_id(self, api_product_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an API product by its ID.

        Args:
            api_product_id (str): The ID of the API product.

        Returns:
            Optional[Dict[str, Any]]: The API product details if found, else None.
        """
        return self.api_product_client.get_api_product(api_product_id)

    def create_api_product(self, data: Dict) -> Dict[str, Any]:
        """
        Create an API product.

        Args:
            name (str): The name of the API product.
            description (str): The description of the API product.

        Returns:
            Dict[str, Any]: The API product details.
        """
        self.logger.info("Creating API product: '%s'", data['name'])
        api_product = self.api_product_client.create_api_product(data)
        self.logger.info("API product '%s' created successfully.", data['name'])
        return api_product
    
    def update_api_product(self, api_product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an API product.

        Args:
            api_product_id (str): The ID of the API product.
            data (Dict[str, Any]): The data to update.

        Returns:
            Dict[str, Any]: The updated API product details.
        """
        self.logger.info("Updating API product: '%s' (%s)", data['name'], api_product_id)
        api_product = self.api_product_client.update_api_product(api_product_id, data)
        self.logger.info("API product '%s' updated successfully.", data['name'])
        return api_product

    def delete_portal_product_version(self, portal_id: str, api_product_version_id: str) -> None:
        """
        Delete a portal product version.

        Args:
            portal_id (str): The ID of the portal.
            api_product_version_id (str): The ID of the API product version.

        Returns:
            None
        """
        self.logger.info("Deleting portal product version: '%s' (%s)", api_product_version_id, api_product_version_id)
        self.portal_client.delete_portal_product_version(portal_id, api_product_version_id)
        self.logger.info("Portal product version '%s' deleted successfully.", api_product_version_id)

    def find_api_product_version_by_name(self, api_product_id: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Find an API product version by its name.

        Args:
            api_product_id (str): The ID of the API product.
            name (str): The name of the API product version.

        Returns:
            Optional[Dict[str, Any]]: The API product version details if found, else None.
        """
        response = self.api_product_client.list_api_product_versions(api_product_id, {"filter[name]": name})

        if len(response['data']) > 1:
            self.logger.error("Multiple API product versions found with the name: %s for product %s. Please resolve the duplicate names manually before proceeding.", name, api_product_id)
            exit(1)

        return response['data'][0] if response['data'] else None

    def list_api_product_versions(self, api_product_id: str) -> List[Dict[str, Any]]:
        """
        List all API product versions.

        Args:
            api_product_id (str): The ID of the API product.

        Returns:
            List[Dict[str, Any]]: The list of API product versions.
        """
        response = self.api_product_client.list_api_product_versions(api_product_id)
        return response['data']
    
    def find_portal(self, portal: str) -> Optional[Dict[str, Any]]:
        """
        Find a portal by its name or ID.

        Args:
            portal (str): The name or ID of the portal.

        Returns:
            Optional[Dict[str, Any]]: The portal details if found, else None.
        """

        if utils.is_valid_uuid(portal):
            response = self.portal_client.get_portal(portal)
            return response if response else None

        response = self.portal_client.list_portals({"filter[name]": portal})

        if len(response['data']) > 1:
            self.logger.error("Multiple portals found with the name: %s. Please resolve the duplicate names manually before proceeding.", portal)
            exit(1)

        return response['data'][0] if response['data'] else None

    def delete_api_product_version(self, api_product_id: str, api_product_version_id: str) -> None:
        """
        Delete an API product version.

        Args:
            api_product_id (str): The ID of the API product.
            api_product_version_id (str): The ID of the API product version.

        Returns:
            None
        """
        self.logger.info("Deleting API product version: '%s' (%s)", api_product_version_id, api_product_version_id)
        self.api_product_client.delete_api_product_version(api_product_id, api_product_version_id)
        self.logger.info("API product version '%s' deleted successfully.", api_product_version_id)
    
    def find_portal_product_version(self, portal_id: str, product_version_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a portal product version by its ID.

        Args:
            portal_id (str): The ID of the portal.
            product_version_id (str): The ID of the product version.

        Returns:
            Optional[Dict[str, Any]]: The portal product version details if found, else None.
        """
        response = self.portal_client.list_portal_product_versions(portal_id, {"filter[product_version_id]": product_version_id})
        return response['data'][0] if response['data'] else None

    def unpublish_api_product(self, api_title: str, portal_id: str) -> None:
        """
        Unpublish an API product.

        Args:
            api_title (str): The title of the API product.
            portal_id (str): The ID of the portal.

        Returns:
            None
        """
        api_product = self.find_api_product_by_name(api_title)
        if api_product:
            self.logger.info("Unpublishing API product: '%s' (%s)", api_product['name'], api_product['id'])
            new_portal_ids = [portal['portal_id'] for portal in api_product['portals'] if portal['portal_id'] != portal_id]
            self.api_product_client.update_api_product(api_product['id'], {"portal_ids": new_portal_ids})
            self.logger.info("API product '%s' unpublished successfully.", api_title)
        else:
            self.logger.warning("API product '%s' not found. Nothing to unpublish.", api_title)

    def upsert_api_product(self, api_title: str, api_description: str, portal_ids: List[str]) -> Dict[str, Any]:
        """
        Create or update an API product.

        Args:
            api_title (str): The title of the API product.
            api_description (str): The description of the API product.
            portal_ids (List[str]): The list of portal IDs.
            unpublish (bool): Whether to unpublish the API product.

        Returns:
            Dict[str, Any]: The API product details.
        """

        self.logger.info("Processing API product")
        existing_api_product = self.find_api_product_by_name(api_title)

        if existing_api_product:
            if existing_api_product['description'] != api_description or existing_api_product['portal_ids'] != portal_ids:
                
                if set(existing_api_product['portal_ids']) != set(portal_ids):
                    self.logger.info("Updating portals for API product '%s'.", api_title)
                    self.logger.info("Publishing to portals: %s", [pid for pid in portal_ids if pid not in existing_api_product['portal_ids']])
                    self.logger.info("Unpublishing from portals: %s", [pid for pid in existing_api_product['portal_ids'] if pid not in portal_ids])
                   

                api_product = self.update_api_product(
                    existing_api_product['id'],
                    {
                        "name": api_title,
                        "description": api_description,
                        "portal_ids": portal_ids
                    }
                )
            else:
                api_product = existing_api_product
                self.logger.info("No changes detected for API product")
        else:
            api_product = self.create_api_product(
                {
                    "name": api_title,
                    "description": api_description,
                    "portal_ids": portal_ids
                }
            )
        
        return api_product
    
    def create_or_update_api_product(self, api_title: str, api_description: str, portal_id: str, unpublish: bool) -> Dict[str, Any]:
        """
        Create or update an API product.

        Args:
            api_title (str): The title of the API product.
            api_description (str): The description of the API product.
            portal_id (str): The ID of the portal.
            unpublish (bool): Whether to unpublish the API product.

        Returns:
            Dict[str, Any]: The API product details.
        """
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

        self.logger.info("%s API product: %s (%s)", action, api_product['name'], api_product['id'])
        self.logger.debug(json.dumps(api_product, indent=2))
        return api_product

    def upsert_api_product_version(self, api_product: Dict[str, Any], version_name: str, gateway_service: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create or update an API product version.

        Args:
            api_product (Dict[str, Any]): The API product details.
            version_name (str): The name of the API product version.
            gateway_service (Optional[Dict[str, str]]): The gateway service details.

        Returns:
            Dict[str, Any]: The API product version details.
        """
        self.logger.info("Processing API Product Version: %s", version_name)

        existing_api_product_version = self.find_api_product_version_by_name(api_product['id'], version_name)
        if existing_api_product_version:
            needs_update = (
                gateway_service and (
                    existing_api_product_version['gateway_service'] is None or
                    gateway_service['id'] != existing_api_product_version['gateway_service'].get('id') or
                    gateway_service['control_plane_id'] != existing_api_product_version['gateway_service'].get('control_plane_id')
                )
            ) or (
                not gateway_service and existing_api_product_version['gateway_service'] is not None
            )

            if needs_update:
                update_data = {
                    "name": version_name,
                    "gateway_service": gateway_service
                }
                api_product_version = self.api_product_client.update_api_product_version(
                    api_product['id'],
                    existing_api_product_version['id'],
                    update_data
                )
                action = "Updated"
            else:
                api_product_version = existing_api_product_version
                action = "No changes detected for"
        else:
            create_data = {
                "name": version_name,
                "gateway_service": gateway_service
            }
            api_product_version = self.api_product_client.create_api_product_version(
                api_product['id'],
                create_data
            )
            action = "Created new"

        self.logger.info("%s API Product Version: %s (%s)", action, api_product_version['name'], api_product_version['id'])
        self.logger.debug(json.dumps(api_product_version, indent=2))
        return api_product_version

    def upsert_api_product_version_spec(self, api_product_id: str, api_product_version_id: str, oas_file_base64: str) -> Dict[str, Any]:
        """
        Create or update an API product version spec.

        Args:
            api_product_id (str): The ID of the API product.
            api_product_version_id (str): The ID of the API product version.
            oas_file_base64 (str): The base64 encoded OpenAPI Specification file.

        Returns:
            Dict[str, Any]: The API product version spec details.
        """
        self.logger.info("Processing API Product Version Spec")

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

        self.logger.info("%s API Product Version Spec: %s", action, api_product_version_id)
        self.logger.debug(json.dumps(api_product_version_spec, indent=2))
        return api_product_version_spec

    def deprecate_portal_product_version(self, portal_id: str, api_product_name: str, api_product_version_name: str) -> None:
        """
        Deprecate a portal product version.

        Args:
            portal_id (str): The ID of the portal.
            api_product_name (str): The name of the API product.
            api_product_version_name (str): The name of the API product version.

        Returns:
            None
        """
        portal = self.portal_client.get_portal(portal_id)
        if portal:
            api_product = self.find_api_product_by_name(api_product_name)
            if api_product:
                api_product_version = self.find_api_product_version_by_name(api_product['id'], api_product_version_name)
                if api_product_version:
                    if api_product_version['deprecated']:
                        self.logger.info("API product version '%s' is already deprecated. Nothing to do.", api_product_version_name)
                        return
                    self.portal_client.update_portal_product_version(
                        portal['id'],
                        api_product_version['id'],
                        {
                            "deprecated": True
                        }
                    )
                    self.logger.info("Portal Product Version '%s' for '%s' on '%s' deprecated successfully.", api_product_version_name, api_product_name, portal['name'])
                else:
                    self.logger.warning("API product version '%s' not found. Nothing to deprecate.", api_product_version_name)
            else:
                self.logger.warning("API product '%s' not found. Nothing to deprecate.", api_product_name)
        else:
            self.logger.warning("Portal '%s' not found. Nothing to deprecate.", portal['name'])
    
    def unpublish_portal_product_version(self, portal_id: str, api_product_name: str, api_product_version_name: str) -> None:
        """
        Unpublish a portal product version.

        Args:
            portal_name (str): The name of the portal.
            api_product_name (str): The name of the API product.
            api_product_version_name (str): The name of the API product version.

        Returns:
            None
        """
        portal = self.portal_client.get_portal(portal_id)
        if portal:
            api_product = self.find_api_product_by_name(api_product_name)
            if api_product:
                api_product_version = self.find_api_product_version_by_name(api_product['id'], api_product_version_name)
                if api_product_version:
                    if api_product_version['publish_status'] == "unpublished":
                        self.logger.info("API product version '%s' is already unpublished. Nothing to do.", api_product_version_name)
                        return
                    self.portal_client.update_portal_product_version(
                        portal['id'],
                        api_product_version['id'],
                        {
                            "publish_status": "unpublished"
                        }
                    )
                    self.logger.info("Portal Product Version '%s' for '%s' on '%s' unpublished successfully.", api_product_version_name, api_product_name, portal['name'])
                else:
                    self.logger.warning("API product version '%s' not found. Nothing to unpublish.", api_product_version_name)
            else:
                self.logger.warning("API product '%s' not found. Nothing to unpublish.", api_product_name)
        else:
            self.logger.warning("Portal '%s' not found. Nothing to unpublish.", portal['name'])
    
    def upsert_portal_product_version(self, portal: Dict[str, Any], api_product_version: Dict[str, Any], api_product: Dict[str, Any], options: Dict[str, Any]) -> None:
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
            self.logger.info("Publishing Portal Product Version '%s' for '%s' on '%s'", api_product_version['name'], api_product['name'], portal['name'])
        else:
            self.logger.info("Unpublishing Portal Product Version '%s' for '%s' on '%s'", api_product_version['name'], api_product['name'], portal['name'])

        if deprecated:
            self.logger.info("Deprecating Portal Product Version '%s' for '%s' on '%s'", api_product_version['name'], api_product['name'], portal['name'])

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
                self.logger.info("Portal Product Version '%s' for '%s' on '%s' is up to date.", api_product_version['name'], api_product['name'], portal['name'])
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

        self.logger.info("%s Portal Product Version '%s' for '%s' on '%s'", action, api_product_version['name'], api_product['name'], portal['name'])

    def delete_api_product(self, identifier: str) -> None:
        """
        Delete an API product by its name.

        Args:
            api_name (str): The name of the API product.

        Returns:
            None
        """

        if utils.is_valid_uuid(identifier):
            api_product = self.find_api_product_by_id(identifier)
        else:
            api_product = self.find_api_product_by_name(identifier)

        if api_product:
            self.logger.info("Deleting API product: '%s' (%s)", api_product['name'], api_product['id'])
            self.api_product_client.delete_api_product(api_product['id'])
            self.logger.info("API product '%s' deleted successfully.", api_product['name'])
        else:
            self.logger.warning("API product '%s' not found. Nothing to delete.", api_product['name'])
        
    def _sync_pages(self, local_pages: List[Dict[str, str]], remote_pages: List[Dict[str, str]], api_product_id: str) -> None:
        """
        Sync local pages with remote pages.

        Args:
            local_pages (List[Dict[str, str]]): The list of local pages.
            remote_pages (List[Dict[str, str]]): The list of remote pages.
            api_product_id (str): The ID of the API product.

        Returns:
            None
        """
        slug_to_id = {page['slug']: page['id'] for page in remote_pages}

        # Handle creation and updates
        for page in local_pages:
            parent_id = slug_to_id.get(page['parent_slug']) if page['parent_slug'] else None
            existing_page_from_list = next((p for p in remote_pages if get_slug_tail(p['slug']) == get_slug_tail(page['slug'])), None)

            existing_page = self.api_product_client.get_api_product_document(api_product_id, existing_page_from_list['id']) if existing_page_from_list else None

            if not existing_page:
                self.logger.info("Creating document: '%s' (%s)", page['title'], page['slug'])
                page = self.api_product_client.create_api_product_document(api_product_id, {
                    "slug": page['slug'],
                    "title": page['title'],
                    "content": page['content'],
                    "status":  page['status'],
                    "parent_document_id": parent_id
                })
                slug_to_id[page['slug']] = page['id']
            elif utils.encode_content(existing_page['content']) != page['content'] or existing_page.get('parent_document_id') != parent_id or existing_page.get('status') != page['status']:
                self.logger.info("Updating document: '%s' (%s)", page['title'], page['slug'])
                self.api_product_client.update_api_product_document(api_product_id, existing_page['id'], {
                    "slug": page['slug'],
                    "title": page['title'],
                    "content": page['content'],
                    "status": page['status'],
                    "parent_document_id": parent_id
                })
            else:
                self.logger.info("No changes detected for document: '%s' (%s)", page['title'], page['slug'])

        # Handle deletions
        local_slugs = {page['slug'] for page in local_pages}
        remote_pages_sorted = sorted(remote_pages, key=lambda x: x['slug'].count('/'), reverse=True)
        for remote_page in remote_pages_sorted:
            if get_slug_tail(remote_page['slug']) not in local_slugs:
                self.logger.warning("Deleting page: '%s' (%s)", remote_page['title'], remote_page['slug'])
                self.api_product_client.delete_api_product_document(api_product_id, remote_page['id'])

    def sync_api_product_documents(self, api_product_id: str, directory: str) -> Dict[str, Any]:
        """
        Sync API product documents from a local directory.

        Args:
            api_product_id (str): The ID of the API product.
            directory (str): The local directory containing the documents.

        Returns:
            Dict[str, Any]: The result of the synchronization.
        """
        directory = os.path.join(os.getcwd(), directory)
        local_pages = parse_directory(directory)

        existing_documents = self.api_product_client.list_api_product_documents(api_product_id)
        remote_pages = existing_documents['data']

        self.logger.info("Processing documents in '%s'", directory)
        self._sync_pages(local_pages, remote_pages, api_product_id)
