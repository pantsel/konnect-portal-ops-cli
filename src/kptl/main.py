"""
Main module for kptl.
"""

import argparse
import os
import sys
import yaml
from kptl import logger, __version__, constants
from kptl.konnect.api import KonnectApi
from kptl.konnect.models import ProductState, Portal, PortalConfig
from kptl.helpers import utils

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logger.Logger(name=constants.APP_NAME, level=LOG_LEVEL)

def sync_command(args, konnect: KonnectApi):
    state_content = utils.read_file_content(args.state)
    state_parsed = yaml.safe_load(state_content)
    product_state = ProductState().from_dict(state_parsed)

    logger.info(f"Product info: {product_state.info.to_dict()}")

    konnect_portals = [find_konnect_portal(konnect, p.id if p.id else p.name) for p in product_state.portals]

    published_portal_ids = filter_published_portal_ids(product_state.portals, konnect_portals)

    api_product = konnect.upsert_api_product(product_state.info.name, product_state.info.description, published_portal_ids)

    if product_state.documents.sync and product_state.documents.directory:
        konnect.sync_api_product_documents(api_product['id'], product_state.documents.directory)

    handle_product_versions(konnect, product_state, api_product, konnect_portals)

def handle_product_versions(konnect: KonnectApi, product_state: ProductState, api_product, konnect_portals):
    handled_versions = []
    for version in product_state.versions:
        oas_data, oas_data_base64 = load_oas_data(version.spec)
        version_name = version.name or oas_data.get('info').get('version')
        gateway_service = create_gateway_service(version.gateway_service)

        handled_versions.append(version_name)
        
        api_product_version = konnect.upsert_api_product_version(
            api_product=api_product,
            version_name=version_name,
            gateway_service=gateway_service
        )

        konnect.upsert_api_product_version_spec(api_product['id'], api_product_version['id'], oas_data_base64)

        for p in version.portals:
            portal = next((portal for portal in konnect_portals if portal['id'] == p.id or portal['name'] == p.name), None)
            if portal:
                manage_portal_product_version(konnect, portal, api_product, api_product_version, p.config)
            else:
                logger.warning(f"Skipping version '{version_name}' operations on '{p.name}' - API product not published on this portal")

        delete_unused_portal_versions(konnect, product_state, version, api_product_version, konnect_portals)
        
    delete_unused_versions(konnect, api_product, handled_versions)

def create_gateway_service(gateway_service):
    if gateway_service.id and gateway_service.control_plane_id:
        return {
            "id": gateway_service.id,
            "control_plane_id": gateway_service.control_plane_id
        }
    return None

def delete_unused_portal_versions(konnect, product_state, version, api_product_version, konnect_portals):
    for portal in product_state.portals:
        if portal.name not in [p.name for p in version.portals]:
            portal_id = next((p['id'] for p in konnect_portals if p['name'] == portal.name), None)
            konnect.delete_portal_product_version(portal_id, api_product_version['id'])

def delete_unused_versions(konnect, api_product, handled_versions):
    existing_api_product_versions = konnect.list_api_product_versions(api_product['id'])
    for existing_version in existing_api_product_versions:
        if existing_version['name'] not in handled_versions:
            konnect.delete_api_product_version(api_product['id'], existing_version['id'])

def load_oas_data(spec_file: str) -> tuple:
    oas_file = utils.read_file_content(spec_file)
    oas_data = parse_yaml(oas_file)
    oas_data_base64 = utils.encode_content(oas_file)
    return oas_data, oas_data_base64

def manage_portal_product_version(konnect: KonnectApi, portal: dict, api_product: dict, api_product_version: dict, config: PortalConfig):

    options = {
        "deprecated": config.deprecated,
        "publish_status": config.publish_status,
        "application_registration_enabled": config.application_registration.enabled,
        "auto_approve_registration": config.application_registration.auto_approve,
        "auth_strategy_ids": config.auth_strategy_ids
    }

    konnect.upsert_portal_product_version(
        portal=portal,
        api_product_version=api_product_version,
        api_product=api_product,
        options=options
    )

def filter_published_portal_ids(product_portals: list[Portal], portals):
    portal_ids = [p['id'] for p in portals]
    return [portal_ids[i] for i in range(len(portal_ids)) if product_portals[i].config.publish_status == "published"]

def delete_command(args, konnect: KonnectApi):
    logger.info("Executing delete command")
    if should_delete_api_product(args, args.product):
        delete_api_product(konnect, args.product)

