

from kptl.konnect.models.schema import ApiProductState


def explain_product_state(product_state: ApiProductState) -> None:
    """
    Generates a detailed explanation of the given product state and the operations to be performed.

    Args:
        product_state (ProductState): The state of the product containing information about the product,
                                      its portals, versions, and documents.

    Returns:
        None: This function prints the explanation to the console.

    The explanation includes:
        - Product name and description.
        - Details of each portal associated with the product.
        - Details of each version of the product, including spec file, gateway service ID, and control plane ID.
        - Details of each portal associated with each version, including deprecated status, publish status,
          application registration settings, and authentication strategy IDs.
        - A list of operations to be performed to ensure the product and its versions are up-to-date and properly configured.
    """
    output = [
        f"\nProduct Name: {product_state.info.name}",
        f"Product Description: {product_state.info.description}"
    ]

    for portal in product_state.portals:
        output.append(f"Portal: {portal.portal_name} (ID: {portal.portal_id})")

    for version in product_state.versions:
        output.extend([
            f"Version: {version.name}",
            f"  Spec File: {version.spec}",
            f"  Gateway Service ID: {version.gateway_service.id}",
            f"  Control Plane ID: {version.gateway_service.control_plane_id}"
        ])

        for portal in version.portals:
            output.extend([
                f"  Portal: {portal.portal_name} (ID: {portal.portal_id})",
                f"    Deprecated: {portal.deprecated}",
                f"    Publish Status: {portal.publish_status}",
                f"    Application Registration Enabled: {portal.application_registration_enabled}",
                f"    Auto Approve Registration: {portal.auto_approve_registration}",
                f"    Auth Strategies: {portal.auth_strategies}"
            ])

    output.append("\nOperations to be performed:")
    operation_count = 1
    output.append(f"{operation_count}. Ensure API product '{product_state.info.name}' with description '{product_state.info.description}' exists and is up-to-date.")
    operation_count += 1

    if product_state.documents.sync and product_state.documents.directory:
        output.append(f"{operation_count}. Ensure documents are synced from directory '{product_state.documents.directory}'.")
    else:
        output.append(f"{operation_count}. Document sync will be skipped.")
    operation_count += 1

    for portal in product_state.portals:
        output.append(f"{operation_count}. Ensure API product '{product_state.info.name}' is published on portal '{portal.portal_name}' with ID '{portal.portal_id}'.")
        operation_count += 1

    for version in product_state.versions:
        output.append(f"{operation_count}. Ensure API product version '{version.name}' with spec file '{version.spec}' exists and is up-to-date.")
        operation_count += 1
        if version.gateway_service.id and version.gateway_service.control_plane_id:
            output.append(f"  Ensure it is linked to Gateway Service with ID '{version.gateway_service.id}' and Control Plane ID '{version.gateway_service.control_plane_id}'.")
        for portal in version.portals:
            output.extend([
                f"{operation_count}. Ensure portal product version {version.name} on portal '{portal.portal_name}' is up-to-date with publish status '{portal.publish_status}'.",
                f"  - Deprecated: {portal.deprecated}",
                f"  - Auth Strategies: {portal.auth_strategies}",
                f"  - Application Registration Enabled: {portal.application_registration_enabled}",
                f"  - Auto Approve Registration: {portal.auto_approve_registration}"
            ])
            operation_count += 1

    return "\n".join(output)