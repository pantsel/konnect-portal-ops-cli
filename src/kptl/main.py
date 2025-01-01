"""
Main module for kptl.
"""

import argparse
import os
import sys
from kptl import __version__
from kptl.config import constants, logger
from kptl.konnect.api import KonnectApi
from kptl.helpers import utils
from kptl.commands import DiffCommand, DeleteCommand, ExplainCommand, SyncCommand

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logger.Logger(name=constants.APP_NAME, level=LOG_LEVEL)


def get_parser_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Konnect Dev Portal Ops CLI",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=40, width=100),
        allow_abbrev=False
    )
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands")

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--config", type=str, help="Path to the CLI configuration file")
    common_parser.add_argument(
        "--konnect-token", type=str, help="The Konnect spat or kpat token")
    common_parser.add_argument(
        "--konnect-url", type=str, help="The Konnect API server URL")
    common_parser.add_argument(
        "--http-proxy", type=str, help="HTTP Proxy URL", default=None)
    common_parser.add_argument(
        "--https-proxy", type=str, help="HTTPS Proxy URL", default=None)

    deploy_parser = subparsers.add_parser(
        'sync', help='Sync API product with Konnect', parents=[common_parser])
    deploy_parser.add_argument(
        "state", type=str, help="Path to the API product state file")

    deploy_parser = subparsers.add_parser(
        'diff', help='Diff API product with Konnect', parents=[common_parser])
    deploy_parser.add_argument(
        "state", type=str, help="Path to the API product state file")

    delete_parser = subparsers.add_parser(
        'delete', help='Delete API product', parents=[common_parser])
    delete_parser.add_argument(
        "product", type=str, help="The name or ID of the API product to delete")
    delete_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation prompt")

    describe_parser = subparsers.add_parser(
        'explain', help='Explain the actions that will be performed on Konnect')
    describe_parser.add_argument(
        "state", type=str, help="Path to the API product state file")
    
    validate_parser = subparsers.add_parser(
        'validate', help='Validate the API product state file')
    validate_parser.add_argument(
        "state", type=str, help="Path to the API product state file")

    return parser.parse_args()


def main() -> None:
    """
    Main function for the kptl module.
    """
    args = get_parser_args()

    if args.command == 'explain':
        ExplainCommand().execute(args)
        sys.exit(0)
    elif args.command == 'validate':
        utils.load_state(args.state)
        sys.exit(0)

    config = utils.read_config_file(args.config)

    konnect = KonnectApi(
        token=args.konnect_token if args.konnect_token else config.get(
            "konnect_token"),
        base_url=args.konnect_url if args.konnect_url else config.get(
            "konnect_url"),
        proxies={
            "http": args.http_proxy if args.http_proxy else config.get("http_proxy"),
            "https": args.https_proxy if args.https_proxy else config.get("https_proxy")
        }
    )

    if args.command == 'sync':
        SyncCommand(konnect).execute(args)
    elif args.command == 'diff':
        DiffCommand(konnect).execute(args)
    elif args.command == 'delete':
        DeleteCommand(konnect).execute(args)
    else:
        logger.error("Invalid command")
        sys.exit(1)


if __name__ == "__main__":
    main()