def explain_command(args):
    state_content = utils.read_file_content(args.state)
    state_parsed = yaml.safe_load(state_content)
    product_state = ProductState().from_dict(state_parsed)

    descriptions = [
        f"\nProduct Name: {product_state.info.name}",
        f"Product Description: {product_state.info.description}"
    ]

    for portal in product_state.portals:
        descriptions.append(f"Portal: {portal.name} (ID: {portal.id})")

    for version in product_state.versions:
        descriptions.extend([
            f"Version: {version.name}",
            f"  Spec File: {version.spec}",
            f"  Gateway Service ID: {version.gateway_service.id}",
            f"  Control Plane ID: {version.gateway_service.control_plane_id}"
        ])

        for portal in version.portals:
            descriptions.extend([
                f"  Portal: {portal.name} (ID: {portal.id})",
                f"    Deprecated: {portal.config.deprecated}",
                f"    Publish Status: {portal.config.publish_status}",
                f"    Application Registration Enabled: {portal.config.application_registration.enabled}",
                f"    Auto Approve Registration: {portal.config.application_registration.auto_approve}",
                f"    Auth Strategy IDs: {portal.config.auth_strategy_ids}"
            ])

    descriptions.append("\nOperations to be performed:")
    operation_count = 1
    descriptions.append(f"{operation_count}. Ensure API product '{product_state.info.name}' with description '{product_state.info.description}' exists and is up-to-date.")
    operation_count += 1

    if product_state.documents.sync and product_state.documents.directory:
        descriptions.append(f"{operation_count}. Ensure documents are synced from directory '{product_state.documents.directory}'.")
    else:
        descriptions.append(f"{operation_count}. Document sync will be skipped.")
    operation_count += 1

    for portal in product_state.portals:
        status = "published" if portal.config.publish_status == "published" else "unpublished"
        descriptions.append(f"{operation_count}. Ensure API product '{product_state.info.name}' is {status} on portal '{portal.name}' with ID '{portal.id}'.")
        operation_count += 1

    for version in product_state.versions:
        descriptions.append(f"{operation_count}. Ensure API product version '{version.name}' with spec file '{version.spec}' exists and is up-to-date.")
        operation_count += 1
        if version.gateway_service.id and version.gateway_service.control_plane_id:
            descriptions.append(f"  Ensure it is linked to Gateway Service with ID '{version.gateway_service.id}' and Control Plane ID '{version.gateway_service.control_plane_id}'.")
        for portal in version.portals:
            descriptions.extend([
                f"{operation_count}. Ensure portal product version {version.name} on portal '{portal.name}' is up-to-date with publish status '{portal.config.publish_status}'.",
                f"  - Deprecated: {portal.config.deprecated}",
                f"  - Auth Strategy IDs: {portal.config.auth_strategy_ids}",
                f"  - Application Registration Enabled: {portal.config.application_registration.enabled}",
                f"  - Auto Approve Registration: {portal.config.application_registration.auto_approve}"
            ])
            operation_count += 1

    logger.info("\n".join(descriptions))

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

    delete_parser = subparsers.add_parser('delete', help='Delete API product', parents=[common_parser])
    delete_parser.add_argument("product", type=str, help="The name or ID of the API product to delete")
    delete_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    describe_parser = subparsers.add_parser('explain', help='Explain the actions that will be performed on Konnect')
    describe_parser.add_argument("state", type=str, help="Path to the API product state file")

    return parser.parse_args()

def delete_api_product(konnect: KonnectApi, identifier: str) -> None:
    """
    Delete the API product.
    """
    try:
        konnect.delete_api_product(identifier)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def find_konnect_portal(konnect: KonnectApi, portal_name: str) -> dict:
    """
    Find the Konnect portal by name.
    """
    try:
        portal = konnect.find_portal(portal_name)
        logger.info(f"Fetching Portal information for '{portal_name}'")

        if not portal:
            logger.error(f"Portal with name {portal_name} not found")
            sys.exit(1)

        return portal
    except Exception as e:
        logger.error(f"Failed to get Portal information: {str(e)}")
        sys.exit(1)

def parse_yaml(file_content: str) -> dict:
    """
    Parse YAML content.
    """
    try:
        return yaml.safe_load(file_content)
    except Exception as e:
        logger.error(f"Error parsing YAML content: {str(e)}")
        sys.exit(1)


def read_config_file(config_file: str) -> dict:
    """
    Read the configuration file.
    """
    try:
        config_file = config_file or os.path.join(os.getenv("HOME"), ".kptl.config.yaml")
        file = utils.read_file_content(config_file)
        return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error reading config file: {str(e)}")
        sys.exit(1)

def confirm_deletion(api_name: str) -> bool:
    """
    Confirm deletion of the API product.
    """
    response = input(f"Are you sure you want to delete the API product '{api_name}'? (yes/no): ")
    return response.lower() == "yes"

def should_delete_api_product(args: argparse.Namespace, api_name: str) -> bool:
    """
    Determine if the API product should be deleted.
    """
    if not args.command == "delete":
        return False

    if not args.yes and not confirm_deletion(api_name):
        logger.info("Delete operation cancelled.")
        sys.exit(0)
    
    return True

def main() -> None:
    """
    Main function for the kptl module.
    """
    args = get_parser_args()

    if args.command == 'explain':
        explain_command(args)
        sys.exit(0)

    config = read_config_file(args.config)
    
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
    elif args.command == 'delete':
        delete_command(args, konnect)
    else:
        logger.error("Invalid command")
        sys.exit(1)

if __name__ == "__main__":
    main()
