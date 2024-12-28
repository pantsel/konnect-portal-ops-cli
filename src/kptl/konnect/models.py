"""
Module for Konnect API state Models.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field

@dataclass
class ApplicationRegistration:
    """
    Class representing application registration settings.
    """
    enabled: bool
    auto_approve: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "auto_approve": self.auto_approve
        }

    def __str__(self) -> str:
        return f"ApplicationRegistration(enabled={self.enabled}, auto_approve={self.auto_approve})"

@dataclass
class PortalConfig:
    """
    Class representing portal configuration.
    """
    deprecated: bool = False
    publish_status: str = "published"
    auth_strategy_ids: List[str] = field(default_factory=list)
    application_registration: ApplicationRegistration = field(default_factory=lambda: ApplicationRegistration(enabled=False, auto_approve=False))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deprecated": self.deprecated,
            "publish_status": self.publish_status,
            "auth_strategy_ids": self.auth_strategy_ids,
            "application_registration": self.application_registration.to_dict()
        }

    def __str__(self) -> str:
        return f"PortalConfig(deprecated={self.deprecated}, publish_status={self.publish_status}, auth_strategy_ids={self.auth_strategy_ids}, application_registration={self.application_registration})"

@dataclass
class Portal:
    """
    Class representing a portal.
    """
    id: str = None
    name: str = None
    config: PortalConfig = field(default_factory=PortalConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "config": self.config.to_dict()
        }

    def __str__(self) -> str:
        return f"Portal(name={self.name}, config={self.config})"

@dataclass
class Documents:
    """
    Class representing documents.
    """
    sync: bool
    directory: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sync": self.sync,
            "directory": self.directory
        }

    def __str__(self) -> str:
        return f"Documents(sync={self.sync}, directory={self.directory})"

@dataclass
class GatewayService:
    """
    Class representing a gateway service.
    """
    id: str = None
    control_plane_id: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "control_plane_id": self.control_plane_id
        }

    def __str__(self) -> str:
        return f"GatewayService(id={self.id}, control_plane_id={self.control_plane_id})"

@dataclass
class ProductInfo:
    """
    Class representing product information.
    """
    name: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description
        }

    def __str__(self) -> str:
        return f"ProductInfo(name={self.name}, description={self.description})"

@dataclass
class ProductVersion:
    """
    Class representing a product version.
    """
    spec: str
    gateway_service: GatewayService
    portals: List[Portal]
    name: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec,
            "gateway_service": self.gateway_service.to_dict(),
            "portals": [portal.to_dict() for portal in self.portals]
        }

    def __str__(self) -> str:
        return f"ProductVersion(spec={self.spec}, gateway_service={self.gateway_service}, portals={self.portals})"

@dataclass
class ProductState:
    """
    Class representing the state of a product in Konnect.
    """
    info: ProductInfo = None
    documents: Documents = None
    portals: List[Portal] = field(default_factory=list)
    versions: List[ProductVersion] = field(default_factory=list)

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
                name=v.get('name'),
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
