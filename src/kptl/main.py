"""
Main module for kptl.
"""

import argparse
import os
import sys
import yaml
from kptl import logger, __version__
from kptl import constants
from kptl.konnect import KonnectApi
from kptl.konnect.state import ApiState, KonnectPortalState, ProductSpec, Portal, PortalConfig, ApplicationRegistration, ProductVersion, Version, Documents
from kptl.helpers import utils

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logger.Logger(name=constants.APP_NAME, level=LOG_LEVEL)


def deploy_command(args, konnect: KonnectApi):
    logger.info(f"Executing deploy command")
    state = load_deploy_state(args.state)

    oas_data, oas_data_base64 = load_oas_data(state.get('info').get('spec'))

    product = create_product_spec(state.get('product'), state.get('info').get('spec'))

    logger.info(f"API Product info: %s", oas_data['info'])

    portals = [find_konnect_portal(konnect, p.name) for p in product.portals]
    published_portal_ids = filter_published_portal_ids(product, portals)

    api_product = upsert_api_product(konnect, oas_data, published_portal_ids)
    api_product_version = manage_api_product_version(konnect, api_product, oas_data, product.version)

    konnect.create_or_update_api_product_version_spec(api_product['id'], api_product_version['id'], oas_data_base64)

    if product.documents.sync and product.documents.dir:
        konnect.sync_api_product_documents(api_product['id'], product.documents.dir)

    for p in product.portals:
        portal = next((portal for portal in portals if portal['name'] == p.name), None)
        logger.info(f"Using '{portal['name']}' ('{portal['id']}') for subsequent operations")
        manage_portal_product_version(konnect, portal, api_product, api_product_version, p.config)

def load_deploy_state(state_file: str) -> dict:
    contents = utils.read_file_content(state_file)
    return yaml.safe_load(contents)

def load_oas_data(spec_file: str) -> tuple:
    oas_file = utils.read_file_content(spec_file)
    oas_data = parse_yaml(oas_file)
    oas_data_base64 = utils.encode_content(oas_file)
    return oas_data, oas_data_base64

def create_product_spec(product_state: dict, spec: str) -> ProductSpec:
    return ProductSpec(
        spec=spec,
        version=Version(gateway=product_state.get('version', {}).get('gateway')),
        documents=Documents(sync=product_state.get('documents').get('sync'), dir=product_state.get('documents').get('dir')),
        portals=[
            Portal(
                name=p.get('name'),
                config=PortalConfig(
                    publish_status=p.get('config', {}).get('publish_status', "published"),
                    auth_strategy_ids=p.get('config', {}).get('auth_strategy_ids', []),
                    application_registration=ApplicationRegistration(
                        enabled=p.get('config', {}).get('application_registration', {}).get('enabled', False),
                        auto_approve=p.get('config', {}).get('application_registration', {}).get('auto_approve', False)
                    ),
                    product_version=ProductVersion(
                        deprecate=p.get('config', {}).get('product_version', {}).get('deprecate', False),
                        publish_status=p.get('config', {}).get('product_version', {}).get('publish_status', "published")
                    )
                )
            ) for p in product_state.get('portals', [])
        ]
    )

def upsert_api_product(konnect: KonnectApi, oas_data: dict, published_portal_ids: list) -> dict:
    return konnect.upsert_api_product(oas_data['info']['title'], oas_data['info']['description'], published_portal_ids)

def manage_api_product_version(konnect: KonnectApi, api_product: dict, oas_data: dict, version: Version) -> dict:
    gateway_service = None
    if version.gateway and version.gateway.get('service_id') and version.gateway.get('control_plane_id'):
        gateway_service = {
            "id": version.gateway['service_id'],
            "control_plane_id": version.gateway['control_plane_id']
        }
    return konnect.create_or_update_api_product_version(
        api_product=api_product,
        version_name=oas_data['info']['version'],
        gateway_service=gateway_service
    )

def manage_portal_product_version(konnect: KonnectApi, portal: dict, api_product: dict, api_product_version: dict, config: PortalConfig):
    options = {
        "deprecated": config.product_version.deprecate,
        "publish_status": config.product_version.publish_status,
        "application_registration_enabled": config.application_registration.enabled,
        "auto_approve_registration": config.application_registration.auto_approve,
        "auth_strategy_ids": config.auth_strategy_ids
    }
    konnect.create_or_update_portal_product_version(
        portal=portal,
        api_product_version=api_product_version,
        api_product=api_product,
        options=options
    )

