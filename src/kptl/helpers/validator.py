import re
from uuid import UUID
import json


class ProductStateValidator:
    """Validator for product state schema."""

    def __init__(self, schema):
        """Initialize with schema."""
        self.schema = schema

    @staticmethod
    def is_valid_semver(version):
        """Check if the version is a valid semantic version."""
        semver_regex = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        return re.match(semver_regex, version) is not None

    def validate(self):
        """Validate the schema."""
        errors = []

        def validate_portal(portal, path):
            if not isinstance(portal, dict):
                errors.append(f"Each portal entry in '{
                              path}' must be a dictionary.")
                return False
            if 'portal_id' in portal:
                try:
                    UUID(portal['portal_id'])
                except ValueError:
                    errors.append(f"The 'portal_id' in '{
                                  path}' is not a valid UUID.")
                    return False
            elif 'portal_name' not in portal or not isinstance(portal['portal_name'], str):
                errors.append(f"The 'portal_name' in '{
                              path}' is missing or not a string.")
                return False
            return True

        def validate_version_portal(portal, path, root_portals):
            if not validate_portal(portal, path):
                return
            if 'portal_id' in portal:
                if not any(root_portal.get('portal_id') == portal['portal_id'] for root_portal in root_portals):
                    errors.append(f"The 'portal_id' in '{
                                  path}' does not match any portal in the root 'portals' list.")
            elif 'portal_name' in portal:
                if not any(root_portal.get('portal_name') == portal['portal_name'] for root_portal in root_portals):
                    errors.append(f"The 'portal_name' in '{
                                  path}' does not match any portal in the root 'portals' list.")
            if 'deprecated' in portal and not isinstance(portal['deprecated'], bool):
                errors.append(f"The 'deprecated' field in '{
                              path}' must be a boolean.")
            if 'publish_status' in portal and portal['publish_status'] not in ['published', 'unpublished']:
                errors.append(f"The 'publish_status' in '{
                              path}' must be either 'published' or 'unpublished'.")
            if 'application_registration_enabled' in portal and not isinstance(portal['application_registration_enabled'], bool):
                errors.append(f"The 'application_registration_enabled' field in '{
                              path}' must be a boolean.")
            if 'auto_approve_registration' in portal and not isinstance(portal['auto_approve_registration'], bool):
                errors.append(f"The 'auto_approve_registration' field in '{
                              path}' must be a boolean.")
            if 'auth_strategies' in portal:
                if not isinstance(portal['auth_strategies'], list):
                    errors.append(f"The 'auth_strategies' in '{
                                  path}' must be a list.")
                else:
                    for k, strategy in enumerate(portal['auth_strategies']):
                        if not isinstance(strategy, dict) or 'id' not in strategy:
                            errors.append(f"Each strategy in '{
                                          path}.auth_strategies' must be a dictionary with an 'id' field. Error at index {k}.")
                        else:
                            try:
                                UUID(strategy['id'])
                            except ValueError:
                                errors.append(f"The 'id' in '{path}.auth_strategies[{
                                              k}]' is not a valid UUID.")

        def validate_gateway_service(gateway_service, path):
            if not isinstance(gateway_service, dict):
                errors.append(f"The 'gateway_service' in '{
                              path}' must be a dictionary.")
                return
            id_present = 'id' in gateway_service and gateway_service['id'] is not None
            control_plane_id_present = 'control_plane_id' in gateway_service and gateway_service[
                'control_plane_id'] is not None
            if id_present or control_plane_id_present:
                if not id_present:
                    errors.append(f"The 'id' in '{
                                  path}.gateway_service' is required when 'control_plane_id' is defined and not None.")
                elif not isinstance(gateway_service['id'], str):
                    errors.append(f"The 'id' in '{
                                  path}.gateway_service' must be a string.")
                else:
                    try:
                        UUID(gateway_service['id'])
                    except ValueError:
                        errors.append(f"The 'id' in '{
                                      path}.gateway_service' is not a valid UUID.")
                if not control_plane_id_present:
                    errors.append(f"The 'control_plane_id' in '{
                                  path}.gateway_service' is required when 'id' is defined and not None.")
                elif not isinstance(gateway_service['control_plane_id'], str):
                    errors.append(f"The 'control_plane_id' in '{
                                  path}.gateway_service' must be a string.")
                else:
                    try:
                        UUID(gateway_service['control_plane_id'])
                    except ValueError:
                        errors.append(f"The 'control_plane_id' in '{
                                      path}.gateway_service' is not a valid UUID.")

        def validate_info(info):
            if 'name' not in info or not isinstance(info['name'], str):
                errors.append("Missing or invalid 'info.name'")
            if 'description' in info and not isinstance(info['description'], str):
                errors.append("Invalid 'info.description'")

        def validate_documents(documents):
            if 'sync' in documents and not isinstance(documents['sync'], bool):
                errors.append("Invalid 'documents.sync'")
            if documents.get('sync', False) and 'dir' not in documents:
                errors.append(
                    "Missing 'documents.dir' when 'documents.sync' is true")
            if 'dir' in documents and not isinstance(documents['dir'], str):
                errors.append("Invalid 'documents.dir'")

        def validate_versions(versions, root_portals):
            for i, version in enumerate(versions):
                if not isinstance(version, dict):
                    errors.append(
                        f"Each version entry in 'versions' must be a dictionary. Error at index {i}.")
                else:
                    if 'name' in version and not isinstance(version['name'], str):
                        errors.append(
                            f"The 'name' in 'versions[{i}]' must be a string.")
                    if 'spec' not in version or not isinstance(version['spec'], str):
                        errors.append(f"The 'spec' in 'versions[{
                                      i}]' is missing or not a string.")
                    if 'portals' in version:
                        if not isinstance(version['portals'], list):
                            errors.append(
                                f"The 'portals' in 'versions[{i}]' must be a list.")
                        else:
                            for j, portal in enumerate(version['portals']):
                                validate_version_portal(
                                    portal, f"versions[{i}].portals[{j}]", root_portals)
                    if 'gateway_service' in version:
                        validate_gateway_service(
                            version['gateway_service'], f"versions[{i}]")

        # Validate _version
        if '_version' not in self.schema or not ProductStateValidator.is_valid_semver(self.schema['_version']):
            errors.append("Invalid or missing '_version'")

        # Validate info
        if 'info' not in self.schema or not isinstance(self.schema['info'], dict):
            errors.append("Missing or invalid 'info'")
        else:
            validate_info(self.schema['info'])

        # Validate documents
        if 'documents' in self.schema:
            if not isinstance(self.schema['documents'], dict):
                errors.append("Invalid 'documents'")
            else:
                validate_documents(self.schema['documents'])

        # Validate portals
        if 'portals' in self.schema:
            if not isinstance(self.schema['portals'], list):
                errors.append("The 'portals' field must be a list.")
            else:
                root_portals = self.schema['portals']
                for i, portal in enumerate(root_portals):
                    validate_portal(portal, f"portals[{i}]")

        # Validate versions
        if 'versions' in self.schema:
            if not isinstance(self.schema['versions'], list):
                errors.append("The 'versions' field must be a list.")
            else:
                validate_versions(self.schema['versions'], root_portals)

        if errors:
            return False, errors
        return True, None
