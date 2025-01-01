import dataclasses
import sys
from typing import Dict, List
import yaml
from kptl.config import logger
from kptl.helpers import utils
from kptl.konnect.api import KonnectApi
from kptl.konnect.models.schema import ApiProductState, ApiProductVersion, ApiProductVersionPortal


class SyncCommand:
    def __init__(self, konnect: KonnectApi):
        self.konnect = konnect
        self.logger = logger.Logger()

    def execute(self, args) -> None:
        """
        Sync the API product with Konnect.
        """
        state = utils.load_state(args.state)

        product_state = ApiProductState().from_dict(state)

        self.logger.info("Product info: %s",
                         dataclasses.asdict(product_state.info))

        konnect_portals = [self.find_konnect_portal(
            p.portal_id if p.portal_id else p.portal_name) for p in product_state.portals]

        published_portal_ids = self.filter_published_portal_ids(
            product_state.portals, konnect_portals)

        api_product = self.konnect.upsert_api_product(
            product_state.info.name, product_state.info.description, published_portal_ids)

        if product_state.documents.sync and product_state.documents.directory:
            self.konnect.sync_api_product_documents(
                api_product['id'], product_state.documents.directory)

        self.handle_product_versions(
            product_state, api_product, konnect_portals)

    def handle_product_versions(self, product_state: ApiProductState, api_product: Dict[str, any], konnect_portals: List[Dict[str, any]]) -> None:
        """
        Handle the versions of the API product.
        """
        handled_versions = []
        for version in product_state.versions:
            oas_data, oas_data_base64 = utils.load_oas_data(version.spec)
            version_name = version.name or oas_data.get('info').get('version')
            gateway_service = self.create_gateway_service(
                version.gateway_service)

            handled_versions.append(version_name)

            api_product_version = self.konnect.upsert_api_product_version(
                api_product=api_product,
                version_name=version_name,
                gateway_service=gateway_service
            )

            self.konnect.upsert_api_product_version_spec(
                api_product['id'], api_product_version['id'], oas_data_base64)

            for version_portal in version.portals:
                konnect_portal = next(
                    (portal for portal in konnect_portals if portal['id'] == version_portal.portal_id or portal['name'] == version_portal.portal_name), None)
                if konnect_portal:
                    self.manage_portal_product_version(
                        konnect_portal, api_product, api_product_version, version_portal)
                else:
                    self.logger.warning(
                        "Skipping version '%s' operations on '%s' - API product not published on this portal", version_name, version_portal.portal_name)

            self.delete_unused_portal_versions(
                product_state, version, api_product_version, konnect_portals)

        self.delete_unused_product_versions(api_product, handled_versions)

    def delete_unused_portal_versions(self, product_state: ApiProductState, version: ApiProductVersion, api_product_version: Dict[str, any], konnect_portals: List[ApiProductVersionPortal]) -> None:
        """
        Delete unused portal versions.
        """
        for portal in product_state.portals:
            if portal.portal_name not in [p.portal_name for p in version.portals]:
                portal_id = next(
                    (p['id'] for p in konnect_portals if p['name'] == portal.portal_name), None)
                self.konnect.delete_portal_product_version(
                    portal_id, api_product_version['id'])

    def create_gateway_service(self, gateway_service) -> dict:
        """
        Create a gateway service.
        """
        if gateway_service.id and gateway_service.control_plane_id:
            return {
                "id": gateway_service.id,
                "control_plane_id": gateway_service.control_plane_id
            }
        return None

    def delete_unused_product_versions(self, api_product, handled_versions) -> None:
        """
        Delete unused versions of the API product.
        """
        existing_api_product_versions = self.konnect.list_api_product_versions(
            api_product['id'])
        for existing_version in existing_api_product_versions:
            if existing_version['name'] not in handled_versions:
                self.konnect.delete_api_product_version(
                    api_product['id'], existing_version['id'])

    def manage_portal_product_version(self, konnect_portal: dict, api_product: dict, api_product_version: dict, version_portal: ApiProductVersionPortal) -> None:
        """
        Manage the portal product version.
        """
        options = {
            "deprecated": version_portal.deprecated,
            "publish_status": version_portal.publish_status,
            "application_registration_enabled": version_portal.application_registration_enabled,
            "auto_approve_registration": version_portal.auto_approve_registration,
            "auth_strategy_ids": [strategy.id for strategy in version_portal.auth_strategies]
        }

        self.konnect.upsert_portal_product_version(
            portal=konnect_portal,
            api_product_version=api_product_version,
            api_product=api_product,
            options=options
        )

    def filter_published_portal_ids(self, product_portals: list[ApiProductVersionPortal], konnect_portals) -> list[str]:
        """
        Filter the published portal IDs.
        """
        portal_ids = [p['id'] for p in konnect_portals]
        return [portal_ids[i] for i in range(len(portal_ids)) if product_portals[i]]

    def find_konnect_portal(self, identifier: str) -> dict:
        """
        Find the Konnect portal by name or id.
        """
        try:
            portal = self.konnect.find_portal(identifier)
            self.logger.info(
                "Fetching Portal information for '%s'", identifier)

            if not portal:
                self.logger.error("Portal with name %s not found", identifier)
                sys.exit(1)

            return portal
        except Exception as e:
            self.logger.error("Failed to get Portal information: %s", str(e))
            sys.exit(1)
