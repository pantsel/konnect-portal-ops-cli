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
from kptl.helpers import utils

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logger.Logger(name=constants.APP_NAME, level=LOG_LEVEL)

def get_parser_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Konnect Dev Portal Ops CLI", allow_abbrev=False)
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument("--oas-spec", type=str, required=True, help="Path to the OAS spec file")
    required_args.add_argument("--konnect-portal-name", type=str, required=not any(arg in sys.argv for arg in ["--delete"]), help="The name of the Konnect portal to perform operations on")
    required_args.add_argument("--konnect-token", type=str, help="The Konnect spat or kpat token", default=None, required=not any(arg in sys.argv for arg in ["--config"]))
    required_args.add_argument("--konnect-url", type=str, help="The Konnect API server URL", default=None, required=not any(arg in sys.argv for arg in ["--config"]))
    required_args.add_argument("--config", type=str, help="Path to the CLI configuration file", required=not any(arg in sys.argv for arg in ["--konnect-token", "--konnect-url"]))

    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument("--docs", type=str, help="Path to the documents folder", default=None)
    optional_args.add_argument("--gateway-service-id", type=str, help="The id of the gateway service to link to the API product version", required="--gateway-service-control-plane-id" in sys.argv)
    optional_args.add_argument("--gateway-service-control-plane-id", type=str, help="The id of the gateway service control plane to link to the API product version", required="--gateway-service-id" in sys.argv)
    optional_args.add_argument("--deprecate", action="store_true", help="Deprecate the API product version on the specified portal")
    optional_args.add_argument("--application-registration-enabled", action="store_true", help="Enable application registration for the API product on the specified portal")
    optional_args.add_argument("--auto-aprove-registration", action="store_true", help="Auto approve application registration for the API product on the specified portal")
    optional_args.add_argument("--auth-strategy-ids", type=str, help="Comma separated list of auth strategy IDs to associate with the API product on the specified portal")
    optional_args.add_argument("--unpublish", action="append", choices=["product", "version"], help="Unpublish the API product or version from the specified portal")
    optional_args.add_argument("--delete", action="store_true", help="Delete the API product and related associations")
    optional_args.add_argument("--yes", action="store_true", help="Skip the confirmation prompts (useful for non-interactive environments).")
    optional_args.add_argument("--http-proxy", type=str, help="HTTP Proxy URL", default=None)
    optional_args.add_argument("--https-proxy", type=str, help="HTTPS Proxy URL", default=None)

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
        portal = konnect.find_portal_by_name(portal_name)
        logger.info(f"Fetching Portal information for '{portal_name}'")

        if not portal:
            logger.error(f"Portal with name {portal_name} not found")
            sys.exit(1)

        logger.info(f"Using '{portal_name}' ({portal['id']}) for subsequent operations")
        return portal
    except Exception as e:
        logger.error(f"Failed to get Portal information: {str(e)}")
        sys.exit(1)

def handle_api_product_publication(args: argparse.Namespace, konnect: KonnectApi, api_info: dict, oas_file_base64: str, portal: dict) -> None:
    """
    Handle the publication of the API product.
    """
    try:
        # API Product management
        unpublish_product = "product" in args.unpublish if args.unpublish else False
        api_product = konnect.create_or_update_api_product(api_info['title'], api_info['description'], portal['id'], unpublish_product)

        # API Product Documents management
        if args.docs:
            konnect.sync_api_product_documents(api_product['id'], args.docs)

        # API Product Version management
        gateway_service = None
        if args.gateway_service_id and args.gateway_service_control_plane_id:
            gateway_service = {
                "id": args.gateway_service_id,
                "control_plane_id": args.gateway_service_control_plane_id
            }
        
        api_product_version = konnect.create_or_update_api_product_version(
            api_product=api_product,
            version_name=api_info['version'],
            gateway_service=gateway_service
        )
        
        # API Product Version Spec management
        konnect.create_or_update_api_product_version_spec(api_product['id'], api_product_version['id'], oas_file_base64)
        
        # Portal Product Version management
        version_publish_status = "unpublished" if args.unpublish and "version" in args.unpublish else "published"
        options = {
                "deprecated": args.deprecate,
                "publish_status": version_publish_status,
                "application_registration_enabled": args.application_registration_enabled,
                "auto_approve_registration": args.auto_aprove_registration,
                "auth_strategy_ids": args.auth_strategy_ids.split(",") if args.auth_strategy_ids else []
            }

        konnect.create_or_update_portal_product_version(
            portal=portal,
            api_product_version=api_product_version,
            api_product=api_product,
            options=options
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def read_oas_document(spec: str) -> tuple:
    """
    Read the OAS document.
    """
    try:
        logger.info(f"Reading OAS file: {spec}")
        oas_file = utils.read_file_content(spec)
        yaml_data = yaml.safe_load(oas_file)
        api_info = yaml_data.get('info', {})
        logger.info(f"API Info: {api_info}")

        if not api_info['title'] or not api_info["description"] or not api_info["version"]:
            raise ValueError("API title, version, and description must be provided in the spec")

        oas_file_base64 = utils.encode_content(oas_file)
        return api_info, oas_file_base64
    except Exception as e:
        logger.error(f"Error reading or parsing OAS file: {str(e)}")
        sys.exit(1)

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
    if not args.delete:
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
    api_info, oas_file_base64 = read_oas_document(args.oas_spec)

    if should_delete_api_product(args, api_info['title']):
        delete_api_product(konnect, api_info['title'])
        sys.exit(0)

    portal = find_konnect_portal(konnect, args.konnect_portal_name)

    handle_api_product_publication(args, konnect, api_info, oas_file_base64, portal)

if __name__ == "__main__":
    main()
