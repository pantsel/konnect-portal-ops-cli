import base64
import yaml
import argparse
import os
import sys
from logger import Logger
from konnect import KonnectApi
import constants

# Try to import dotenv and load the .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

KONNECT_URL = os.getenv("KONNECT_URL")
KONNECT_TOKEN = os.getenv("KONNECT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = Logger(name=constants.APP_NAME, level=LOG_LEVEL)

def get_parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Konnect Dev Portal Ops CLI")
    parser.add_argument("--oas-spec", type=str, required=True, help="Path to the OAS spec file")
    parser.add_argument("--konnect-portal-name", type=str, required=not any(arg in sys.argv for arg in ["--delete"]), help="The name of the Konnect portal to perform operations on")
    parser.add_argument("--konnect-token", type=str, default=KONNECT_TOKEN, help="The Konnect spat or kpat token")
    parser.add_argument("--konnect-url", type=str, default=KONNECT_URL, help="The Konnect API server URL")
    parser.add_argument("--deprecate", action="store_true", help="Deprecate the API product version on the specified portal")
    parser.add_argument("--unpublish", action="store_true", help="Unpublish the API product version from the specified portal")
    parser.add_argument("--delete", action="store_true", help="Delete the API product and related associations from ALL portals")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompts (useful for non-interactive environments).")
    return parser.parse_args()

def confirm_deletion(api_name: str) -> bool:
    confirmation = input(f"Are you sure you want to delete the API product '{api_name}'? This action cannot be undone. (yes/No): ")
    return confirmation.strip().lower() == 'yes'

def handle_api_product_deletion(args: argparse.Namespace, konnect: KonnectApi, api_name: str) -> None:
    if not args.delete:
        return

    if not args.yes and not confirm_deletion(api_name):
        logger.info("Delete operation cancelled.")
        sys.exit(0)

    try:
        konnect.delete_api_product(api_name)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def find_konnect_portal(konnect: KonnectApi, portal_name: str) -> dict:
    try:
        portal = konnect.find_portal_by_name(portal_name)
        logger.info(f"Fetching information for {portal_name}")

        if not portal:
            logger.error(f"Portal with name {portal_name} not found")
            sys.exit(1)

        logger.info(f"Using {portal_name} ({portal['id']}) for subsequent operations")
        return portal
    except Exception as e:
        logger.error(f"Failed to get Portal information: {str(e)}")
        sys.exit(1)

def handle_api_product_publication(args: argparse.Namespace, konnect: KonnectApi, api_info: dict, oas_file_base64: str, portal: dict) -> None:
    try:
        api_product = konnect.create_or_update_api_product(api_info['title'], api_info['description'], portal['id'])
        api_product_version = konnect.create_or_update_api_product_version(api_product, api_info['version'])
        konnect.create_or_update_api_product_version_spec(api_product['id'], api_product_version['id'], oas_file_base64)
        
        publish_status = "unpublished" if args.unpublish else "published"
        konnect.create_or_update_portal_api_product_version(portal, api_product_version, api_product, args.deprecate, publish_status)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def read_oas_document(spec: str) -> tuple:
    try:
        logger.info(f"Reading OAS file: {spec}")
        with open(spec, 'rb') as file:
            oas_file = file.read()
            yaml_data = yaml.safe_load(oas_file)

            api_info = yaml_data.get('info', {})
            logger.info(f"API Info: {api_info}")

            if not api_info['title'] or not api_info["description"] or not api_info["version"]:
                raise ValueError("API name, version, and description must be provided in the spec")
            
            oas_file_base64 = base64.b64encode(oas_file).decode('utf-8')
            return api_info, oas_file_base64
    except Exception as e:
        logger.error(f"Error reading or parsing OAS file: {str(e)}")
        sys.exit(1)

def main() -> None:
    args = get_parser_args()
    konnect = KonnectApi(args.konnect_url, args.konnect_token)
    api_info, oas_file_base64 = read_oas_document(args.oas_spec)

    handle_api_product_deletion(args, konnect, api_info['title'])

    portal = find_konnect_portal(konnect, args.konnect_portal_name)

    handle_api_product_publication(args, konnect, api_info, oas_file_base64, portal)

if __name__ == "__main__":
    main()
