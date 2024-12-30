"""
Main module for kptl.
"""

import argparse
import os
import sys
from typing import Callable, Dict, List
import yaml
from kptl import __version__
from kptl.config import constants, logger
from kptl.konnect.api import KonnectApi
from kptl.konnect.models.schema import ApiProductPortal, GatewayService, ApiProduct, ApiProductState, ApiProductVersionPortal, ApiProductVersion
from kptl.helpers import utils, api_product_documents
from kptl.commands import DiffCommand, DeleteCommand, ExplainCommand
import json
from deepdiff import DeepDiff, Delta
import difflib
import dataclasses
import copy

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logger.Logger(name=constants.APP_NAME, level=LOG_LEVEL)

def sync_command(args, konnect: KonnectApi) -> None:
    """
    Sync the API product with Konnect.
    """
    state_content = utils.read_file_content(args.state)
    state_parsed = yaml.safe_load(state_content)
    product_state = ApiProductState().from_dict(state_parsed)

    logger.info("Product info: %s", dataclasses.asdict(product_state.info))

    konnect_portals = [find_konnect_portal(konnect, p.portal_id if p.portal_id else p.portal_name) for p in product_state.portals]

    published_portal_ids = filter_published_portal_ids(product_state.portals, konnect_portals)

    api_product = konnect.upsert_api_product(product_state.info.name, product_state.info.description, published_portal_ids)

    if product_state.documents.sync and product_state.documents.directory:
        konnect.sync_api_product_documents(api_product['id'], product_state.documents.directory)

    handle_product_versions(konnect, product_state, api_product, konnect_portals)

def handle_product_versions(konnect: KonnectApi, product_state: ApiProductState, api_product: Dict[str, any], konnect_portals: List[Dict[str, any]]) -> None:
    """
    Handle the versions of the API product.
    """
    handled_versions = []
    for version in product_state.versions:
        oas_data, oas_data_base64 = utils.load_oas_data(version.spec)
        version_name = version.name or oas_data.get('info').get('version')
        gateway_service = create_gateway_service(version.gateway_service)

        handled_versions.append(version_name)
        
        api_product_version = konnect.upsert_api_product_version(
            api_product=api_product,
            version_name=version_name,
            gateway_service=gateway_service
        )

        konnect.upsert_api_product_version_spec(api_product['id'], api_product_version['id'], oas_data_base64)

        for version_portal in version.portals:
            konnect_portal = next((portal for portal in konnect_portals if portal['id'] == version_portal.portal_id or portal['name'] == version_portal.portal_name), None)
            if konnect_portal:
                manage_portal_product_version(konnect, konnect_portal, api_product, api_product_version, version_portal)
            else:
                logger.warning("Skipping version '%s' operations on '%s' - API product not published on this portal", version_name, version_portal.portal_name)

        delete_unused_portal_versions(konnect, product_state, version, api_product_version, konnect_portals)
        
    delete_unused_product_versions(konnect, api_product, handled_versions)

def delete_unused_portal_versions(konnect: KonnectApi, product_state: ApiProductState, version: ApiProductVersion, api_product_version: Dict[str, any], konnect_portals: List[ApiProductVersionPortal]) -> None:
    """
    Delete unused portal versions.
    """
    for portal in product_state.portals:
        if portal.portal_name not in [p.portal_name for p in version.portals]:
            portal_id = next((p['id'] for p in konnect_portals if p['name'] == portal.portal_name), None)
            konnect.delete_portal_product_version(portal_id, api_product_version['id'])

def create_gateway_service(gateway_service) -> dict:
    """
    Create a gateway service.
    """
    if gateway_service.id and gateway_service.control_plane_id:
        return {
            "id": gateway_service.id,
            "control_plane_id": gateway_service.control_plane_id
        }
    return None

