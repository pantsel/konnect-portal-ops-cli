"""
Module for diffing local and remote API product states.
"""

import argparse
import copy
import dataclasses
import difflib
import sys
from typing import Callable
from deepdiff import DeepDiff
import yaml

from kptl.config import logger
from kptl.helpers import api_product_documents, utils
from kptl.konnect.api import KonnectApi
from kptl.konnect.models.schema import ApiProduct, ApiProductPortal, ApiProductState, ApiProductVersion, ApiProductVersionAuthStrategy, ApiProductVersionPortal, GatewayService

RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"
YELLOW: Callable[[str], str] = lambda text: f"\u001b[33m{text}\033\u001b[0m"


class DiffCommand:
    """
    Command to diff local and remote API product states.
    """

    def __init__(self, konnect: KonnectApi):
        """
        Initialize the DiffCommand with a KonnectApi instance.
        """
        self.konnect = konnect

    def execute(self, args: argparse.Namespace) -> None:
        """
        Execute the diff command.
        """
        state = utils.load_state(args.state)
        local_state = ApiProductState().from_dict(state)

        should_sync_docs = local_state.documents and local_state.documents.sync and local_state.documents.directory

        if should_sync_docs:
            local_docs = api_product_documents.parse_directory(
                local_state.documents.directory)
            local_state.documents.set_data(local_docs)

        remote_state = self.load_remote_state(local_state, should_sync_docs)

        # Before the diff, there are a couple of things we need to do:
        # ============================================================

        # 1. Encode the OAS spec content for the local state versions so that it can be compared with the remote state.
        local_state.encode_versions_spec_content()

        # 2. Clean up state dictionaries in preparation for the diff.
        remote_state_dict_clean = self._prepare_for_diff(
            dataclasses.asdict(remote_state))
        local_state_dict_clean = self._prepare_for_diff(
            dataclasses.asdict(local_state))

        print(
            self._get_edits_string(
                yaml.dump(remote_state_dict_clean, indent=2, sort_keys=True),
                yaml.dump(local_state_dict_clean, indent=2, sort_keys=True)
            )
        )

        print(self._get_summary_of_changes(
            remote_state_dict_clean, local_state_dict_clean))

    def load_remote_state(self, local_state, should_sync_docs):

        remote_state = ApiProductState()

        api_product = self.konnect.find_api_product_by_name(
            local_state.info.name)

        if not api_product:
            return remote_state

        api_product['portal_ids'] = [p['portal_id']
                                     for p in api_product['portals']]

        portals = [self._find_konnect_portal(
            p['portal_id']) for p in api_product['portals']]

        if should_sync_docs:
            remote_docs = self.konnect.list_api_product_documents(
                api_product['id'])

            for doc in remote_docs:
                full_doc = self.konnect.get_api_product_document(
                    api_product['id'], doc['id'])
                doc['content'] = utils.encode_content(full_doc['content'])

            remote_state.documents.set_data(remote_docs)

        product_versions = self.konnect.list_api_product_versions(
            api_product['id'])

        remote_state.info = ApiProduct(
            name=api_product['name'],
            description=api_product['description']
        )

        remote_state.portals = sorted([ApiProductPortal(
            portal_id=p['id'],
            portal_name=p['name'],
        ) for p in portals], key=lambda portal: portal.portal_name)

        remote_state.versions = sorted([ApiProductVersion(
            name=v['name'],
            spec=self._get_encoded_api_product_version_spec_content(
                api_product['id'], v['id']),
            gateway_service=GatewayService(
                id=v['gateway_service']['id'],
                control_plane_id=v['gateway_service']['control_plane_id']
            )
            if v['gateway_service'] else GatewayService(),
            portals=sorted([ApiProductVersionPortal(
                portal_id=p['portal_id'],
                portal_name=p['portal_name'],
                publish_status=p['publish_status'],
                deprecated=p['deprecated'],
                auth_strategies=[ApiProductVersionAuthStrategy(
                    id=a['id']
                ) for a in p['auth_strategies']],
                application_registration_enabled=p['application_registration_enabled'],
                auto_approve_registration=p['auto_approve_registration']
            ) for p in v['portals']], key=lambda portal: portal.portal_name)
        ) for v in product_versions], key=lambda version: version.name)

        return remote_state

    def _get_edits_string(self, old: str, new: str) -> str:
        """
        Get the string representation of the edits between the old and new content.
        """
        result = ""

        lines = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(
            keepends=True), fromfile="before", tofile="after", n=100000)

        for line in lines:
            line = line.rstrip()
            if len(line) > 100:
                line = line[:97] + "..."
            if line.startswith("+"):
                result += GREEN(line) + "\n"
            elif line.startswith("-"):
                result += RED(line) + "\n"
            elif line.startswith("?") or line.startswith("@@"):
                continue
            else:
                result += line + "\n"

        return result

    def _get_summary_of_changes(self, old: dict, new: dict) -> str:
        """
        Get a summary of the changes between the old and new state dictionaries.
        """
        diff = DeepDiff(old, new)
        summary = {
            "added": [],
            "removed": [],
            "updated": []
        }

        if not diff:
            return "Summary:\n==================\nNo changes detected.\n"

        change_types = {
            'dictionary_item_added': 'added',
            'dictionary_item_removed': 'removed',
            'values_changed': 'updated',
            'iterable_item_added': 'added',
            'iterable_item_removed': 'removed',
            'type_changes': 'updated'
        }

        for diff_key, summary_key in change_types.items():
            if diff_key in diff:
                for key in diff[diff_key]:
                    color_func = GREEN if summary_key == 'added' else RED if summary_key == 'removed' else YELLOW
                    summary[summary_key].append(
                        color_func(f"  - {key.replace('root', '')}"))

        human_readable_summary = ""
        for change_type, items in summary.items():
            if items:
                color_func = GREEN if change_type == 'added' else RED if change_type == 'removed' else YELLOW
                human_readable_summary += color_func(
                    f"{change_type.capitalize()} ({len(items)}):\n")
                human_readable_summary += "\n".join(items) + "\n"

        return f"Summary:\n==================\n{human_readable_summary}"

    def _prepare_for_diff(self, state_dict: dict) -> dict:
        """
        Prepare the state dictionary for diffing.
        """
        new_state_dict = copy.deepcopy(state_dict)

        # Remove portal IDs from the state dictionaries to ensure they don't affect the diff.
        # Portal names are unique and portal-related lists are sorted by portal name.
        # @TODO: Maybe there's a better way to handle this.
        for portal in new_state_dict.get('portals', []):
            portal.pop('portal_id', None)
        for version in new_state_dict.get('versions', []):
            for portal in version.get('portals', []):
                portal.pop('portal_id', None)

            # Remove gateway service if it doesn't have an ID or control plane ID.
            # gateway_service = version.get('gateway_service')
            # if gateway_service and not gateway_service.get('id') and not gateway_service.get('control_plane_id'):
            #     version.pop('gateway_service', None)

        # We only need documents data (pages) to show in diff.
        if new_state_dict.get('documents', None):
            new_state_dict['documents'] = new_state_dict['documents']['data']

        return new_state_dict

    def _get_encoded_api_product_version_spec_content(self, api_product_id: str, api_product_version_id: str) -> str:
        """
        Get the encoded API product version spec.
        """
        spec = self.konnect.get_api_product_version_spec(
            api_product_id, api_product_version_id)

        if not spec:
            return ""

        return utils.encode_content(spec['content'])

    def _find_konnect_portal(self, identifier: str) -> dict:
        """
        Find the Konnect portal by name or id.
        """
        try:
            portal = self.konnect.find_portal(identifier)
            if not portal:
                logger.Logger().error("Portal with name %s not found", identifier)
                sys.exit(1)

            return portal
        except Exception as e:
            logger.Logger().error("Failed to get Portal information: %s", str(e))
            sys.exit(1)