def filter_published_portal_ids(product, portals):
    portal_ids = [p['id'] for p in portals]

    # Only keep the portal ids that correspont to the portals in the state where product.portal publish_status is "published"
    portal_ids = [portal_ids[i] for i in range(len(portal_ids)) if product.portals[i].config.publish_status == "published"]
    return portal_ids

def display_header_message(message):
    logger.info("#" * len(message))
    logger.info(message)
    logger.info("#" * len(message))

def delete_command(args, konnect: KonnectApi):
    logger.info(f"Executing delete command")
    if should_delete_api_product(args, args.name):
        delete_api_product(konnect, args.name)

def sync_command(args, konnect: KonnectApi, state: ApiState):
    logger.info(f"Executing sync command")

    portal = find_konnect_portal(konnect, args.konnect_portal)

    # API Product management
    unpublish_product = state.metadata.product_publish == False
    api_product = konnect.create_or_update_api_product(state.title, state.description, portal['id'], unpublish_product)

    # API Product Documents management
    if args.documents_dir:
        konnect.sync_api_product_documents(api_product['id'], args.documents_dir)
    elif state.metadata.documents_sync and state.metadata.documents_dir:
        konnect.sync_api_product_documents(api_product['id'], state.metadata.documents_dir)

    # API Product Version management
    gateway_service = None
    if state.metadata.gateway_service_id and state.metadata.gateway_control_plane_id:
        gateway_service = {
            "id": state.metadata.gateway_service_id,
            "control_plane_id": state.metadata.gateway_control_plane_id
        }
    
    api_product_version = konnect.create_or_update_api_product_version(
        api_product=api_product,
        version_name=state.version,
        gateway_service=gateway_service
    )
    
    # API Product Version Spec management
    konnect.create_or_update_api_product_version_spec(api_product['id'], api_product_version['id'], state.spec_base64)
    
    # Portal Product Version management
    version_publish_status = "unpublished" if state.metadata.version_publish == False else "published"
    options = {
            "deprecated": state.metadata.version_deprecate,
            "publish_status": version_publish_status,
            "application_registration_enabled": state.metadata.application_registration_enabled,
            "auto_approve_registration": state.metadata.application_registration_auto_approve,
            "auth_strategy_ids": state.metadata.auth_strategy_ids
        }

    konnect.create_or_update_portal_product_version(
        portal=portal,
        api_product_version=api_product_version,
        api_product=api_product,
        options=options
    )

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

    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--config", type=str, help="Path to the CLI configuration file")
    common_parser.add_argument("--konnect-token", type=str, help="The Konnect spat or kpat token", required="--config" not in sys.argv)
    common_parser.add_argument("--konnect-url", type=str, help="The Konnect API server URL", required="--config" not in sys.argv)
    common_parser.add_argument("--http-proxy", type=str, help="HTTP Proxy URL", default=None)
    common_parser.add_argument("--https-proxy", type=str, help="HTTPS Proxy URL", default=None)

    # Sync command arguments
    sync_parser = subparsers.add_parser('sync', help='Synchronize the API state with the portal', parents=[common_parser])
    sync_parser.add_argument("spec", type=argparse.FileType('r'),
        nargs='?',
        default=sys.stdin, help="Open API Specification (default: stdin)")
    sync_parser.add_argument("--konnect-portal", type=str, required=True, help="The name or id the Konnect portal to perform operations on")
    sync_parser.add_argument("--konnect-portal-state", type=str, help="Path to the portal state file (default: x-konnect-portal-state in the OAS file)")
    sync_parser.add_argument("--documents-dir", type=str, help="Path to the documents folder", default=None)
    sync_parser.add_argument("--gateway-service-id", type=str, help="The id of the gateway service to link to the API product version", required="--gateway-service-control-plane-id" in sys.argv)
    sync_parser.add_argument("--gateway-service-control-plane-id", type=str, help="The id of the gateway service control plane to link to the API product version", required="--gateway-service-id" in sys.argv)
    sync_parser.add_argument("--application-registration-enabled", action="store_true", help="Enable application registration for the API product on the specified portal")
    sync_parser.add_argument("--auto-aprove-registration", action="store_true", help="Auto approve application registration for the API product on the specified portal")
    sync_parser.add_argument("--auth-strategy-ids", type=str, help="Comma separated list of auth strategy IDs to associate with the API product on the specified portal")
    sync_parser.add_argument("--deprecate", action="store_true", help="Deprecate the API product version on the specified portal")
    sync_parser.add_argument("--unpublish", action="append", choices=["product", "version"], help="Unpublish the API product or version from the specified portal")

    # Deploy command arguments
    deploy_parser = subparsers.add_parser('deploy', help='Deploy the API product', parents=[common_parser])
    deploy_parser.add_argument("state", type=str, help="Path to the API product state file")

    # Delete command arguments
    delete_parser = subparsers.add_parser('delete', help='Delete API product', parents=[common_parser])
    delete_parser.add_argument("name", type=str, help="The name of the API product to delete")
    delete_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    return parser.parse_args()

