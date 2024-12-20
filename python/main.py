import base64
import yaml
import argparse
import os
import sys
from portal import PortalAPI
from logger import Logger

# Try to import dotenv and load the .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load environment variables
KONNECT_URL = os.getenv("KONNECT_URL")
KONNECT_TOKEN = os.getenv("KONNECT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Initialize the logger
logger = Logger(name="konnect-portal-ops", level=LOG_LEVEL)

# Initialize the argument parser
def init_arg_parser():
    parser = argparse.ArgumentParser(
        description="Konnect Dev Portal Ops CLI"
    )
    parser.add_argument(
        "--oas-spec", 
        type=str, 
        required=True, 
        help="Path to the OAS spec file"
    )
    parser.add_argument(
        "--konnect-portal-name", 
        type=str, 
        required=True, 
        help="The name of the Konnect portal to perform operations on"
    )
    parser.add_argument(
        "--konnect-token", 
        type=str, 
        help="The Konnect spat or kpat token", 
        default=KONNECT_TOKEN
    )
    parser.add_argument(
        "--konnect-url", 
        type=str, 
        help="The Konnect API server URL",
        default=KONNECT_URL
    )

    parser.add_argument(
        "--deprecate",
        action="store_true",
        help="Deprecate the API product version"
    )

    parser.add_argument(
        "--unpublish",
        action="store_true",
        help="Unpublish the API product version"
    )

    return parser

def main():
    parser = init_arg_parser()
    args = parser.parse_args()
    api = PortalAPI(args.konnect_url, args.konnect_token)

    product_version_spec = args.oas_spec
    portal_name = args.konnect_portal_name

    try:
        logger.info(f"Reading OAS file: {product_version_spec}")
        with open(product_version_spec, 'rb') as file:
            oas_file = file.read()
            yaml_data = yaml.safe_load(oas_file)

            api_name = yaml_data['info'].get('title', '').strip()
            logger.info(f"API Name: {api_name}")

            api_version = yaml_data['info'].get('version', '').strip()
            logger.info(f"API Version: {api_version}")

            api_description = yaml_data['info'].get('description', '').strip()
            logger.info(f"API Description: {api_description}")

            if not api_name or not api_version or not api_description:
                raise ValueError("API name, version, and description must be provided in the spec")
            oas_file_base64 = base64.b64encode(oas_file).decode('utf-8')
    except Exception as e:
        logger.error(f"Error reading or parsing OAS file: {str(e)}")
        sys.exit(1)

    try:
        portal = api.find_portal_by_name(portal_name)

        logger.info(f"Fetching Konnect Portal information for {portal_name}")

        if not portal:
            logger.error(f"Portal with name {portal_name} not found")
            sys.exit(1)

        portal_id = portal['id']

        logger.info(f"Using {portal_name} ({portal_id}) for subsequent operations")
    except Exception as e:
        logger.error(f"Failed to get Konnect Portal information: {str(e)}")
        sys.exit(1)

    try:
        # Create or update the API product and version
        api_product = api.create_or_update_api_product(api_name, api_description, portal_id)

        # Create or update the API product version
        api_product_version = api.create_or_update_api_product_version(api_product, api_version)

        # Create or update the API product version spec
        api.create_or_update_api_product_version_spec(api_product['id'], api_product_version['id'], oas_file_base64)

        # Create or update API product version in the portal
        publish_status = "unpublished" if args.unpublish else "published"
        api.create_or_update_portal_api_product_version(portal, api_product_version, api_product, args.deprecate, publish_status)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
