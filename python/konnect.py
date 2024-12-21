import json
import os
import base64
from logger import Logger
from clients import ApiProductClient, PortalManagementClient
import constants
from typing import Optional, Dict, Any
import utils
import uuid


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
        # Copy the existing portal IDs to a new list to modify it without affecting the original
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
        existing_api_product_version = self.find_api_product_version_by_name(api_product['id'], version_name)
        if existing_api_product_version:
            # if existing_api_product_version['name'] != version_name:
            #     api_product_version = self.api_product_client.update_api_product_version(
            #         api_product['id'],
            #         existing_api_product_version['id'],
            #         {"name": version_name}
            #     )
            #     action = "Updated"
            # else:
            #     api_product_version = existing_api_product_version
            #     action = "No changes detected for"

            # If a version with the same name exists, then we're done.
            api_product_version = existing_api_product_version
            action = "No changes detected for"
        else:
            api_product_version = self.api_product_client.create_api_product_version(
                api_product['id'],
                {
                    "name": version_name,
                    "labels": {"generated_by": constants.APP_NAME}
                }
            )
            action = "Created new"

        self.logger.info(f"{action} API product version: {api_product_version['name']} ({api_product_version['id']})")
        self.logger.debug(json.dumps(api_product_version, indent=2))
        return api_product_version

    def create_or_update_api_product_version_spec(self, api_product_id: str, api_product_version_id: str, oas_file_base64: str) -> Dict[str, Any]:
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
            self.logger.info(f"Publishing API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")
        else:
            self.logger.info(f"Unpublishing API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

        if deprecated:
            self.logger.info(f"Deprecating API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

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
                self.logger.info(f"API product version {api_product_version['name']} for {api_product['name']} on {portal['name']} is up to date. No further action required.")
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

        self.logger.info(f"{action} API product version {api_product_version['name']} for {api_product['name']} on {portal['name']}")

    def delete_api_product(self, api_name: str) -> None:
        api_product = self.find_api_product_by_name(api_name)
        if api_product:
            self.logger.info(f"Deleting API product: {api_product['name']} ({api_product['id']})")
            self.api_product_client.delete_api_product(api_product['id'])
            self.logger.info(f"API product {api_name} deleted successfully.")
        else:
            self.logger.warning(f"API product {api_name} not found. Nothing to delete.")
        
    def create_or_update_api_product_documents(self, api_product_id: str, directory: str) -> Dict[str, Any]:
        """
        Create or update API product documents based on the files in the specified directory.
        """
        self.logger.info(f"Processing documents in {directory}")

        def process_existing_documents(api_product_id: str, existing_slugs: Dict[str, str], data: Dict[str, Any], file_name: str) -> None:
            """
            Process existing documents to update or create new ones if necessary.
            """
            if data['slug'] in existing_slugs:
                # Retrieve the existing document using the slug
                existing_doc = self.api_product_client.get_api_product_document(api_product_id, existing_slugs[data['slug']])
                
                has_content_changed = (
                    existing_doc['title'] != data['title'] or 
                    utils.encode_content(existing_doc['content']) != data['content'] or 
                    existing_doc['status'] != data['status'] or
                    (data.get('parent_document_id') and existing_doc.get('parent_document_id') != data['parent_document_id'])
                )
                
                if has_content_changed:
                    self.logger.info(f"Updating document: {file_name}")
                    updated_doc = self.api_product_client.update_api_product_document(api_product_id, existing_slugs[data['slug']], data)
                    
                    # Update the existing_documents list with the updated document
                    for i, doc in enumerate(existing_documents['data']):
                        if doc['id'] == updated_doc['id']:
                            existing_documents['data'][i] = updated_doc
                            break
                else:
                    self.logger.info(f"No changes detected for document: {file_name}")
                
                # Remove the slug from existing_slugs to avoid deletion later
                del existing_slugs[data['slug']]
                
            else:
                self.logger.info(f"Creating document: {file_name}")
                new_doc = self.api_product_client.create_api_product_document(api_product_id, data)
                # Add the new document to existing_documents
                existing_documents['data'].append(new_doc)

        def get_parent_document_id(file_name: str, directory: str) -> Optional[str]:
            """
            Get the parent document ID based on the file name and directory.

            Args:
            file_name (str): The name of the file for which to find the parent document ID.
            directory (str): The directory where the files are located.

            Returns:
            Optional[str]: The ID of the parent document if found, otherwise None.
            """
            parent_document_id = None
            if '_' in file_name:
                # Extract the prefix from the file name (e.g., "1.1_child.md" -> "1.1")
                prefix = file_name.split('_')[0]
                if '.' in prefix:
                    # Extract the parent prefix (e.g., "1.1" -> "1")
                    parent_prefix = prefix.split('.')[0]
                    # Find the parent file name in the directory (e.g., "1_parent.md")
                    parent_file_name = next((f for f in os.listdir(directory) if f.startswith(f"{parent_prefix}_") and f.endswith(".md")), None)
                    
                    if parent_file_name:
                        # Read the content of the parent file
                        parent_content = utils.read_file_content(os.path.join(directory, parent_file_name))
                        # Generate document data for the parent file
                        parent_data = generate_document_data(parent_file_name, parent_content)
                        # Extract the slug for the parent document
                        parent_slug = parent_data['slug']
                        # Find the parent document in the existing documents
                        parent_document = next((doc for doc in existing_documents['data'] if doc['slug'] == parent_slug), None)
                        # Get the parent document ID if it exists
                        parent_document_id = parent_document['id'] if parent_document else None

                        self.logger.debug(f"File name: {file_name} | Parent Slug: {parent_slug} | Parent Document ID: {parent_document_id}")
            return parent_document_id

        def generate_document_data(file_name: str, content: str, parent_document_id: str = None) -> Dict[str, Any]:
            """
            Generate a dictionary containing document data based on the provided file name and content.

            Args:
                file_name (str): The name of the file, which may include special suffixes like '__unpublished'.
                content (str): The content of the document to be encoded.
                parent_document_id (str, optional): The ID of the parent document, if any. Defaults to None.

            Returns:
                Dict[str, Any]: A dictionary containing the document data with the following keys:
                    - 'title' (str): The title of the document, derived from the file name.
                    - 'slug' (str): The slug for the document, derived from the file name.
                    - 'content' (str): The encoded content of the document.
                    - 'status' (str): The publication status of the document, either 'unpublished' or 'published'.
                    - 'parent_document_id' (str, optional): The ID of the parent document, if provided.
            """
            title_slug = os.path.splitext(file_name)[0].replace('__unpublished', '')
            title_slug = '_'.join(title_slug.split('_')[1:]) if title_slug[0].isdigit() else title_slug
            data = {
                'title': title_slug.replace('_', ' ').replace('-', ' ').title(),
                'slug': title_slug.replace('_', '-').replace(' ', '-').lower(),
                'content': utils.encode_content(content),
                'status': "unpublished" if "__unpublished" in file_name else "published"
            }
            if parent_document_id:
                data['parent_document_id'] = parent_document_id
            return data
    
        existing_documents = self.api_product_client.list_api_product_documents(api_product_id)
        existing_slugs = {doc['slug'].split('/')[-1]: doc['id'] for doc in existing_documents['data']}
        
        for file_name in sorted(os.listdir(directory), key=utils.sort_key_for_numbered_files):
            if file_name.endswith(".md"):
                content = utils.read_file_content(os.path.join(directory, file_name))
                parent_document_id = get_parent_document_id(file_name, directory)
                data = generate_document_data(file_name, content, parent_document_id)
                process_existing_documents(api_product_id, existing_slugs, data, file_name)

        # Delete documents that are not in the input folder
        # Sort existing_documents slugs to ensure child documents are deleted before their parents
        sorted_existing_slugs = sorted(
            [(doc['slug'], doc['id']) for doc in existing_documents['data'] if doc['slug'].split('/')[-1] in existing_slugs],
            key=lambda item: item[0].count('/'),  # Sort by the number of slashes in the slug (indicating hierarchy depth)
            reverse=True  # Ensure child documents (more slashes) come before parent documents (fewer slashes)
        )

        for slug, doc_id in sorted_existing_slugs:
            self.logger.info(f"Deleting document: {slug}")
            self.api_product_client.delete_api_product_document(api_product_id, doc_id)