def confirm_deletion(api_name: str) -> bool:
    """
    Confirm deletion of the API product.
    """
    confirmation = input(f"Are you sure you want to delete the API product '{api_name}'? This action cannot be undone. (yes/No): ")
    return confirmation.strip().lower() == 'yes'

def delete_api_product(konnect: KonnectApi, api_name: str) -> None:
    """
    Delete the API product.
    """
    try:
        konnect.delete_api_product(api_name)
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

def load_state(args: argparse.Namespace) -> ApiState:
    """
    Read the OAS document and return the API state.
    """
    oas_file = read_spec_file(args.spec)
    oas_data = parse_yaml(oas_file)
    konnect_portal_state: KonnectPortalState = load_konnect_portal_state(args, oas_data)

    api_info = extract_api_info(oas_data)
    oas_file_base64 = utils.encode_content(oas_file)

    return ApiState(
        title=api_info['title'],
        description=api_info['description'],
        version=api_info['version'],
        spec_base64=oas_file_base64,
        metadata=konnect_portal_state
    )

def read_spec_file(spec) -> str:
    """
    Read the OAS file content.
    """
    try:
        return spec.read()
    except Exception as e:
        logger.error(f"Error reading OAS file: {str(e)}")
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

def load_konnect_portal_state(args: argparse.Namespace, yaml_data: dict) -> KonnectPortalState:
    """
    Load Konnect portal state from file or YAML data.
    """
    try:
        if args.konnect_portal_state:
            konnect_portal_state_file = utils.read_file_content(args.konnect_portal_state)
            return KonnectPortalState(args, yaml.safe_load(konnect_portal_state_file))
        else:
            return KonnectPortalState(args, yaml_data.get('x-konnect-portal-state') or {})
    except Exception as e:
        logger.error(f"Error loading Konnect portal state: {str(e)}")
        sys.exit(1)

def extract_api_info(yaml_data: dict) -> dict:
    """
    Extract API information from YAML data.
    """
    api_info = yaml_data.get('info') or {}
    if not api_info.get('title') or not api_info.get("description") or not api_info.get("version"):
        logger.error("API title, version, and description must be provided in the spec")
        sys.exit(1)
    return api_info

def read_config_file(config_file: str) -> dict:
    """
    Read the configuration file.
    """
    try:
        file = utils.read_file_content(config_file)
        return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error reading config file: {str(e)}")
        sys.exit(1)

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
    config = read_config_file(args.config) if args.config else {}
    
    konnect = KonnectApi(
        token= args.konnect_token if args.konnect_token else config.get("konnect_token"),
        base_url=args.konnect_url if args.konnect_url else config.get("konnect_url"),
        proxies={
            "http": args.http_proxy if args.http_proxy else config.get("http_proxy"),
            "https": args.https_proxy if args.https_proxy else config.get("https_proxy")
        }
    )

    if args.command == 'sync':
        state: ApiState = load_state(args)
        sync_command(args, konnect, state)
    elif args.command == 'delete':
        delete_command(args, konnect)
    elif args.command == 'deploy':
        deploy_command(args, konnect)
    else:
        logger.error("Invalid command")
        sys.exit(1)

if __name__ == "__main__":
    main()
