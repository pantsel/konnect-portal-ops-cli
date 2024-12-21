import requests
from typing import Any, Dict, Optional, List, Union

class PortalManagementClient:
  def __init__(self, base_url: str, token: str):
    self.base_url = base_url
    self.headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
    }

  def _handle_response(self, response: requests.Response) -> Any:
    if response.status_code in {200, 201, 204}:
      if response.content:
        return response.json()
      return None
    else:
      self._handle_error(response)

  def _handle_error(self, response: requests.Response):
    try:
      error = response.json()
    except ValueError:
      response.raise_for_status()
    status = error.get('status', response.status_code)
    title = error.get('title', 'Error')
    detail = error.get('detail', response.text)
    raise Exception(f"{status} {title}: {detail}")

  def list_portals(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def create_portal(self, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def get_portal(self, portal_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_portal(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_portal(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> None:
    url = f'{self.base_url}/portals/{portal_id}'
    response = requests.delete(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def list_portal_products(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/products'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def list_portal_product_versions(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def create_portal_product_version(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def get_portal_product_version(self, portal_id: str, product_version_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def replace_portal_product_version(self, portal_id: str, product_version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.put(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_portal_product_version(self, portal_id: str, product_version_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/product-versions/{product_version_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_applications(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/applications'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_application(self, portal_id: str, application_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def delete_application(self, portal_id: str, application_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_application_registrations(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/application-registrations'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def list_registrations_by_application(self, portal_id: str, application_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}/registrations'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_application_registration(self, portal_id: str, application_id: str, registration_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}/registrations/{registration_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_application_registration(self, portal_id: str, application_id: str, registration_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}/registrations/{registration_id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_application_registration(self, portal_id: str, application_id: str, registration_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}/registrations/{registration_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_granted_scopes(self, portal_id: str, application_id: str, registration_id: str) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/applications/{application_id}/registrations/{registration_id}/granted-scopes'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def get_portal_appearance(self, portal_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/appearance'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_portal_appearance(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/appearance'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def get_portal_logo(self, portal_id: str) -> Union[Dict[str, Any], None]:
    url = f'{self.base_url}/portals/{portal_id}/appearance/logo'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def get_portal_catalog_cover(self, portal_id: str) -> Union[Dict[str, Any], None]:
    url = f'{self.base_url}/portals/{portal_id}/appearance/catalog-cover'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def verify_portal_domains(self, portal_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/verify-domain'
    response = requests.post(url, headers=self.headers)
    return self._handle_response(response)

  def get_portal_authentication_settings(self, portal_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/authentication-settings'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_portal_authentication_settings(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/authentication-settings'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_portal_team_group_mappings(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/identity-provider/team-group-mappings'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def update_portal_team_group_mappings(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/identity-provider/team-group-mappings'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def list_portal_teams(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/teams'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def create_portal_team(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/teams'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def get_portal_team(self, portal_id: str, team_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_portal_team(self, portal_id: str, team_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_portal_team(self, portal_id: str, team_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_portal_team_developers(self, portal_id: str, team_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}/developers'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def add_developer_to_portal_team(self, portal_id: str, team_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}/developers'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def remove_developer_from_portal_team(self, portal_id: str, team_id: str, developer_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}/developers/{developer_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_portal_team_roles(self, portal_id: str, team_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}/assigned-roles'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def assign_role_to_portal_team(self, portal_id: str, team_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{team_id}/assigned-roles'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def remove_role_from_portal_team(self, portal_id: str, team_id: str, role_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/teams/{team_id}/assigned-roles/{role_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_portal_developers(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/developers'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def get_developer(self, portal_id: str, developer_id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/developers/{developer_id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_developer(self, portal_id: str, developer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/developers/{developer_id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_developer(self, portal_id: str, developer_id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/developers/{developer_id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)

  def list_portal_developer_teams(self, portal_id: str, developer_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/developers/{developer_id}/teams'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def list_portal_roles(self) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portal-roles'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def retrieve_identity_providers(self, portal_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    url = f'{self.base_url}/portals/{portal_id}/identity-providers'
    response = requests.get(url, headers=self.headers, params=params)
    return self._handle_response(response)

  def create_identity_provider(self, portal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/identity-providers'
    response = requests.post(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def get_identity_provider(self, portal_id: str, id: str) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/identity-providers/{id}'
    response = requests.get(url, headers=self.headers)
    return self._handle_response(response)

  def update_identity_provider(self, portal_id: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f'{self.base_url}/portals/{portal_id}/identity-providers/{id}'
    response = requests.patch(url, headers=self.headers, json=data)
    return self._handle_response(response)

  def delete_identity_provider(self, portal_id: str, id: str) -> None:
    url = f'{self.base_url}/portals/{portal_id}/identity-providers/{id}'
    response = requests.delete(url, headers=self.headers)
    return self._handle_response(response)
  
# Example usage:
# portal_client = PortalManagementClient(base_url="https://us.api.konghq.com/v2", token="your_token_here")
# portal_client.list_portals()
