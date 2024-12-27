"""
Module for Konnect API state classes.
"""

from typing import Any, Dict

class ApplicationRegistration:
    """
    Class representing application registration settings.
    """
    def __init__(self, enabled: bool, auto_approve: bool):
        self.enabled = enabled
        self.auto_approve = auto_approve

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "auto_approve": self.auto_approve
        }

    def __str__(self) -> str:
        return f"ApplicationRegistration(enabled={self.enabled}, auto_approve={self.auto_approve})"

class PortalConfig:
    """
    Class representing portal configuration.
    """
    def __init__(self, deprecated: bool = False, publish_status: str = "published", auth_strategy_ids: list[str] = None, application_registration: ApplicationRegistration = None):
        if auth_strategy_ids is None:
            auth_strategy_ids = []
        if application_registration is None:
            application_registration = ApplicationRegistration(enabled=False, auto_approve=False)
        self.deprecated = deprecated
        self.publish_status = publish_status
        self.auth_strategy_ids = auth_strategy_ids
        self.application_registration = application_registration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deprecated": self.deprecated,
            "publish_status": self.publish_status,
            "auth_strategy_ids": self.auth_strategy_ids,
            "application_registration": self.application_registration.to_dict()
        }

    def __str__(self) -> str:
        return f"PortalConfig(deprecated={self.deprecated}, publish_status={self.publish_status}, auth_strategy_ids={self.auth_strategy_ids}, application_registration={self.application_registration})"

class Portal:
    """
    Class representing a portal.
    """
    def __init__(self, id: str = None, name: str = None, config: PortalConfig = None):
        if config is None:
            config = PortalConfig()
        self.id = id
        self.name = name
        self.config = config

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "config": self.config.to_dict()
        }

    def __str__(self) -> str:
        return f"Portal(name={self.name}, config={self.config})"

class Documents:
    """
    Class representing documents.
    """
    def __init__(self, sync: bool, directory: str):
        self.sync = sync
        self.directory = directory

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sync": self.sync,
            "directory": self.directory
        }

    def __str__(self) -> str:
        return f"Documents(sync={self.sync}, directory={self.directory})"

class GatewayService:
    """
    Class representing a gateway service.
    """
    def __init__(self, id: str = None, control_plane_id: str = None):
        self.id = id
        self.control_plane_id = control_plane_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "control_plane_id": self.control_plane_id
        }

    def __str__(self) -> str:
        return f"GatewayService(id={self.id}, control_plane_id={self.control_plane_id})"

class ProductInfo:
    """
    Class representing product information.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description
        }

    def __str__(self) -> str:
        return f"ProductInfo(name={self.name}, description={self.description})"

class ProductVersion:
    """
    Class representing a product version.
    """
    def __init__(self, spec: str, gateway_service: GatewayService, portals: list[Portal]):
        self.spec = spec
        self.gateway_service = gateway_service
        self.portals = portals

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec,
            "gateway_service": self.gateway_service.to_dict(),
            "portals": [portal.to_dict() for portal in self.portals]
        }

    def __str__(self) -> str:
        return f"ProductVersion(spec={self.spec}, gateway_service={self.gateway_service}, portals={self.portals})"

class ProductState:
    """
    Class representing the state of a product in Konnect.
    """
    def __init__(self, info: ProductInfo = None, documents: Documents = None, portals: list[Portal] = None, versions: list[ProductVersion] = None):
        if portals is None:
            portals = []
        if versions is None:
            versions = []
        self.info = info
        self.documents = documents
        self.portals = portals
        self.versions = versions

    def from_dict(self, data: Dict[str, Any]):
        """
        Initialize ProductState from a dictionary.
        """
        self.info = ProductInfo(
            name=data.get('info', {}).get('name'),
            description=data.get('info', {}).get('description', ""),
        )
        self.documents = Documents(
            sync=data.get('documents', {}).get('sync', False),
            directory=data.get('documents', {}).get('dir', None)
        )
        self.portals = [
            Portal(
                id=p.get('id'),
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
                        id=p.get('id'),
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "info": self.info.to_dict() if self.info else None,
            "documents": self.documents.to_dict() if self.documents else None,
            "portals": [portal.to_dict() for portal in self.portals],
            "versions": [version.to_dict() for version in self.versions]
        }

    def __str__(self) -> str:
        return f"ProductState(info={self.info}, documents={self.documents}, portals={self.portals}, versions={self.versions})"
