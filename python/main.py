import base64
import yaml
import argparse
from dotenv import load_dotenv
import os
import sys
from portal import PortalAPI

# Load the .env file
load_dotenv()

KONNECT_URL = os.getenv("KONNECT_URL")
KONNECT_TOKEN = os.getenv("KONNECT_TOKEN")

PORTALS = {
    "dev": os.getenv("KONNECT_DEV_PORTAL_ID"),
    "prod": os.getenv("KONNECT_PROD_PORTAL_ID")
}

def init_arg_parser():
    parser = argparse.ArgumentParser(description="Process OAS spec and environment.")
    parser.add_argument("--oas_spec", type=str, help="Path to the OAS spec file")
    parser.add_argument("--environment", type=str, choices=PORTALS.keys(), help="Environment (dev or prod)")
    parser.add_argument("--konnect-token", type=str, help="The Konnect spat or kpat token", default=KONNECT_TOKEN)
    parser.add_argument("--konnect-url", type=str, help="The Konnect URL", default=KONNECT_URL)
    return parser

def main():
    parser = init_arg_parser()
    args = parser.parse_args()

    environment = args.environment
    portal_id = PORTALS[environment]
    product_version_spec = args.oas_spec
    oas_file_base64 = ""
    api = PortalAPI(args.konnect_url, args.konnect_token)

    try:
        with open(product_version_spec, 'rb') as file:
            oas_file = file.read()
            yaml_data = yaml.safe_load(oas_file)
            api_name = yaml_data['info'].get('title', '').strip()
            api_version = yaml_data['info'].get('version', '').strip()
            api_description = yaml_data['info'].get('description', '').strip()

            if not api_name or not api_version or not api_description:
                raise ValueError("API name, version, and description must be provided in the spec")
            oas_file_base64 = base64.b64encode(oas_file).decode('utf-8')
    except Exception as e:
        print(f"Error reading or parsing OAS file: {str(e)}")
        sys.exit(1)

    try:
        # Create or update the API product and version
        api_product = api.create_or_update_api_product(api_name, api_description, portal_id)

        # Create or update the API product version
        api_product_version = api.create_or_update_api_product_version(api_product['body']['id'], api_version)

        # Create or update the API product version spec
        api.create_or_update_api_product_version_spec(api_product['body']['id'], api_product_version['body']['id'], oas_file_base64)

        # Ensure the API product version is published to the portal
        api.publish_api_product_version_to_portal(portal_id, api_product_version['body']['id'], api_product_version['body']['name'], api_product['body']['name'], environment)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
