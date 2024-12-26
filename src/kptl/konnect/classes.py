import argparse
from typing import Any, Dict

class KonnectPortalState:
    def __init__(self, args: argparse.Namespace, data: Dict[str, Any] = {}):
        self.product_publish = self._get_value(data, 'product.publish', True)
        self.version_deprecate = self._get_value(data, 'version.deprecate', False)
        self.version_publish = self._get_value(data, 'version.publish', True)
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
    def __init__(self, title: str, description: str, version: str, spec_base64: str, metadata: KonnectPortalState):
        self.title = title
        self.description = description
        self.version = version
        self.spec_base64 = spec_base64
        self.metadata = metadata