def delete_unused_product_versions(konnect: KonnectApi, api_product, handled_versions) -> None:
    """
    Delete unused versions of the API product.
    """
    existing_api_product_versions = konnect.list_api_product_versions(api_product['id'])
    for existing_version in existing_api_product_versions:
        if existing_version['name'] not in handled_versions:
            konnect.delete_api_product_version(api_product['id'], existing_version['id'])

def manage_portal_product_version(konnect: KonnectApi, konnect_portal: dict, api_product: dict, api_product_version: dict, version_portal: ApiProductVersionPortal) -> None:
    """
    Manage the portal product version.
    """
    options = {
        "deprecated": version_portal.deprecated,
        "publish_status": version_portal.publish_status,
        "application_registration_enabled": version_portal.application_registration_enabled,
        "auto_approve_registration": version_portal.auto_approve_registration,
        "auth_strategy_ids": [strategy['id'] for strategy in version_portal.auth_strategies]
    }

    konnect.upsert_portal_product_version(
        portal=konnect_portal,
        api_product_version=api_product_version,
        api_product=api_product,
        options=options
    )

def filter_published_portal_ids(product_portals: list[ApiProductVersionPortal], konnect_portals) -> list[str]:
    """
    Filter the published portal IDs.
    """
    portal_ids = [p['id'] for p in konnect_portals]
    return [portal_ids[i] for i in range(len(portal_ids)) if product_portals[i]]

def get_parser_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Konnect Dev Portal Ops CLI",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=100),
        allow_abbrev=False
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--config", type=str, help="Path to the CLI configuration file")
    common_parser.add_argument("--konnect-token", type=str, help="The Konnect spat or kpat token")
    common_parser.add_argument("--konnect-url", type=str, help="The Konnect API server URL")
    common_parser.add_argument("--http-proxy", type=str, help="HTTP Proxy URL", default=None)
    common_parser.add_argument("--https-proxy", type=str, help="HTTPS Proxy URL", default=None)

    deploy_parser = subparsers.add_parser('sync', help='Sync API product with Konnect', parents=[common_parser])
    deploy_parser.add_argument("state", type=str, help="Path to the API product state file")

    deploy_parser = subparsers.add_parser('diff', help='Diff API product with Konnect', parents=[common_parser])
    deploy_parser.add_argument("state", type=str, help="Path to the API product state file")

    delete_parser = subparsers.add_parser('delete', help='Delete API product', parents=[common_parser])
    delete_parser.add_argument("product", type=str, help="The name or ID of the API product to delete")
    delete_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    describe_parser = subparsers.add_parser('explain', help='Explain the actions that will be performed on Konnect')
    describe_parser.add_argument("state", type=str, help="Path to the API product state file")

    return parser.parse_args()

def find_konnect_portal(konnect: KonnectApi, identifier: str) -> dict:
    """
    Find the Konnect portal by name or id.
    """
    try:
        portal = konnect.find_portal(identifier)
        logger.info("Fetching Portal information for '%s'", identifier)

        if not portal:
            logger.error("Portal with name %s not found", identifier)
            sys.exit(1)

        return portal
    except Exception as e:
        logger.error("Failed to get Portal information: %s", str(e))
        sys.exit(1)

def main() -> None:
    """
    Main function for the kptl module.
    """
    args = get_parser_args()

    if args.command == 'explain':
        ExplainCommand().execute(args)
        sys.exit(0)

    config = utils.read_config_file(args.config)
    
    konnect = KonnectApi(
        token= args.konnect_token if args.konnect_token else config.get("konnect_token"),
        base_url=args.konnect_url if args.konnect_url else config.get("konnect_url"),
        proxies={
            "http": args.http_proxy if args.http_proxy else config.get("http_proxy"),
            "https": args.https_proxy if args.https_proxy else config.get("https_proxy")
        }
    )
    
    if args.command == 'sync':
        sync_command(args, konnect)
    elif args.command == 'diff':
        DiffCommand(konnect).execute(args)
    elif args.command == 'delete':
        DeleteCommand(konnect).execute(args)
    else:
        logger.error("Invalid command")
        sys.exit(1)

if __name__ == "__main__":
    main()
