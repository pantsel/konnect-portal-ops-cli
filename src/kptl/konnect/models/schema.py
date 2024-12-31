"""
Module for Konnect API state Models.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field
from kptl.helpers import utils, api_product_documents


@dataclass
class ApiProductVersionAuthStrategy:
    """
    Class representing an auth strategy.
    """
    id: str = None


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
    auth_strategies: List[ApiProductVersionAuthStrategy] = field(
        default_factory=list)


@dataclass
class ApiProductDocument:
    """
    Class representing a document.
    """
    slug: str
    title: str
    content: str
    status: str


@dataclass
class Documents:
    """
    Class representing documents.
    """
    sync: bool = False
    directory: str = None
    data: List[ApiProductDocument] = field(default_factory=list)

    def set_data(self, data: List[Dict[str, str]]):
        """
        Set the data.
        """

        self.data = sorted(
            [
                ApiProductDocument(
                    slug=api_product_documents.get_slug_tail(d.get('slug')),
                    title=d.get('title'),
                    content=d.get('content'),
                    status=d.get('status')
                ) for d in data
            ],
            key=lambda document: document.slug
        )


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
    name: str = None
    description: str = None


@dataclass
class ApiProductVersion:
    """
    Class representing a product version.
    """
    spec: str
    gateway_service: GatewayService = field(default_factory=GatewayService)
    portals: List[ApiProductVersionPortal] = field(
        default_factory=list[ApiProductVersionPortal])
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
    documents: Documents = field(default_factory=Documents)
    portals: List[ApiProductPortal] = field(default_factory=list)
    versions: List[ApiProductVersion] = field(default_factory=list)

    def from_dict(self, data: Dict[str, Any]):
        """
        Initialize ProductState from a dictionary.
        """
        if data.get('info'):
            self.info = ApiProduct(
                name=data.get('info', {}).get('name'),
                description=data.get('info', {}).get('description', ""),
            )
        self.documents = Documents(
            sync=data.get('documents', {}).get('sync', False),
            directory=data.get('documents', {}).get('dir', None),
            data=data.get('documents', {}).get('data', [])
        )
        self.portals = sorted(
            [
                ApiProductPortal(
                    portal_id=p.get('portal_id'),
                    portal_name=p.get('portal_name')
                ) for p in data.get('portals')
            ],
            key=lambda portal: portal.portal_name
        )
        self.versions = sorted(
            [
                ApiProductVersion(
                    name=self.get_version_name(v),
                    spec=v.get('spec'),
                    gateway_service=GatewayService(
                        id=v.get('gateway_service', {}).get('id'),
                        control_plane_id=v.get(
                            'gateway_service', {}).get('control_plane_id')
                    ),
                    portals=sorted(
                        [ApiProductVersionPortal(
                            portal_id=p.get('portal_id'),
                            portal_name=p.get('portal_name'),
                            deprecated=p.get('deprecated', False),
                            publish_status=p.get(
                                'publish_status', "published"),
                            application_registration_enabled=p.get(
                                'application_registration_enabled', False),
                            auto_approve_registration=p.get(
                                'auto_approve_registration', False),
                            auth_strategies=[
                                ApiProductVersionAuthStrategy(
                                    id=a.get('id')
                                ) for a in p.get('auth_strategies', [])
                            ]
                        ) for p in v.get('portals', [])
                        ],
                        key=lambda portal: portal.portal_name
                    )
                ) for v in data.get('versions', [])
            ],
            key=lambda version: version.name
        )

        return self

    def make_api_docs(self, documents: Documents):
        """
        Make the API docs.
        """
        if documents.sync:
            self.api_docs = api_product_documents.parse_directory(
                documents.directory)

    def get_version_name(self, version: ApiProductVersion):
        """
        Get the version name.
        """
        if version.get('name'):
            return version.get('name')

        oas_data, _ = utils.load_oas_data(version.get('spec'))
        return oas_data.get('info', {}).get('version')

    def encode_versions_spec_content(self):
        """
        Encode the version specs content to base64.
        """
        for version in self.versions:
            _, oas_data_base64 = utils.load_oas_data(version.spec)
            version.spec = oas_data_base64
