import argparse
import sys

from kptl.config import logger
from kptl.konnect.api import KonnectApi


class DeleteCommand:
    def __init__(self, konnect: KonnectApi):
        self.konnect = konnect

    def execute(self, args: argparse.Namespace) -> None:
        """
        Execute the delete command.
        """
        logger.Logger().info("Executing delete command")
        if self.should_delete_api_product(args, args.product):
            self.konnect.delete_api_product(args.product)

    def confirm_deletion(self, api_name: str) -> bool:
        """
        Confirm deletion of the API product.
        """
        response = input(f"Are you sure you want to delete the API product '{
                         api_name}'? (yes/no): ")
        return response.lower() == "yes"

    def should_delete_api_product(self, args: argparse.Namespace, api_name: str) -> bool:
        """
        Determine if the API product should be deleted.
        """
        if not args.command == "delete":
            return False

        if not args.yes and not self.confirm_deletion(api_name):
            logger.Logger().info("Delete operation cancelled.")
            sys.exit(0)

        return True
