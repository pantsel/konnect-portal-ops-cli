"""
Module for Konnect API state Models.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field
from kptl.helpers import utils

@dataclass
class ApiProductVersionAuthStrategy:
    """
    Class representing an auth strategy.
    """
    id: str
    name: str

@dataclass
class ApiProductVersionPortal:
    """
    Class representing a portal.
    """
    portal_id: str = None
    portal_name: str = None
    publish_status: str = "published"  # can be either "published" or "unpublished"
    deprecated: bool = False
    application_registration_enabled: bool = False
    auto_approve_registration: bool = False
    auth_strategies: List[ApiProductVersionAuthStrategy] = field(default_factory=list)

@dataclass
class Documents:
    """
    Class representing documents.
    """
    sync: bool
    directory: str

@dataclass
class GatewayService:
    """
    Class representing a gateway service.
    """
    id: str = None
    control_plane_id: str = None

@dataclass
class ApiProduct:
    """
    Class representing product information.
    """
    name: str
    description: str

@dataclass
class ApiProductVersion:
    """
    Class representing a product version.
    """
    spec: str
    gateway_service: GatewayService
    portals: List[ApiProductVersionPortal]
    name: str = None

@dataclass
class ApiProductPortal:
    """
    Class representing a product portal.
    """
    portal_id: str
    portal_name: str

@dataclass
class ApiProductState:
    """
    Class representing the state of a product in Konnect.
    """
    info: ApiProduct = None
    documents: Documents = None
    portals: List[ApiProductPortal] = field(default_factory=list)
    versions: List[ApiProductVersion] = field(default_factory=list)

    def from_dict(self, data: Dict[str, Any]):
        """
        Initialize ProductState from a dictionary.
        """
        self.info = ApiProduct(
            name=data.get('info', {}).get('name'),
            description=data.get('info', {}).get('description', ""),
        )
        self.documents = Documents(
            sync=data.get('documents', {}).get('sync', False),
            directory=data.get('documents', {}).get('dir', None)
        )
        self.portals = sorted(
            [
            ApiProductPortal(
                portal_id=p.get('portal_id'),
                portal_name=p.get('portal_name')
            ) for p in data.get('portals', [])
            ],
            key=lambda portal: portal.portal_name
        )
        self.versions = [
            ApiProductVersion(
            name=v.get('name'),
            spec=v.get('spec'),
            gateway_service=GatewayService(
                id=v.get('gateway_service', {}).get('id'),
                control_plane_id=v.get('gateway_service', {}).get('control_plane_id')
            ),
            portals=sorted(
                [
                ApiProductVersionPortal(
                    portal_id=p.get('portal_id'),
                    portal_name=p.get('portal_name')
                ) for p in v.get('portals', [])
                ],
                key=lambda portal: portal.portal_name
            )
            ) for v in data.get('versions', [])
        ]

        return self
    
    def encode_versions_spec_content(self):
        """
        Encode the version specs content to base64.
        """
        for version in self.versions:
            _, oas_data_base64 = utils.load_oas_data(version.spec)
            version.spec = oas_data_base64
            
