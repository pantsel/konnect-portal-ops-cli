"""
Module for Konnect API state classes.
"""

import argparse
from typing import Any, Dict
from kptl.helpers import utils

class KonnectPortalState:
    """
    Class representing the state of the Konnect portal.
    """
    def __init__(self, args: argparse.Namespace, data: Dict[str, Any] = None):
        if data is None:
            data = {}
        self.product_publish = not (args.unpublish and "product" in args.unpublish) and self._get_value(data, 'product.publish', True)
        self.version_publish = not (args.unpublish and "version" in args.unpublish) and self._get_value(data, 'version.publish', True)
        self.version_deprecate = args.deprecate or self._get_value(data, 'version.deprecate', False)
        self.application_registration_enabled = args.application_registration_enabled or self._get_value(data, 'application_registration.enabled', False)
        self.application_registration_auto_approve = args.auto_aprove_registration or self._get_value(data, 'application_registration.auto_approve', False)
        self.gateway_service_id = args.gateway_service_id or self._get_value(data, 'gateway.service_id', None)
        self.gateway_control_plane_id = args.gateway_service_control_plane_id or self._get_value(data, 'gateway.control_plane_id', None)
        self.auth_strategy_ids = args.auth_strategy_ids.split(",") if args.auth_strategy_ids else self._get_value(data, 'auth.strategy_ids', [])
        self.documents_sync = self._get_value(data, 'documents.sync', False)
        self.documents_dir = self._get_value(data, 'documents.dir', None)

    @staticmethod
    def _get_value(data: Dict[str, Any], key: str, default: Any) -> Any:
        keys = key.split('.')
        for k in keys:
            data = data.get(k, {})
        return data if data else default

class ApiState:
    """
    Class representing the state of an API.
    """
    def __init__(self, title: str, description: str, version: str, spec_base64: str, metadata: KonnectPortalState):
        self.title = title
        self.description = description
        self.version = version
        self.spec_base64 = spec_base64
        self.metadata = metadata

class ProductVersion:
    def __init__(self, deprecate: bool, publish_status: str):
        self.deprecate = deprecate
        self.publish_status = publish_status

class ApplicationRegistration:
    def __init__(self, enabled: bool, auto_approve: bool):
        self.enabled = enabled
        self.auto_approve = auto_approve

class PortalConfig:
    def __init__(self, deprecated: bool = False, publish_status: str = "published", auth_strategy_ids: list[str] = [], application_registration: ApplicationRegistration = ApplicationRegistration(enabled=False, auto_approve=False)):
        self.deprecated = deprecated
        self.publish_status = publish_status
        self.auth_strategy_ids = auth_strategy_ids
        self.application_registration = application_registration

class Portal:
    def __init__(self, name: str, config: PortalConfig = {}):
        self.name = name
        self.config = config

class Documents:
    def __init__(self, sync: bool, dir: str):
        self.sync = sync
        self.dir = dir

class GatewayService:
    def __init__(self, id: str = None, control_plane_id: str = None):
        self.id = id
        self.control_plane_id = control_plane_id

# class Version:
#     def __init__(self, gateway: dict[Gateway, str] = None):
#         self.gateway = gateway

# class ProductSpec:
#     def __init__(self, spec: str, version: Version = {}, documents: Documents = {}, portals: list[Portal] = []):
#         self.spec = spec
#         self.version = version
#         self.documents = documents
#         self.portals = portals

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "spec": self.spec,
#             "version": {
#                 "gateway": self.version.gateway
#             },
#             "documents": {
#                 "sync": self.documents.sync,
#                 "dir": self.documents.dir
#             },
#             "portals": [
#                 {
#                     "name": portal.name,
#                     "config": {
#                         "publish_status": portal.config.publish_status,
#                         "auth_strategy_ids": portal.config.auth_strategy_ids,
#                         "application_registration": {
#                             "enabled": portal.config.application_registration.enabled,
#                             "auto_approve": portal.config.application_registration.auto_approve
#                         },
#                         "product_version": {
#                             "deprecate": portal.config.product_version.deprecate,
#                             "publish_status": portal.config.product_version.publish_status
#                         }
#                     }
#                 } for portal in self.portals
#             ]
#         }


class ProductInfo:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class ProductVersion:
    def __init__(self, spec: str, gateway_service: GatewayService, portals: list[Portal]):
        self.spec = spec
        self.gateway_service = gateway_service
        self.portals = portals

class ProductState:
    """
    Class representing the state of a product in Konnect.
    """

    def __init__(self, info: ProductInfo = None, documents: Documents = None, portals: list[Portal] = [], versions: list[ProductVersion] = []):
        self.info = info
        self.documents = documents
        self.portals = portals
        self.versions = versions

    def fromDict(self, data: Dict[str, Any]):
        self.info = ProductInfo(
            name=data.get('info', {}).get('name'),
            description=data.get('info', {}).get('description', ""),
        )
        self.documents = Documents(
            sync=data.get('documents', {}).get('sync', False),
            dir=data.get('documents', {}).get('dir', None)
        )
        self.portals = [
            Portal(
                name=p.get('name'),
                config=PortalConfig(
                    publish_status=p.get('config', {}).get('publish_status', "published"),
                )
            ) for p in data.get('portals', [])
        ]
        self.versions = [
            ProductVersion(
                spec=v.get('spec'),
                gateway_service=GatewayService(
                    id=v.get('gateway_service', {}).get('id'),
                    control_plane_id=v.get('gateway_service', {}).get('control_plane_id')
                ),
                portals=[
                    Portal(
                        name=p.get('name'),
                        config=PortalConfig(
                            deprecated=p.get('config', {}).get('deprecated', False),
                            publish_status=p.get('config', {}).get('publish_status', "published"),
                            auth_strategy_ids=p.get('config', {}).get('auth_strategy_ids', []),
                            application_registration=ApplicationRegistration(
                                enabled=p.get('config', {}).get('application_registration', {}).get('enabled', False),
                                auto_approve=p.get('config', {}).get('application_registration', {}).get('auto_approve', False)
                            )
                        )
                    ) for p in v.get('portals', [])
                ]
            ) for v in data.get('versions', [])
        ]

        return self
# Example usage of fromJSON method
# example_data = {
#     "info": {
#         "name": "Example Product",
#         "description": "This is an example product."
#     },
#     "documents": {
#         "sync": True,
#         "dir": "examples/docs/example"
#     },
#     "portals": [
#         {
#             "name": "example_portal",
#             "config": {
#                 "publish_status": "published",
#                 "auth_strategy_ids": ["strategy1", "strategy2"],
#                 "application_registration": {
#                     "enabled": True,
#                     "auto_approve": False
#                 },
#                 "deprecated": False
#             }
#         }
#     ],
#     "versions": [
#         {
#             "spec": "example_spec",
#             "gateway_service": {
#                 "id": "gateway_id",
#                 "control_plane_id": "control_plane_id"
#             },
#             "portals": [
#                 {
#                     "name": "example_portal",
#                     "config": {
#                         "publish_status": "published",
#                         "auth_strategy_ids": ["strategy1", "strategy2"],
#                         "application_registration": {
#                             "enabled": True,
#                             "auto_approve": False
#                         },
#                         "deprecated": False
#                     }
#                 }
#             ]
#         }
#     ]
# }

# product_state = ProductState(info=None, documents=None)
# product_state.fromJSON(example_data)
# print(product_state.info.name)  # Output: Example Product
# print(product_state.documents.dir)  # Output: examples/docs/example
